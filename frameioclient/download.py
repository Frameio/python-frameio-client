import os
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


class FrameioDownloader(object):
  def __init__(self, asset, download_folder, replace):
    self.asset = asset
    self.download_folder = download_folder
    self.replace = replace
    self.retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429],
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

    adapter = HTTPAdapter(max_retries=self.retry_strategy)
    http = requests.Session()
    http.mount('https://', adapter)

    url = self.asset['original']

    r = http.request(
      'GET',
      url,
      stream=True
    )

    handle = open(final_destination, 'wb')

    for chunk in r.iter_content(chunk_size=4096):
      if chunk:
        handle.write(chunk)
