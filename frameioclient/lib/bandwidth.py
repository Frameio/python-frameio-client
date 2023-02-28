import speedtest


class NetworkBandwidth:
    # Test the network bandwidth any time we have a new IP address
    # Persist this information to a config.json file

    def __init__(self):
        self.results = dict()

    def load_stats(self):
        # Force an update on these stats before starting download/upload
        pass

    def persist_stats(self):
        pass

    def run(self):
        self.results = self.speed_test()

    @staticmethod
    def speedtest():
        """
        Run a speedtest using Speedtest.net in order to get a 'control' for \
            bandwidth optimization.

        Example::
            NetworkBandwidth.speedtest()
        """

        st = speedtest.Speedtest()
        download_speed = round(st.download(threads=10) * (1.192 * 10 ** -7), 2)
        upload_speed = round(st.upload(threads=10) * (1.192 * 10 ** -7), 2)
        servernames = []
        server_names = st.get_servers(servernames)
        ping = st.results.ping

        return {
            "ping": ping,
            "download_speed": download_speed,
            "upload_speed": upload_speed,
        }

    def __repr__(self):
        self.results


class DiskBandwidth:
    # Test the disk speed and write to a config.json file for re-use
    # Worth re-checking the disk every time a new one is detected (base route)

    def __init__(self, volume):
        self.volume = volume
        self.results = dict()

    def __repr__(self):
        self.results
