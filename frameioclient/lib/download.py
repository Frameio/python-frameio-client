import io
import os
import math
import time
import logging
import enlighten
import requests
import threading
import concurrent.futures

from .utils import Utils
from .exceptions import DownloadException, WatermarkIDDownloadException, AssetNotFullyUploaded

thread_local = threading.local()

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger('enlighten')

class FrameioDownloader(object):
  def __init__(self, asset, download_folder, prefix, multi_part=False, concurrency=5, progress=True):
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
    self.tasks = list()
    self.bytes_started = 0
    self.bytes_completed = 0
    self.in_progress = 0
    self.filename = Utils.normalize_filename(asset["name"])

    self._evaluate_asset()

  def _calculate_in_progress(self):
    self.in_progress = self.bytes_started - self.bytes_completed
    return self.in_progress

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
      fp = open(self.destination, "w")
      # fp.write(b"\0" * self.file_size) # Disabled to prevent pre-allocatation of disk space
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
    print("Beginning download -- {} -- {}".format(self.asset["name"], Utils.format_bytes(self.file_size, type="size")))

    # Downloading
    r = requests.get(url)
    open(self.destination, "wb").write(r.content)

    download_time = time.time() - start_time
    download_speed = Utils.format_bytes(math.ceil(self.file_size/(download_time)))
    print("Downloaded {} at {}".format(Utils.format_bytes(self.file_size, type="size"), download_speed))

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
    
    print("Multi-part download -- {} -- {}".format(self.asset["name"], Utils.format_bytes(self.file_size, type="size")))

    # Queue up threads
    with enlighten.get_manager() as manager:
      status = manager.status_bar(
        position=4,
        status_format=u'{fill}Stage: {stage}{fill}{elapsed}',
        color='bold_underline_bright_white_on_lightslategray',
        justify=enlighten.Justify.CENTER, 
        stage='Initializing',
        autorefresh=True, 
        min_delta=0.5
      )

      BAR_FORMAT = '{desc}{desc_pad}|{bar}|{percentage:3.0f}% ' + \
                  'Downloading: {count_1:.2j}/{total:.2j} ' + \
                  'Completed: {count_2:.2j}/{total:.2j} ' + \
                  '[{elapsed}<{eta}, {rate:.2j}{unit}/s]'

      # Add counter to track completed chunks
      initializing = manager.counter(
        position=2,
        total=float(self.file_size),
        desc='Progress',
        unit='B',
        bar_format=BAR_FORMAT,
      )

      # Add additional counter
      in_progress = initializing.add_subcounter('yellow', all_fields=True)
      completed = initializing.add_subcounter('green', all_fields=True)

      # Set default state
      initializing.refresh()

      status.update(stage='Downloading', color='green')
      
      with concurrent.futures.ThreadPoolExecutor(max_workers=self.concurrency) as executor:
        for i in range(int(self.chunks)):
          # Increment by the iterable + 1 so we don't mutiply by zero
          out_byte = offset * (i+1)
          # Create task tuple
          task = (url, in_byte, out_byte, i, in_progress)
          # Stagger start for each chunk by 0.1 seconds
          if i < self.concurrency: time.sleep(0.1)
          # Append tasks to futures list
          self.futures.append(executor.submit(self.download_chunk, task))
          # Reset new in byte equal to last out byte
          in_byte = out_byte
    
        # Keep updating the progress while we have > 0 bytes left.
        # Wait on threads to finish
        for future in concurrent.futures.as_completed(self.futures):
          try:
            chunk_size = future.result()
            completed.update_from(in_progress, float((chunk_size - 1)), force=True)
          except Exception as exc:
            print(exc)
          
        # Calculate and print stats
        download_time = time.time() - start_time
        download_speed = Utils.format_bytes(math.ceil(self.file_size/(download_time)))

        # Perform hash-verification
        status.update(stage='Verifying')

        VERIFICATION_FORMAT = '{desc}{desc_pad}|{bar}|{percentage:3.0f}% ' + \
                    'Progress: {count:.2j}/{total:.2j} ' + \
                    '[{elapsed}<{eta}, {rate:.2j}{unit}/s]'

        # Add counter to track completed chunks
        verification = manager.counter(
          position=1,
          total=float(self.file_size),
          desc='Verifying',
          unit='B',
          bar_format=VERIFICATION_FORMAT,
          color='purple'
        )

        Utils.calculate_hash(self.destination, progress_callback=verification)

        status.update(stage='Download Complete!', force=True)

        LOGGER.info("Downloaded {} at {}".format(Utils.format_bytes(self.file_size, type="size"), download_speed))
    
    return self.destination

  def download_chunk(self, task):
    # Download a particular chunk
    # Called by the threadpool executor

    url = task[0]
    start_byte = task[1]
    end_byte = task[2]
    chunk_number = task[3]
    in_progress = task[4]

    # Update the count for bytes we've started to download

    chunk_size = (end_byte - start_byte)

    if self.bytes_started + (chunk_size) > self.file_size:
      difference = abs(self.file_size - (self.bytes_started + chunk_size)) # should be negative
      chunk_size = chunk_size - difference
      print(f"Chunk size as done via math: {chunk_size}")
    else:
      pass

    # Set chunk size in a smarter way
    self.bytes_started += (chunk_size)
    in_progress.update(float(chunk_size))

    # Get the shared thread's requests session
    session = self._get_session()

    # print("Beginning: \t {}/{}".format(chunk_number + 1, self.chunks).expandtabs(3))
         
    # Specify the start and end of the range request 
    headers = {"Range": "bytes=%d-%d" % (start_byte, end_byte)} 

    # Grab the data as a stream
    r = session.get(url, headers=headers, stream=True)

    with open(self.destination, "r+b") as fp:
      fp.seek(start_byte) # Seek to the right spot in the file
      chunk_size = len(r.content) # Get the final chunk size
      fp.write(r.content) # Write the data
      # print("Completed: \t {}/{}".format(chunk_number + 1, self.chunks).expandtabs(3))

    self.bytes_completed += (chunk_size)
    if self.bytes_completed > self.file_size:
      self.bytes_completed = self.file_size

    self._calculate_in_progress()

    return chunk_size

  @staticmethod
  def get_byte_range(url, start_byte=0, end_byte=2048):
    headers = {"Range": "bytes=%d-%d" % (start_byte, end_byte)}
    br = requests.get(url, headers=headers).content
    return br