from .service import Service

class Comment(Service):
  def create(self, asset_id, **kwargs):
    """
    Create a comment.

    :Args:
      asset_id (string): The asset id.
    :Kwargs:
      (optional) kwargs: additional request parameters.

      Example::

        client.create_comment(
          asset_id="123abc",
          text="Hello world"
        )
    """
    endpoint = '/assets/{}/comments'.format(asset_id)
    return self.client._api_call('post', endpoint, payload=kwargs)

  def get(self, comment_id, **kwargs):
    """
    Get a comment.

    :Args:
      comment_id (string): The comment id.
    """
    endpoint = '/comments/{}'.format(comment_id)
    return self.client._api_call('get', endpoint, **kwargs)

  def list(self, asset_id, **kwargs):
    """
    Get an asset's comments.

    :Args:
      asset_id (string): The asset id.
    """
    endpoint = '/assets/{}/comments'.format(asset_id)
    return self.client._api_call('get', endpoint, **kwargs)

  def update(self, comment_id, **kwargs):
    """
    Update a comment.

    :Args:
      comment_id (string): The comment id.
    :Kwargs:
      (optional) kwargs: additional request parameters.

      Example::

        client.create_comment(
          comment_id="123abc",
          text="Hello world"
        )
    """
    endpoint = '/comments/{}'.format(comment_id)
    return self.client._api_call('post', endpoint, payload=kwargs)

  def delete(self, comment_id):
    """
    Delete a comment.

    :Args:
      comment_id (string): The comment id.
    """
    endpoint = '/comments/{}'.format(comment_id)
    return self.client._api_call('delete', endpoint)

  def reply(self, comment_id, **kwargs):
    """
    Reply to an existing comment.

    :Args:
      comment_id (string): The comment id.
    :Kwargs:
      (optional) kwargs: additional request parameters.

      Example::

        client.reply_comment(
          comment_id="123abc",
          text="Hello world"
        )
    """
    endpoint = '/comments/{}/replies'.format(comment_id)
    return self.client._api_call('post', endpoint, payload=kwargs)
