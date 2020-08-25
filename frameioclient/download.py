import io
import os
import math
import time
import requests
import threading
import concurrent.futures

from .utils import format_bytes
from .exceptions import DownloadException

thread_local = threading.local()

class FrameioDownloader(object):
  def __init__(self, asset, download_folder, prefix=None):
    self.asset = asset
    self.download_folder = download_folder
    self.resolution_map = dict()
    self.destination = None
    self.watermarked = False
    self.chunk_manager = dict()
    self.chunk_size = 52428800
    self.chunks = math.floor(asset['filesize'] / self.chunk_size)
    self.prefix = prefix
    self.filename = asset['name']

  def _get_session(self):
    if not hasattr(thread_local, "session"):
        thread_local.session = requests.Session()
    return thread_local.session

  def get_download_key(self):
    try:
      url = self.asset['original']
    except KeyError as e:
      if self.asset['is_session_watermarked'] == True:
        resolution_list = list()
        try:
          for resolution_key, download_url in sorted(self.asset['downloads'].items()):
            resolution = resolution_key.split("_")[1] # Grab the item at index 1 (resolution)
            try:
              resolution = int(resolution)
            except ValueError:
              continue

            if download_url is not None:
              resolution_list.append(download_url)

          # Grab the highest resolution (first item) now
          url = resolution_list[0]
        except KeyError:
          raise DownloadException
      else:
        raise DownloadException

    return url

  def get_path(self):
    if self.prefix != None:
      self.filename = self.prefix + self.filename

    if self.destination == None:
      final_destination = os.path.join(self.download_folder, self.filename)
      self.destination = final_destination
      
    return self.destination

  def download_handler(self, acceleration_override=False):
    if os.path.isfile(self.get_path()):
      return self.destination, 0
    else:
      url = self.get_download_key()

      if self.watermarked == True:
        return self.download(url)
      else:
        if acceleration_override == True:
          return self.accelerate_download(url)
        else:
          return self.download(url)

  def download(self, url):
    start_time = time.time()
    print("Beginning download -- {} -- {}".format(self.asset['name'], format_bytes(self.asset['filesize'], type="size")))

    # Downloading
    r = requests.get(url)
    open(self.destination, 'wb').write(r.content)

    download_time = time.time() - start_time
    download_speed = format_bytes(math.ceil(self.asset['filesize']/(download_time)))
    print("Downloaded {} at {}".format(self.asset['filesize'], download_speed))

    return self.destination, download_speed

  def accelerate_download(self, url):
    start_time = time.time()
    offset = math.ceil(self.asset['filesize'] / self.chunks)
    in_byte = 0 # Set initially here, but then override
    
    print("Accelerated download -- {} -- {}".format(self.asset['name'], format_bytes(self.asset['filesize'], type="size")))

    # Build chunk manager state
    chunk_list = list(range(self.chunks))
    for chunk in chunk_list:
      self.chunk_manager.update({
        chunk: None
      })

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
      for i in range(self.chunks):
        out_byte = offset * (i+1)

        headers = {
          "Range": "bytes={}-{}".format(in_byte, out_byte)
          }
        task = (url, headers, i)
        executor.submit(self.get_chunk, task)

        in_byte = out_byte + 1 # Reset new in byte

    # Merge chunks
    print("Writing chunks to disk")
    with open(self.destination, 'a') as outfile:
      for chunk in self.chunk_manager:
        outfile.write(self.chunk_manager[chunk])

    download_time = time.time() - start_time
    download_speed = format_bytes(math.ceil(self.asset['filesize']/(download_time)))
    print("Downloaded {} at {}".format(self.asset['filesize'], download_speed))

    return self.destination, download_speed

  def get_chunk(self, task):
    url = task[0]
    headers = task[1]
    chunk_number = task[2]

    session = self._get_session()

    print("Getting chunk {}/{}".format(chunk_number + 1, self.chunks))
    r = session.get(url, headers=headers)
    self.chunk_manager[chunk_number] = r.content
    print("Completed chunk {}/{}".format(chunk_number + 1, self.chunks))

    return True
