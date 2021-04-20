from .lib import (
  Utils,
  APIClient,
  AWSClient,
  Telemetry,
  ClientVersion,
  ClientVersion,
  FrameioDownloader
)

class FrameioClient(APIClient, object):
  def __init__(self, token, host):
    super().__init__(token, host)

  @property
  def me(self):
    return self.users.get_me()

  @property
  def telemetry(self):
    return Telemetry(self)

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
