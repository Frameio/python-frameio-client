import re
import sys
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from .lib import ClientVersion, PaginatedResponse

class FrameioClient(object):
  def __init__(self, token, host='https://api.frame.io'):
    self.token = token
    self.host = host
    self.retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429],
        method_whitelist=["POST", "OPTIONS", "GET"]
    )
    self.client_version = ClientVersion.version()

  def _api_call(self, method, endpoint, payload={}, limit=None):
    url = '{}/v2{}'.format(self.host, endpoint)

    headers = {
      'Authorization': 'Bearer {}'.format(self.token),
      'x-frameio-client': 'python/{}'.format(self.client_version)
    }

    adapter = HTTPAdapter(max_retries=self.retry_strategy)

    http = requests.Session()
    http.mount("https://", adapter)

    r = http.request(
      method,
      url,
      json=payload,
      headers=headers,
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
