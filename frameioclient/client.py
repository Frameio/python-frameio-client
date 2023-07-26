"""
client.py
====================================
The core module of the frameioclient
"""

from .config import Config
from .lib import APIClient, ClientVersion, FrameioDownloader

from .resources import *


class FrameioClient(APIClient):
    def __init__(
        self,
        token: str,
        host: str = Config.api_host,
        threads: int = Config.default_concurrency,
        progress=False,
    ):
        super().__init__(token, host, threads, progress)

    @property
    def me(self):
        return self.users.get_me()

    def _auth(self):
        return self.token

    def _version(self):
        return ClientVersion.version()

    def _download(self):
        return FrameioDownloader(self)

    @property
    def users(self):
        from .resources import User

        return User(self)

    @property
    def assets(self):
        from .resources import Asset

        return Asset(self)

    @property
    def comments(self):
        from .resources import Comment

        return Comment(self)

    @property
    def logs(self):
        from .resources import AuditLogs

        return AuditLogs(self)

    @property
    def review_links(self):
        from .resources import ReviewLink

        return ReviewLink(self)

    @property
    def presentation_links(self):
        from .resources import PresentationLink

        return PresentationLink(self)

    @property
    def projects(self):
        from .resources import Project

        return Project(self)

    @property
    def teams(self):
        from .resources import Team

        return Team(self)

    @property
    def helpers(self):
        from .resources import FrameioHelpers

        return FrameioHelpers(self)
