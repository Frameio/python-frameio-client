from ..client import FrameioClient


class Service(object):
    def __init__(self, client: FrameioClient):
        self.client = client
        self.concurrency = 10

        # Auto-configure SDK
        self.autoconfigure()

    def autoconfigure(self):
        return

    def save_config(self):
        pass

    def load_config(self):
        pass
