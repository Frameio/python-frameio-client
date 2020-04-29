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
    
    url = self.asset['original']
    r = requests.get(url)
    
    open(final_destination, 'wb').write(r.content)
    