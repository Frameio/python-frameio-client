import requests
import os

class FrameioDownloader(object):
  def __init__(self, asset, download_folder, replace):
    self.asset = asset
    self.download_folder = download_folder
    self.replace = replace

  def download(self):
    original_filename = self.asset['name']
    final_destination = os.path.join(self.download_folder, original_filename)

    if os.path.isfile(final_destination) and not self.replace:
      try:
        raise FileExistsError   # Added in python 3.3
      except NameError:
        raise OSError('File exists')

    url = self.asset['original']
    r = requests.get(url, stream=True)

    handle = open(final_destination, 'wb')

    for chunk in r.iter_content(chunk_size=4096):
      if chunk:
        handle.write(chunk)
