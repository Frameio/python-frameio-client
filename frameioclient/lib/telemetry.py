import logging
import analytics

logger = logging.getLogger('telemetry')
segment_id = 'iuwUzRjCbX2iKgf5qvHhM4FfMJOZN4tQ'

analytics.write_key = segment_id


class Telemetry(object):
    def __init__(self, user_id):
        self.speedtest = None
        self.user = None

    def _run_speedtest(self):
        pass

    def extract_properties(requests_data):
        # Turn the request payload into a useful shape

        return message

    def send_to_segment(self, event_name, message):

        analytics.track(
            '[user_id]', '[event_name]', {
                'properties': {
                    'download_speed': 0,
                    'control': {
                        'upload_bytes_sec' 0,
                        'download_bits_sec': 0,
                        'ping_ms': 0
                    }
                }
            }
        )



def send_to_segment(''):
    pass