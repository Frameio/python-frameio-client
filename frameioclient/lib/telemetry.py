import os
import analytics

from pprint import pprint

from .logger import SDKLogger
from .version import ClientVersion

segment_id = os.getenv("SEGMENT_WRITE_KEY", "")  # Production
analytics.write_key = segment_id


class Telemetry(object):
    def __init__(self, user_id):
        self.user_id = user_id
        self.identity = None
        self.context = None
        self.integrations = {"all": False, "Amplitude": True}
        self.logger = SDKLogger("frameioclient.telemetry")

        self.build_context()

    def build_context(self):
        return {
            "app": {
                "name": "python-frameoclient",
                "version": ClientVersion.version(),
            }
        }

    def push(self, event_name, properties):
        self.logger.info((f"Pushing '{event_name}' event to segment", properties))

        try:
            status = analytics.track(
                self.user_id,
                event_name,
                properties=properties,
                context=self.build_context(),
                integrations=self.integrations,
            )
        except Exception as e:
            self.logger.info(e, event_name, properties)


class Event(Telemetry, object):
    def __init__(self, user_id, event_name, properties):
        super().__init__(user_id)
        self.push(event_name, properties)


class ComparisonTest(Event, object):
    def __init__(self, transfer_stats, request_logs=[]):
        super().__init__()
        # self.event_name = event_name
        self.transfer_stats = None
        # self.requests_logs = requests_logs

    @staticmethod
    def _parse_requests_data(req_object):
        return {
            "speed": 0,
            "time_to_first_byte": 0,
            "response_time": 0,
            "byte_transferred": 0,
            "http_status": 200,
            "request_type": "GET",
        }

    def _build_transfer_stats_payload(self, event_data):
        # Turn the request payload into a useful shape
        properties = {
            "download_speed": 0,
            "control": {"upload_bytes_sec": 0, "download_bits_sec": 0, "ping_ms": 0},
            "hash_speed": 0,
        }

        return properties

    def track_transfer(self):
        for chunk in self.requests_logs:
            pprint(chunk)
            # self.logger.info(pprint(chunk))

        # Collect info to build message
        # Build payload for transfer tracking
        # stats_payload = self._build_transfer_stats_payload()

        # Push the payload for tracking the transfer
        # self.push('python_transfer_stats', stats_payload)
