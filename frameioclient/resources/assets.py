import mimetypes
import os
from typing import Dict, List, Optional, Union
from uuid import UUID

from frameioclient.lib.transfer import AWSClient

from ..lib import ApiReference, FrameioDownloader, FrameioUploader, constants
from ..lib.service import Service
from .projects import Project


class Asset(Service):
    def _build_asset_info(self, filepath: str) -> Dict:
        full_path = os.path.abspath(filepath)

        file_info = {
            "filepath": full_path,
            "filename": os.path.basename(full_path),
            "filesize": os.path.getsize(full_path),
            "mimetype": mimetypes.guess_type(full_path)[0],
        }

        return file_info

    @ApiReference(operation="#getAsset")
    def get(self, asset_id: Union[str, UUID]):
        """
        Get an asset by id.

        :param asset_id: The asset id.

        Example::

          client.assets.get(
            asset_id='1231-12414-afasfaf-aklsajflaksjfla',
          )

        """
        endpoint = "/assets/{}".format(asset_id)
        return self.client._api_call("get", endpoint)

    @ApiReference(operation="#getAssets")
    def get_children(
        self,
        asset_id: Union[str, UUID],
        includes: Optional[List] = [],
        slim: Optional[bool] = False,
        **kwargs,
    ):
        """
        Get a folder.

        :param asset_id: The asset id.

        :Keyword Arguments:
          includes (list): List of includes you would like to add.

        Example::

            client.assets.get_children(
              asset_id='1231-12414-afasfaf-aklsajflaksjfla',
              include=['review_links','cover_asset','creator','presentation']
            )
        """
        endpoint = "/assets/{}/children".format(asset_id)

        if slim == True:
            query_params = ""

            if len(includes) > 0:
                query_params += "?include={}".format(includes.join(","))
            else:
                # Always include children
                query_params += "?" + "include=children"

            # Only fields
            query_params += (
                "&" + "only_fields=" + ",".join(constants.asset_excludes["only_fields"])
            )

            # # Drop includes
            query_params += (
                "&"
                + "drop_includes="
                + ",".join(constants.asset_excludes["drop_includes"])
            )

            # # Hard drop fields
            query_params += (
                "&"
                + "hard_drop_fields="
                + ",".join(constants.asset_excludes["hard_drop_fields"])
            )

            # Excluded fields
            # query_params += '&' + 'excluded_fields=' + ','.join(constants.asset_excludes['excluded_fields'])

            # # Sort by inserted_at
            # query_params += '&' + 'sort=-inserted_at'

            endpoint += query_params

            # print("Final URL", endpoint)

        return self.client._api_call("get", endpoint, kwargs)

    @ApiReference(operation="#createAsset")
    def create(
        self,
        parent_asset_id: Union[str, UUID],
        name: str,
        type: Optional[str] = "file",
        filetype: Optional[str] = None,
        filesize: Optional[int] = None,
    ):
        """
        Create an asset.

        :param parent_asset_id: The parent asset id
        :param name: The asset's display name
        :param type: The type of asset ('file', 'folder')
        :param filesize: The size of the asset in bytes
        :param filetype: The MIME-type of the asset

        Example::

            client.assets.create(
              parent_asset_id="123abc",
              name="ExampleFile.mp4",
              type="file",
              filetype="video/mp4",
              filesize=123456
            )
        """
        kwargs = {
            "name": name,
            "type": type,
            "filesize": filesize,
            "filetype": filetype,
        }

        endpoint = "/assets/{}/children".format(parent_asset_id)
        return self.client._api_call("post", endpoint, payload={**kwargs})

    @ApiReference(operation="#createAsset")
    def create_folder(self, parent_asset_id: str, name: str = "New Folder"):
        """
        Create a new folder.

        :param parent_asset_id: The parent asset id.
        :param name: The name of the new folder.

        Example::

            client.assets.create_folder(
              parent_asset_id="123abc",
              name="ExampleFile.mp4",
            )
        """
        endpoint = "/assets/{}/children".format(parent_asset_id)
        return self.client._api_call(
            "post", endpoint, payload={"name": name, "type": "folder"}
        )

    @ApiReference(operation="#createAsset")
    def from_url(self, parent_asset_id: Union[str, UUID], name: str, url: str):
        """
        Create an asset from a URL.

        :param parent_asset_id: The parent asset id.
        :param name: The filename.
        :param url: The remote URL.

        Example::

            client.assets.from_url(
              parent_asset_id="123abc",
              name="ExampleFile.mp4",
              type="file",
              url="https://"
            )
        """
        payload = {"name": name, "type": "file", "source": {"url": url}}

        endpoint = "/assets/{}/children".format(parent_asset_id)
        return self.client._api_call("post", endpoint, payload=payload)

    @ApiReference(operation="#updateAsset")
    def update(self, asset_id: Union[str, UUID], **kwargs):
        """
        Updates an asset

        :param asset_id: The asset's id

        :Keyword Arguments:
          the fields to update

        Example::

            client.assets.update("adeffee123342", name="updated_filename.mp4")
        """
        endpoint = "/assets/{}".format(asset_id)
        return self.client._api_call("put", endpoint, kwargs)

    @ApiReference(operation="#copyAsset")
    def copy(
        self,
        destination_folder_id: Union[str, UUID],
        target_asset_id: Union[str, UUID],
    ):
        """
        Copy an asset

        :param destination_folder_id: The id of the folder you want to copy into.
        :param target_asset_id: The id of the asset you want to copy.

        Example::

            client.assets.copy("adeffee123342", id="7ee008c5-49a2-f8b5-997d-8b64de153c30")
        """
        kwargs = {"id": target_asset_id}
        endpoint = "/assets/{}/copy".format(destination_folder_id)
        return self.client._api_call("post", endpoint, kwargs)

    @ApiReference(operation="#batchCopyAsset")
    def bulk_copy(
        self,
        destination_folder_id: Union[str, UUID],
        asset_list: Optional[List] = [],
        copy_comments: Optional[bool] = False,
    ):
        """
        Bulk copy assets

        :param destination_folder_id: The id of the folder you want to copy into.
        :param asset_list: A list of the asset IDs you want to copy.
        :param copy_comments: Whether or not to copy comments: True or False.

        Example::

            client.assets.bulk_copy(
              "adeffee123342",
              asset_list=[
                "7ee008c5-49a2-f8b5-997d-8b64de153c30",
                "7ee008c5-49a2-f8b5-997d-8b64de153c30"
              ],
              copy_comments=True
            )
        """
        payload = {"batch": []}

        if copy_comments:
            payload["copy_comments"] = "all"

        for asset in asset_list:
            payload["batch"].append({"id": asset})

        endpoint = "/batch/assets/{}/copy".format(destination_folder_id)
        return self.client._api_call("post", endpoint, payload)

    @ApiReference(operation="#addVersionToAsset")
    def add_version(
        self, target_asset_id: Union[str, UUID], new_version_id: Union[str, UUID]
    ):
        """
        Add a new version to a version stack, or create a new one!

        :param target_asset_id: The main/destination Asset or Version Stack.
        :param new_version_id: The id for the asset you want to add to the Version Stack or create a new one with.

        Example::

            client.add_version_to_asset(
              destination_id="123",
              next_asset_id="234"
            )
        """

        payload = {"next_asset_id": new_version_id}

        endpoint = f"/assets/{target_asset_id}/version"

        return self.client._api_call("post", endpoint, payload=payload)

    @ApiReference(operation="#deleteAsset")
    def delete(self, asset_id: Union[str, UUID]):
        """
        Delete an asset

        :param asset_id: the asset's id
        """
        endpoint = "/assets/{}".format(asset_id)
        return self.client._api_call("delete", endpoint)

    def _upload(self, asset: Dict, file: object):
        """
        Upload an asset. The method will exit once the file is uploaded.

        :param asset: The asset object as returned via the frame.io API.
        :param file: The file to upload.

        Example::

            client.upload(asset, open('example.mp4'))
        """
        uploader = FrameioUploader(asset, file)
        uploader.upload()

    def upload(
        self,
        destination_id: Union[str, UUID],
        filepath: str,
        asset: Optional[Dict] = None,
    ):
        """
        Upload a file. The method will exit once the file is uploaded.

        :param destination_id: The destination Project or Folder ID.
        :param filepath: The location of the file on your local filesystem that you want to upload.

        Example::

          client.assets.upload('1231-12414-afasfaf-aklsajflaksjfla', "./file.mov")
        """

        # Check if destination is a project or folder
        # If it's a project, well then we look up its root asset ID, otherwise we use the folder id provided
        # Then we start our upload

        try:
            # First try to grab it as a folder
            folder_id = self.get(destination_id)["id"]
        except Exception as e:
            # Then try to grab it as a project
            folder_id = Project(self.client).get(destination_id)["root_asset_id"]
        finally:
            file_info = self._build_asset_info(filepath)

            if not asset:
                try:
                    asset = self.create(
                        folder_id,
                        type="file",
                        name=file_info["filename"],
                        filetype=file_info["mimetype"],
                        filesize=file_info["filesize"],
                    )

                except Exception as e:
                    print(e)

                try:
                    with open(file_info["filepath"], "rb") as fp:
                        self._upload(asset, fp)

                except Exception as e:
                    print(e)

        return asset

    def download(
        self,
        asset: Dict,
        download_folder: str,
        prefix: Optional[str] = None,
        multi_part: Optional[bool] = None,
        replace: Optional[bool] = False,
    ):
        """
        Download an asset. The method will exit once the file is downloaded.

        :param asset: The asset object.
        :param download_folder: The location to download the file to.
        :param multi_part: Attempt to do a multi-part download (non-WMID assets).
        :param replace: Whether or not you want to replace a file if one is found at the destination path.

        Example::

            client.assets.download(asset, "~./Downloads")
        """

        downloader = FrameioDownloader(
            asset, download_folder, prefix, multi_part, replace
        )

        return AWSClient(downloader, concurrency=5).multi_thread_download()

    def upload_folder(self, source_path: str, destination_id: Union[str, UUID]):
        """
        Upload a folder full of assets, maintaining hierarchy. \
          The method will exit once the file is uploaded.

        :param filepath: The location of the folder on your disk.
        :param destination_id: The destination Project or Folder ID.

        Example::

            client.assets.upload("./file.mov", "1231-12414-afasfaf-aklsajflaksjfla")
          """

        # Check if destination is a project or folder
        # If it's a project, well then we look up its root asset ID, otherwise we use the folder id provided
        # Then we start our upload

        try:
            # First try to grab it as a folder
            folder_id = self.get(destination_id)["id"]
        except Exception as e:
            # Then try to grab it as a project
            folder_id = Project(self.client).get(destination_id)["root_asset_id"]
        finally:
            return FrameioUploader().upload_recursive(
                self.client, source_path, folder_id
            )
