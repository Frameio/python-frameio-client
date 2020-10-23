import re
import sys
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from .lib import ClientVersion, PaginatedResponse, Utils, ClientVersion


class FrameioConnection(object):
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
    self.headers = Utils.format_headers(self.token, self.client_version)

    self.adapter = HTTPAdapter(max_retries=self.retry_strategy)
    self.session = requests.Session()
    self.session.mount("https://", self.adapter)

  def _api_call(self, method, endpoint, payload={}, limit=None):
    url = '{}/v2{}'.format(self.host, endpoint)

    r = self.session.request(
      method,
      url,
      json=payload,
      headers=self.headers,
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


class FrameioClient(FrameioConnection):
  @property
  def _auth(self):
    return self.token

  @property
  def _version(self):
    return ClientVersion.version()

  @property
  def users(self):
    from .service import User
    return User(self)

  @property
  def assets(self):
    from .service import Asset
    return Asset(self)
  
  @property
  def comments(self):
    from .service import Comment
    return Comment(self)

  @property
  def logs(self):
    from .service import AuditLogs
    return AuditLogs(self)

  @property
  def review_links(self):
    from .service import ReviewLink
    return ReviewLink(self)

  @property
  def presentation_links(self):
    from .service import PresentationLink
    return PresentationLink(self)

  @property
  def projects(self):
    from .service import Project
    return Project(self)

  @property
  def teams(self):
    from .service import Team
    return Team(self)
