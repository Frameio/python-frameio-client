import io
import os
import math
import time
import requests
import threading
import concurrent.futures

from .utils import format_bytes, normalize_filename
from .exceptions import DownloadException, WatermarkIDDownloadException, AssetNotFullyUploaded

thread_local = threading.local()

class FrameioDownloader(object):
  def __init__(self, asset, download_folder, prefix, multi_part=False, concurrency=5):
    self.multi_part = multi_part
    self.asset = asset
    self.asset_type = None
    self.download_folder = download_folder
    self.resolution_map = dict()
    self.destination = None
    self.watermarked = asset['is_session_watermarked'] # Default is probably false
    self.file_size = asset["filesize"]
    self.concurrency = concurrency
    self.futures = list()
    self.chunk_size = (25 * 1024 * 1024) # 25 MB chunk size
    self.chunks = math.ceil(self.file_size/self.chunk_size)
    self.prefix = prefix
    self.filename = normalize_filename(asset["name"])

    self._evaluate_asset()

  def _evaluate_asset(self):
    if self.asset.get("_type") != "file":
      raise DownloadException(message="Unsupport Asset type: {}".format(self.asset.get("_type")))
    
    if self.asset.get("upload_completed_at") == None:
      raise AssetNotFullyUploaded

  def _get_session(self):
    if not hasattr(thread_local, "session"):
        thread_local.session = requests.Session()
    return thread_local.session

  def _create_file_stub(self):
    try:
      fp = open(self.destination, "wb")
      fp.write(b"\0" * self.file_size)
      fp.close()
    except FileExistsError as e:
      print(e)
      raise e
    return True

  def get_download_key(self):
    try:
      url = self.asset['original']
    except KeyError as e:
      if self.watermarked == True:
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
        raise WatermarkIDDownloadException

    return url

  def get_path(self):
    if self.prefix != None:
      self.filename = self.prefix + self.filename

    if self.destination == None:
      final_destination = os.path.join(self.download_folder, self.filename)
      self.destination = final_destination
      
    return self.destination

  def download_handler(self):
    if os.path.isfile(self.get_path()):
      print("File already exists at this location.")
      return self.destination
    else:
      url = self.get_download_key()

      if self.watermarked == True:
        return self.download(url)
      else:
        if self.multi_part == True:
          return self.multi_part_download(url)
        else:
          return self.download(url)

  def download(self, url):
    start_time = time.time()
    print("Beginning download -- {} -- {}".format(self.asset["name"], format_bytes(self.file_size, type="size")))

    # Downloading
    r = requests.get(url)
    open(self.destination, "wb").write(r.content)

    download_time = time.time() - start_time
    download_speed = format_bytes(math.ceil(self.file_size/(download_time)))
    print("Downloaded {} at {}".format(format_bytes(self.file_size, type="size"), download_speed))

    return self.destination, download_speed

  def multi_part_download(self, url):
    start_time = time.time()

    # Generate stub
    try:
      self._create_file_stub()

    except Exception as e:
      raise DownloadException(message=e)

    offset = math.ceil(self.file_size / self.chunks)
    in_byte = 0 # Set initially here, but then override
    
    print("Multi-part download -- {} -- {}".format(self.asset["name"], format_bytes(self.file_size, type="size")))

    # Queue up threads
    with concurrent.futures.ThreadPoolExecutor(max_workers=self.concurrency) as executor:
      for i in range(int(self.chunks)):
        out_byte = offset * (i+1) # Increment by the iterable + 1 so we don't mutiply by zero
        task = (url, in_byte, out_byte, i)

        self.futures.append(executor.submit(self.download_chunk, task))
        in_byte = out_byte # Reset new in byte equal to last out byte
    
    # Wait on threads to finish
    for future in concurrent.futures.as_completed(self.futures):
      try:
        status = future.result()
        print(status)
      except Exception as exc:
        print(exc)
    
    # Calculate and print stats
    download_time = time.time() - start_time
    download_speed = format_bytes(math.ceil(self.file_size/(download_time)))
    print("Downloaded {} at {}".format(format_bytes(self.file_size, type="size"), download_speed))

    return self.destination

  def download_chunk(self, task):
    # Download a particular chunk
    # Called by the threadpool executor

    url = task[0]
    start_byte = task[1]
    end_byte = task[2]
    chunk_number = task[3]

    session = self._get_session()
    print("Getting chunk {}/{}".format(chunk_number + 1, self.chunks))
         
    # Specify the starting and ending of the file 
    headers = {"Range": "bytes=%d-%d" % (start_byte, end_byte)} 

    # Grab the data as a stream
    r = session.get(url, headers=headers, stream=True)

    with open(self.destination, "r+b") as fp:
      fp.seek(start_byte) # Seek to the right of the file
      fp.write(r.content) # Write the data
      print("Done writing chunk {}/{}".format(chunk_number + 1, self.chunks))

    return "Complete!"
