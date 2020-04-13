import requests
import math
import concurrent.futures
import threading
import websockets
import json
from socket_service import FIOWebsocket

thread_local = threading.local()

class FrameioUploader(object):
  def __init__(self, token, user_id, project, asset, file):
    self.token = token
    self.user = user_id
    self.project = asset['project_id']
    self.asset = asset

    self.socket = FIOWebsocket(token, user_id, asset['project_id'], con_type="project", event_type="UploadProgressClient")
    
    self.file = file
    self.upload_urls = asset['upload_urls']
    self.bytes_total = asset['filesize']
    self.bytes_sent = 0

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
    
    self.socket.update_progress(self.bytes_sent) # Update socket event when chunk completed

  def upload(self):
    upload_urls = self.asset['upload_urls']
    size = int(math.ceil(self.bytes_total / len(upload_urls)))

    tasks = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
      for i, chunk in enumerate(self._read_chunk(self.file, size)):
        task = (upload_urls[i], chunk)
        tasks.append(task)

      executor.map(self._upload_chunk, tasks)
