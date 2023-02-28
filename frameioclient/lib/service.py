from ..client import FrameioClient
from ..lib.bandwidth import NetworkBandwidth


class Service(object):
    def __init__(self, client: FrameioClient):
        self.client = client
        self.concurrency = 10
        self.bandwidth = NetworkBandwidth()

        # Auto-configure afterwards
        self.autoconfigure()

    def autoconfigure(self):
        # self.bandwidth = SpeedTest.speedtest()
        return

    def save_config(self):
        pass

    def load_config(self):
        pass
