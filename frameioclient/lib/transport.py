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

    def _get_session(self):
        if not hasattr(self.thread_local, "session"):
            http = requests.Session()
            adapter = HTTPAdapter(max_retries=self.retry_strategy)
            adapter.add_headers(self.shared_headers) # add version header
            http.mount("https", adapter)
            self.thread_local.session = http

        return self.thread_local.session


class APIClient(HTTPClient, object):
    def __init__(self, token, host):
        super().__init__()
        self.host = host
        self.token = token
        self._initialize_thread()
        self.session = self._get_session()
        self.auth_header = {
            'Authorization': 'Bearer {}'.format(self.token),
        }
    
    def _format_api_call(self, endpoint):
        return '{}/v2{}'.format(self.host, endpoint)

    def _api_call(self, method, endpoint, payload={}, limit=None):
        r = self.session.request(
            method,
            url=self._format_api_call(endpoint),
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
    def __init__(self, concurrency=None, progress=True):
        super().__init__() # Initialize via inheritance
        self.progress = progress
        if concurrency is not None:
            self.concurrency = concurrency
        else:
            self.concurrency = self.optimize_concurrency()

    def optimize_concurrency(self):
        """
        This method looks as the net_stats and disk_stats that we've run on \
            the current environment in order to suggest the best optimized \
            number of concurrent TCP connections.

        Example::
            AWSClient.optimize_concurrency()
        """

        net_stats = NetworkBandwidth
        disk_stats = DiskBandwidth

        # Algorithm ensues
        #
        #

        return 5
    
    @staticmethod
    def get_byte_range(url, start_byte=0, end_byte=2048):
        """
        Get a specific byte range from a given URL. This is **not** optimized \
            for heavily-threaded operations currently because it doesn't use a shared \
            HTTP session object / thread

        :Args:
            url (string): The URL you want to fetch a byte-range from
            start_byte (int): The first byte you want to request
            end_byte (int): The last byte you want to extract

        Example::
            AWSClient.get_byte_range(asset, "~./Downloads")
        """

        headers = {"Range": "bytes=%d-%d" % (start_byte, end_byte)}
        br = requests.get(url, headers=headers).content
        return br

    @staticmethod
    def check_cdn(url):
        # TODO improve this algo
        if 'assets.frame.io' in url:
            return 'Cloudfront'
        elif 's3' in url:
            return 'S3'
        else:
            return None


class TransferJob(AWSClient):
    # These will be used to track the job and then push telemetry
    def __init__(self, job_info):
        self.job_info = self.check_cdn(job_info)
        self.cdn = 'S3' # or 'CF' - use check_cdn to confirm
        self.progress_manager = None

class DownloadJob(TransferJob):
    def __init__(self):
        self.asset_type = 'review_link' # we should use a dataclass here
        # Need to create a re-usable job schema
        # Think URL -> output_path
        pass

class UploadJob(TransferJob):
    def __init__(self, destination):
        self.destination = destination
        # Need to create a re-usable job schema
        # Think local_file path and remote Frame.io destination
        pass
