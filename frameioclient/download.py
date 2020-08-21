import os
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from frameioclient.utils import calculate_hash


class FrameioDownloader(object):
  def __init__(self, asset, download_folder, replace):
    self.asset = asset
    self.download_folder = download_folder
    self.replace = replace
    self.attempts = 0
    self.retry_limit = 3

    self.http_retry_strategy = Retry(
      total=3,
      backoff_factor=1,
      status_forcelist=[408, 500, 502, 503, 504],
      method_whitelist=['GET']
    )

  def download(self):
    original_filename = self.asset['name']
    final_destination = os.path.join(self.download_folder, original_filename)

    if os.path.isfile(final_destination) and not self.replace:
      try:
        raise FileExistsError
      except NameError:
        raise OSError('File exists')  # Python < 3.3

    adapter = HTTPAdapter(max_retries=self.http_retry_strategy)
    http = requests.Session()
    http.mount('https://', adapter)

    url = self.asset['original']

    try:
      original_checksum = self.asset['checksums']['xx_hash']
    except (TypeError, KeyError):
      original_checksum = None

    while self.attempts < self.retry_limit:
      r = http.request('GET', url, stream=True)

      with open(final_destination, 'wb') as handle:
        try:
          for chunk in r.iter_content(chunk_size=4096):
            if chunk:
              handle.write(chunk)
        except requests.exceptions.ChunkedEncodingError:
          self.attempts += 1
          continue

      if not original_checksum:
        break

      if calculate_hash(final_destination) == original_checksum:
        break

      self.attempts += 1
