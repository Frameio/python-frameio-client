import os
import mimetypes

from .service import Service
from .projects import Project

from ..lib import FrameioUploader, FrameioDownloader

class Asset(Service):
  def get(self, asset_id):
    """
    Get an asset by id.

    :Args:
      asset_id (string): The asset id.
    """
    endpoint = '/assets/{}'.format(asset_id)
    return self.client._api_call('get', endpoint)

  def get_children(self, asset_id, **kwargs):
    """
    Get a folder.

    :Args:
      asset_id (string): The asset id.
    """
    endpoint = '/assets/{}/children'.format(asset_id)
    return self.client._api_call('get', endpoint, kwargs)

  def create(self, parent_asset_id, **kwargs):
    """
    Create an asset.

    :Args:
      parent_asset_id (string): The parent asset id.
    :Kwargs:
      (optional) kwargs: additional request parameters.

      Example::

        client.create_asset(
          parent_asset_id="123abc",
          name="ExampleFile.mp4",
          type="file",
          filetype="video/mp4",
          filesize=123456
        )
    """
    endpoint = '/assets/{}/children'.format(parent_asset_id)
    return self.client._api_call('post', endpoint, payload=kwargs)
  
  def from_url(self, parent_asset_id, name, url):
    """
    Create an asset from a URL.

    :Args:
      parent_asset_id (string): The parent asset id.
      name (string): The filename.
      url (string): The remote URL.

      Example::

        client.create_asset(
          parent_asset_id="123abc",
          name="ExampleFile.mp4",
          type="file",
          url="https://"
        )
    """
    
    payload = {
      "name": name,
      "source": {
        "url": url
      }
    }

    endpoint = '/assets/{}/children'.format(parent_asset_id)
    return self.client._api_call('post', endpoint, payload=payload)

  def update(self, asset_id, **kwargs):
    """
    Updates an asset

    :Args:
      asset_id (string): the asset's id
    :Kwargs:
      the fields to update

      Example::
        client.update_asset("adeffee123342", name="updated_filename.mp4")
    """
    endpoint = '/assets/{}'.format(asset_id)
    return self.client._api_call('put', endpoint, kwargs)

  def copy(self, destination_folder_id, **kwargs):
    """
    Copy an asset

    :Args:
      destination_folder_id (string): The id of the folder you want to copy into.
    :Kwargs:
      id (string): The id of the asset you want to copy.

      Example::
        client.copy_asset("adeffee123342", id="7ee008c5-49a2-f8b5-997d-8b64de153c30")
    """
    endpoint = '/assets/{}/copy'.format(destination_folder_id)
    return self.client._api_call('post', endpoint, kwargs)

  def bulk_copy(self, destination_folder_id, asset_list=[], copy_comments=False):
    """Bulk copy assets

    :Args:
      destination_folder_id (string): The id of the folder you want to copy into.
    :Kwargs:
      asset_list (list): A list of the asset IDs you want to copy.
      copy_comments (boolean): Whether or not to copy comments: True or False.

      Example::
        client.bulk_copy_assets("adeffee123342", asset_list=["7ee008c5-49a2-f8b5-997d-8b64de153c30", \ 
        "7ee008c5-49a2-f8b5-997d-8b64de153c30"], copy_comments=True)
    """
    
    payload = {"batch": []}
    new_list = list()

    if copy_comments:
      payload['copy_comments'] = "all"

    for asset in asset_list:
      payload['batch'].append({"id": asset})

    endpoint = '/batch/assets/{}/copy'.format(destination_folder_id)
    return self.client._api_call('post', endpoint, payload)

  def delete(self, asset_id):
    """
    Delete an asset

    :Args:
      asset_id (string): the asset's id
    """
    endpoint = '/assets/{}'.format(asset_id)
    return self.client._api_call('delete', endpoint)

  def _upload(self, asset, file):
    """
    Upload an asset. The method will exit once the file is uploaded.

    :Args:
      asset (object): The asset object.
      file (file): The file to upload.

      Example::

        client.upload(asset, open('example.mp4')) // TODO fix this example (bad way of opening file)
    """

    uploader = FrameioUploader(asset, file)
    uploader.upload()

  def upload_folder(self, destination_id, folderpath):
    pass

  def build_asset_info(self, filepath):
    full_path = os.path.abspath(filepath)

    file_info = {
        "filepath": full_path,
        "filename": os.path.basename(full_path),
        "filesize": os.path.getsize(full_path),
        "mimetype": mimetypes.guess_type(full_path)[0]
    }

    return file_info

  def upload(self, destination_id, filepath):
    # Check if destination is a project or folder
    # If it's a project, well then we look up its root asset ID, otherwise we use the folder id provided
    # Then we start our upload

    try:
        # First try to grab it as a folder
        folder_id = self.get(destination_id)['id']
    except Exception as e:
        # Then try to grab it as a project
        folder_id = Project(self.client).get_project(destination_id)['root_asset_id']
    finally:
      file_info = self.build_asset_info(filepath)
      try:
        asset = self.create(folder_id,  
            type="file",
            name=file_info['filename'],
            filetype=file_info['mimetype'],
            filesize=file_info['filesize']
        )

        with open(file_info['filepath'], "rb") as fp:
          self._upload(asset, fp)

      except Exception as e:
          print(e)

  def download(self, asset, download_folder, prefix=None, multi_part=False, concurrency=5):
    """
    Download an asset. The method will exit once the file is downloaded.

    :Args:
      asset (object): The asset object.
      download_folder (path): The location to download the file to.

      Example::

        client.download(asset, "~./Downloads")
    """
    downloader = FrameioDownloader(asset, download_folder, prefix, multi_part, concurrency)
    return downloader.download_handler()