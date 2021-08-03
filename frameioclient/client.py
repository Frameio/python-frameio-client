"""
client.py
====================================
The core module of the frameioclient
"""
from .lib import APIClient, Telemetry, ClientVersion, ClientVersion, FrameioDownloader
from services import *


class FrameioClient(APIClient):
    def __init__(self, token, host="https://api.frame.io", threads=5, progress=False):
        super().__init__(token, host, threads, progress)

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
        return User(self)

    @property
    def assets(self):
        return Asset(self)

    @property
    def comments(self):
        return Comment(self)

    @property
    def logs(self):
        return AuditLogs(self)

    @property
    def review_links(self):
        return ReviewLink(self)

    @property
    def presentation_links(self):
        return PresentationLink(self)

    @property
    def projects(self):
        return Project(self)

    @property
    def teams(self):
        return Team(self)

    @property
    def helpers(self):
        return FrameioHelpers(self)
