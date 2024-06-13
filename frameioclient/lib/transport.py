import concurrent.futures
import threading
import time
from typing import Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from token_bucket import Limiter, MemoryStorage
from urllib3.util.retry import Retry

from .constants import default_thread_count, retryable_statuses
from .exceptions import PresentationException
from .utils import PaginatedResponse
from .version import ClientVersion


class HTTPMethods:
    GET = "get"
    POST = "post"
    PUT = "put"
    DELETE = "delete"
    PATCH = "patch"
    HEAD = "head"


class HTTPClient(object):
    """HTTP Client base that automatically handles the following:
    - Shared thread/session object
    - Client version headers
    - Automated retries

    """

    def __init__(self, threads: Optional[int] = default_thread_count):
        """
        :param threads: Number of threads to use concurrently.
        """

        # Setup number of threads to use
        self.threads = threads

        # Initialize empty thread object
        self.thread_local = None
        self.client_version = ClientVersion.version()
        self.shared_headers = {"x-frameio-client": f"python/{self.client_version}"}

        # Configure retry strategy (very broad right now)
        self.retry_strategy = Retry(
            total=100,
            backoff_factor=2,
            status_forcelist=retryable_statuses,
            method_whitelist=["GET", "POST", "PUT", "GET", "DELETE"],
        )

        # Create real thread
        self._initialize_thread()

    def _initialize_thread(self):
        self.thread_local = threading.local()

    def _get_session(self):
        # Create session only if needed
        if not hasattr(self.thread_local, "session"):
            http = requests.Session()
            adapter = HTTPAdapter(max_retries=self.retry_strategy)
            adapter.add_headers(self.shared_headers)  # add version header
            http.mount("https://", adapter)
            http.mount("http://", adapter)
            self.thread_local.session = http

        # Return session
        return self.thread_local.session


class APIClient(HTTPClient, object):
    """Frame.io API Client that handles automatic pagination, and lots of other nice things.

    Args:
        HTTPClient (class): HTTP Client base class
        token (str): Frame.io developer token, JWT, or OAuth access token.
        threads (int): Number of threads to concurrently use for uploads/downloads.
        progress (bool): If True, show status bars in console.
    """

    def __init__(self, token: str, host: str, threads: int, progress: bool):
        super().__init__(threads)
        self.host = host
        self.token = token
        self.threads = threads
        self.progress = progress
        self._initialize_thread()
        self.session = self._get_session()
        self.auth_header = {"Authorization": f"Bearer {self.token}"}

    def _format_api_call(self, endpoint: str):
        return f"{self.host}/v2{endpoint}"

    def _api_call(
        self, method, endpoint: str, payload: Dict = {}, limit: Optional[int] = None
    ):
        headers = {**self.shared_headers, **self.auth_header}

        r = self.session.request(
            method, self._format_api_call(endpoint), headers=headers, json=payload
        )

        if r.ok:
            if r.headers.get("page-number"):
                if int(r.headers.get("total-pages")) > 1:
                    return PaginatedResponse(
                        results=r.json(),
                        limit=limit,
                        page_size=r.headers["per-page"],
                        total_pages=r.headers["total-pages"],
                        total=r.headers["total"],
                        endpoint=endpoint,
                        method=method,
                        payload=payload,
                        client=self,
                    )

            if isinstance(r.json(), list):
                return r.json()[:limit]

            return r.json()

        if r.status_code == 422 and "presentation" in endpoint:
            raise PresentationException
        
        if r.status_code == 500 and 'audit' in endpoint:
            print(f"Hit a 500 on page: {r.headers.get('page-number')}, url: {r.url}")
            return []

        return r.raise_for_status()

    def get_specific_page(
        self, method: HTTPMethods, endpoint: str, payload: Dict, page: int
    ):
        """
        Gets a specific page for that endpoint, used by Pagination Class

        :Args:
            method (string): 'get', 'post'
            endpoint (string): endpoint ('/accounts/<ACCOUNT_ID>/teams')
            payload (dict): Request payload
            page (int): What page to get
        """
        if method == HTTPMethods.GET:
            endpoint = f"{endpoint}?page={page}"
            return self._api_call(method, endpoint)

        if method == HTTPMethods.POST:
            payload["page"] = page
        return self._api_call(method, endpoint, payload=payload)

    def exec_stream(callable, iterable, sync=lambda _: False, capacity=10, rate=10):
        """
        Executes a stream according to a defined rate limit.
        """
        limiter = Limiter(capacity, rate, MemoryStorage())
        futures = set()

        def execute(operation):
            return (operation, callable(operation))

        with concurrent.futures.ThreadPoolExecutor(max_workers=capacity) as executor:
            while True:
                if not limiter.consume("stream", 1):
                    start = int(time.time())
                    done, pending = concurrent.futures.wait(
                        futures, return_when=concurrent.futures.FIRST_COMPLETED
                    )
                    for future in done:
                        yield future.result()

                    futures = pending
                    if (int(time.time()) - start) < 1:
                        time.sleep(
                            1.0 / rate
                        )  # guarantee there's capacity in the rate limit at end of the loop

                operation = next(iterable, None)

                if not operation:
                    done, _ = concurrent.futures.wait(futures)
                    for future in done:
                        yield future.result()
                    break

                if sync(operation):
                    yield execute(operation)
                    continue

                futures.add(executor.submit(execute, operation))
