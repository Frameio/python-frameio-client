import os
import math
import base64
import hashlib
import requests
import traceback
import threading
import concurrent.futures

thread_local = threading.local()

class FrameioUploader(object):
  def __init__(self, asset, file):
    self.asset = asset
    self.file = file
    self.chunk_size = None

  def _calculate_chunks(self, total_size, chunk_count):
    self.chunk_size = int(math.ceil(total_size / chunk_count))

    chunk_offsets = list()

    for index in range(chunk_count):
      offset_amount = index * self.chunk_size
      chunk_offsets.append(offset_amount)

    return chunk_offsets

  def _get_content_md5(self, data):
      digest = hashlib.md5(data[:]).digest()
      # print(base64.b64encode(digest).decode('utf-8'))
      return base64.b64encode(digest).decode('utf-8')

  def _get_session(self):
    if not hasattr(thread_local, "session"):
        thread_local.session = requests.Session()
    return thread_local.session

  def _smart_read_chunk(self, chunk_offset, is_final_chunk):
    with open(os.path.realpath(self.file.name), "rb") as file:
      file.seek(chunk_offset, 0)
      if is_final_chunk: # If it's the final chunk, we want to just read until the end of the file
        data = file.read()
      else: # If it's not the final chunk, we want to ONLY read the specified chunk
        data = file.read(self.chunk_size)
      # self._get_content_md5(data)
      return data

  def _upload_chunk(self, task):
    url = task[0]
    chunk_offset = task[1]
    chunk_id = task[2]
    chunks_total = len(self.asset['upload_urls'])

    is_final_chunk = False

    if chunk_id+1 == chunks_total:
      is_final_chunk = True
    
    session = self._get_session()

    chunk_data = self._smart_read_chunk(chunk_offset, is_final_chunk)
    chunk_md5 = self._get_content_md5(chunk_data)

    print(chunk_md5)

    try:
      r = session.put(url, data=chunk_data, headers={
        'content-type': self.asset['filetype'],
        'x-amz-acl': 'private',
        'Content-MD5': chunk_md5
      })
      # 'Content-Length': str(len(chunk_data))
      print("Completed chunk, status: {}".format(r.content))
      print("Completed chunk, status: {}".format(r.status_code))
    except Exception as e:
      print(e)

    r.raise_for_status()

  def upload(self):
    total_size = self.asset['filesize']
    upload_urls = self.asset['upload_urls']

    chunk_offsets = self._calculate_chunks(total_size, chunk_count=len(upload_urls))

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
      for i in range(len(upload_urls)):
        url = upload_urls[i]
        chunk_offset = chunk_offsets[i]
        
        task = (url, chunk_offset, i)
        executor.submit(self._upload_chunk, task)
