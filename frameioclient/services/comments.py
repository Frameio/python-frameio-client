from ..lib.utils import ApiReference
from ..lib.service import Service
from typing import Union
from uuid import UUID


class Comment(Service):
    @ApiReference(operation="#createComment")
    def create(self, asset_id: Union[str, UUID], **kwargs):
        """
        Create a comment.

        :param asset_id: The asset id.

        :Keyword Arguments:
          (optional) kwargs: additional request parameters.

        Example::

          client.comments.create(
            asset_id="123abc",
            text="Hello world"
          )
          """
        endpoint = "/assets/{}/comments".format(asset_id)
        return self.client._api_call("post", endpoint, payload=kwargs)

    @ApiReference(operation="#getComment")
    def get(self, comment_id: Union[str, UUID], **kwargs):
        """
        Get a comment.

        :param comment_id: The comment id.
          """
        endpoint = "/comments/{}".format(comment_id)
        return self.client._api_call("get", endpoint, **kwargs)

    @ApiReference(operation="#getComments")
    def list(self, asset_id: Union[str, UUID], **kwargs):
        """
        Get an asset's comments.

        :param asset_id: The asset id.
          """
        endpoint = "/assets/{}/comments".format(asset_id)
        return self.client._api_call("get", endpoint, **kwargs)

    @ApiReference(operation="#updateComment")
    def update(self, comment_id: Union[str, UUID], **kwargs):
        """
        Update a comment.

        :param comment_id: The comment id.

        :Keyword Arguments:
          (optional) kwargs: additional request parameters.

        Example::

          client.comments.update(
            comment_id="123abc",
            text="Hello world"
          )
          """
        endpoint = "/comments/{}".format(comment_id)
        return self.client._api_call("post", endpoint, payload=kwargs)

    @ApiReference(operation="#deleteComment")
    def delete(self, comment_id: Union[str, UUID]):
        """
        Delete a comment.

        :param comment_id: The comment id.
          """
        endpoint = "/comments/{}".format(comment_id)
        return self.client._api_call("delete", endpoint)

    @ApiReference(operation="#createReply")
    def reply(self, comment_id, **kwargs):
        """
        Reply to an existing comment.

        Args:
          comment_id (string): The comment id.

        :Keyword Arguments:
          (optional) kwargs: additional request parameters.

        Example::

          client.comments.reply(
            comment_id="123abc",
            text="Hello world"
          )
          """
        endpoint = "/comments/{}/replies".format(comment_id)
        return self.client._api_call("post", endpoint, payload=kwargs)
