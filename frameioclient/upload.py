from multiprocessing import Process
import requests
import math

class FrameioUploader(object):
  def __init__(self, asset, file):
    self.asset = asset
    self.file = file

  def _read_chunk(self, file, size):
    while True:
      data = file.read(size)
      if not data:
        break
      yield data

  def _upload_chunk(self, url, chunk):
    requests.put(url, data=chunk, headers={
      'content-type': self.asset['filetype'],
      'x-amz-acl': 'private'
    })

  def upload(self):
    procs = []

    total_size = self.asset['filesize']
    upload_urls = self.asset['upload_urls']
    size = int(math.ceil(total_size / len(upload_urls)))

    for i, chunk in enumerate(self._read_chunk(self.file, size)):
      proc = Process(target=self._upload_chunk, args=(upload_urls[i], chunk,))
      procs.append(proc)
      proc.start()

    for proc in procs:
      proc.join()
