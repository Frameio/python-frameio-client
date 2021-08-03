"""
client.py
====================================
The core module of the frameioclient
"""
from .lib import (
  APIClient,
  Telemetry,
  ClientVersion,
  ClientVersion,
  FrameioDownloader,
  PresentationException
)

class FrameioClient(APIClient, object):
  def __init__(self, token, host='https://api.frame.io', threads=5, progress=False):
    super().__init__(token, host, threads, progress)

  @property
  def me(self):
    return self.users.get_me()

  @property
  def telemetry(self):
    return Telemetry(self)

<<<<<<<

=======
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
      # If we've already got a ? in the endpoint, then it has to be an &
      if '?' in endpoint:
        endpoint = '{}&page={}'.format(endpoint, page)
      else:
        endpoint = '{}?page={}'.format(endpoint, page)
      return self._api_call(method, endpoint)

    if method == 'post':
      payload['page'] = page
      return self._api_call(method, endpoint, payload=payload)


class FrameioClient(FrameioConnection):
  """[summary]

  Args:
      FrameioConnection ([type]): [description]

  Returns:
      [type]: [description]
  """  
>>>>>>>
  @property
  def _auth(self):
    return self.token

  @property
  def _version(self):
    return ClientVersion.version()

  @property
  def _download(self):
    return FrameioDownloader(self)

  @property
  def users(self):
    from .services import User
    return User(self)

  @property
  def assets(self):
    from .services import Asset
    return Asset(self)
  
  @property
  def comments(self):
    from .services import Comment
    return Comment(self)

  @property
  def logs(self):
    from .services import AuditLogs
    return AuditLogs(self)

  @property
  def review_links(self):
    from .services import ReviewLink
    return ReviewLink(self)

  @property
  def presentation_links(self):
    from .services import PresentationLink
    return PresentationLink(self)

  @property
  def projects(self):
    from .services import Project
    return Project(self)

  @property
  def teams(self):
    from .services import Team
    return Team(self)

  @property
  def helpers(self):
    from .services import FrameioHelpers
    return FrameioHelpers(self)
