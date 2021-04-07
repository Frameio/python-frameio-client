import os
import logging
import enlighten
import requests
import threading
import concurrent.futures

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from .version import ClientVersion
from .utils import Utils, PaginatedResponse
from .bandwidth import NetworkBandwidth, DiskBandwidth


class HTTPClient(object):
    def __init__(self):
        # Initialize empty thread object
        self.thread_local = None
        self.client_version = ClientVersion.version()
        self.shared_headers = {
            'x-frameio-client': 'python/{}'.format(self.client_version)
        }
        # Configure retry strategy (very broad right now)
        self.retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[400, 429, 500, 503],
            method_whitelist=["GET", "POST", "PUT", "GET", "DELETE"]
        )
        # Create real thread
        self._initialize_thread()

    def _initialize_thread(self):
        self.thread_local = threading.local()

    def _get_session(self, auth=True):
        if not hasattr(self.thread_local, "session"):
            http = requests.Session()
            adapter = HTTPAdapter(max_retries=self.retry_strategy)
            adapter.add_headers(self.shared_headers) # add version header
            http.mount("https", adapter)
            self.thread_local.session = http

        return self.thread_local.session


class APIClient(HTTPClient, object):
    def __init__(self, token, host='https://api.frame.io'):
        super().__init__()
        self.host = host
        self.token = token
        self._initialize_thread()
        self.session = self._get_session(auth=token)
        self.auth_header = {
            'Authorization': 'Bearer {}'.format(self.token),
        }


    def _api_call(self, method, endpoint, payload={}, limit=None):
        url = '{}/v2{}'.format(self.host, endpoint)

        headers = {**self.shared_headers, **self.auth_header}

        r = self.session.request(
            method,
            url,
            headers=self.auth_header,
            json=payload
        )

        if r.ok:
            if r.headers.get('page-number'):
                if int(r.headers.get('total-pages')) > 1:
                    return PaginatedResponse(
                        results=r.json(),
                        limit=limit,
                        page_size=r.headers['per-page'],
                        total_pages=r.headers['total-pages'],
                        total=r.headers['total'],
                        endpoint=endpoint,
                        method=method,
                        payload=payload,
                        client=self
                    )
            if isinstance(r.json(), list):
                return r.json()[:limit]

            return r.json()

        if r.status_code == 422 and "presentation" in endpoint:
            raise PresentationException

        print(r.headers)

        return r.raise_for_status()

    def get_specific_page(self, method, endpoint, payload, page):
        """
        Gets a specific page for that endpoint, used by Pagination Class

        :Args:
        method (string): 'get', 'post'
        endpoint (string): endpoint ('/accounts/<ACCOUNT_ID>/teams')
        payload (dict): Request payload
        page (int): What page to get
        """
        if method == 'get':
            endpoint = '{}?page={}'.format(endpoint, page)
        return self._api_call(method, endpoint)

        if method == 'post':
            payload['page'] = page
        return self._api_call(method, endpoint, payload=payload)


class AWSClient(HTTPClient, object):
    def __init__(self, concurrency=5):
        super().__init__()
        pass
    
    @staticmethod
    def get_byte_range(url, start_byte=0, end_byte=2048):
        headers = {"Range": "bytes=%d-%d" % (start_byte, end_byte)}
        br = requests.get(url, headers=headers).content
        return br

class TransferJob(AWSClient):
    # These will be used to track the job and then push telemetry
    def __init__(self, job_info):
        self.job_info = job_info
        self.cdn = 'S3' # or 'CF'

class DownloadJob(TransferJob):
    def __init__(self):
        # Need to create a re-usable job schema
        # Think like URL -> output_path
        pass

class UploadJob(TransferJob):
    def __init__(self, destination):
        self.destination = destination
        # Need to create a re-usable job schema
        # Think local_file path and remote Frame.io destination
        pass