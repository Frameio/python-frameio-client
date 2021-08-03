from ..client import FrameioClient

class Service(object):
    def __init__(self, client: FrameioClient):
        self.client = client
