import requests
import math
import os

class FrameioDownloader(object):
  def __init__(self, asset, download_folder):
    self.asset = asset
    self.download_folder = download_folder

  def download(self):
    original_filename = self.asset['name']
    final_destination = os.path.join(self.download_folder, original_filename)

    print(f"Final destiation: {final_destination}")

    if os.path.isfile(final_destination):
      return final_destination
    else:
      url = self.asset['original']
      r = requests.get(url)
      open(final_destination, 'wb').write(r.content)
      return final_destination
    