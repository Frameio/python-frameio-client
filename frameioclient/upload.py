import requests
import math
import concurrent.futures
import threading
import websockets
import asyncio
import json
import uuid
import json

thread_local = threading.local()

class FrameioUploader(object):
  def __init__(self, asset, file, token):
    self.asset = asset
    self.file = file
    self.token = token
    self.bytes_sent = 0 
    self.ws_event = 0
    self.connection_uuid = str(uuid.uuid1())
    self.project = "1ff2708c-acf0-42c1-8b06-d477b7819189"

    # Start socket update event loop
    asyncio.get_event_loop().run_until_complete(self.update_socket())

  def _read_chunk(self, file, size):
    while True:
      data = file.read(size)
      if not data:
        break
      yield data

  def _get_session(self):
    if not hasattr(thread_local, "session"):
        thread_local.session = requests.Session()
    return thread_local.session

  def _upload_chunk(self, task):
    url = task[0]
    chunk = task[1]
    session = self._get_session()

    session.put(url, data=chunk, headers={
      'content-type': self.asset['filetype'],
      'x-amz-acl': 'private'
    })

    self.bytes_sent += len(chunk) # Increment bytes_sent after each chunk
    self.ws_event += 1 # auto-increment

    self.update_socket() # Update socket event when chunk completed

  async def update_socket(self):
    uri = "wss://sockets.frame.io/socket/websocket"

    room_id = f"projects:{self.project}"
    event_dict = {
      "connection_id": self.connection_uuid,
      "type": "UploadProgressClient",
      "data": {
        "asset_id": self.asset['id'],
        "sent_bytes": self.bytes_sent,
        "total_bytes": self.asset['filesize'],
        "version": "1.0.0"
      }
    }

    print(json.dumps(event_dict))

    message = f"""["3", {self.ws_event}, {room_id}, "UploadProgressClient", {json.dumps(event_dict)}]"""

    async with websockets.connect(uri, ssl=True) as websocket:
        print("connected to socket")
        await websocket.send(message)

  def upload(self):
    total_size = self.asset['filesize']
    upload_urls = self.asset['upload_urls']
    size = int(math.ceil(total_size / len(upload_urls)))

    tasks = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
      for i, chunk in enumerate(self._read_chunk(self.file, size)):
        task = (upload_urls[i], chunk)
        tasks.append(task)

      executor.map(self._upload_chunk, tasks)
