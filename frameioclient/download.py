import os
import math
import requests

from .exceptions import DownloadException

class FrameioDownloader(object):
  def __init__(self, asset, download_folder):
    self.asset = asset
    self.download_folder = download_folder

  def get_download_key(self):
    try:
      url = self.asset['original']
    except KeyError:
      if self.asset['is_session_watermarked'] == True:
        resolution_map = dict() 
        for resolution_key, download_url in sorted(self.asset['downloads'].items()):
          resolution = resolution_key.split("_")[1] # Grab the item at index 1 (resolution)
          try:
            resolution = int(resolution)
            if download_url is not None:
              resolution_map.update({
                resolution: download_url
              })
          except ValueError:
            continue

        # Grab the highest resolution now
        url = resolution_map.values()[0]
      else:
        raise DownloadException

    return url

  def download(self):
    original_filename = self.asset['name']
    final_destination = os.path.join(self.download_folder, original_filename)

    print("Final destiation: {}".format(final_destination))

    if os.path.isfile(final_destination):
      return final_destination
    else:
      url = self.get_download_key()
      r = requests.get(url)
      open(final_destination, 'wb').write(r.content)
      return final_destination
    