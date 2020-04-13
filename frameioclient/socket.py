import websocket
import uuid
import json


# Python 2/3 support
try:
    import thread
except ImportError:
    import _thread as thread


class FIOWebsocket(object):
    def __init__(self, token, user_id, project_id, asset, con_type, event_type):
        self.ws_event = 0
        self.token = token
        self.user_id = user_id
        self.project_id = project_id
        self.asset = asset
        self.con_type = con_type
        self.event_type = event_type
        self.socket_uri = "wss://sockets.frame.io/socket/websocket"

        self.room_id = f"{con_type}:{project_id}"
        self.connection_uuid = str(uuid.uuid1())

        self.ws = None
        self.initalize_connection()

        self.join_upload_channel()

    @staticmethod
    def on_message(self, ws, message):
        print(message)

    @staticmethod
    def on_error(ws, error):
        print(error)

    @staticmethod
    def on_open(ws):
        def run(*args):
            ws.send("Hello World")
            print("thread terminating...")
        thread.start_new_thread(run, ())

    def initalize_connection(self):
        websocket.enableTrace(True)
        ws = websocket.WebSocketApp(self.socket_uri,
            on_message = self.on_message,
            on_error = self.on_error,
            # on_close = self.on_close
        )

        ws.on_open = self.on_open(ws)
        ws.run_forever()

        self.connection = ws

    def join_upload_channel(self):
        join_command = \
            [
                "3",
                "3",
                self.room_id,
                "phx_join",
                {
                    "user_token": self.token,
                    "user_id": self.user_id
                }
            ]
        
        self.emit_event(json.dumps(join_command))

    async def emit_event(self, message):
        self.ws_event += 1 # auto-increment
        self.ws.send()

    def update_progress(self, bytes_sent):
        progress = f"""{
            "connection_id": self.connection_uuid,
            "type": self.con_type,
            "data": {
                "asset_id": self.asset['id'],
                "sent_bytes": bytes_sent,
                "total_bytes": self.asset['filesize'],
                "version": "1.0.0"
            }
        }"""

        message = f"""["", {self.ws_event}, {self.room_id}, "UploadProgressClient", {json.dumps(progress)}]"""

        self.emit_event(message)
