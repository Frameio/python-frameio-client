from .service import Service

class ReviewLink(Service):
  def create(self, project_id, **kwargs):
    """
    Create a review link.

    :Args:
      project_id (string): The project id.
    :Kwargs:
      kwargs: additional request parameters.

      Example::

        client.create_review_link(
          project_id="123",
          name="My Review Link",
          password="abc123"
        )
    """
    endpoint = '/projects/{}/review_links'.format(project_id)
    return self.client._api_call('post', endpoint, payload=kwargs)

  def list(self, project_id):
    """
    Get the review links of a project

    :Args:
      asset_id (string): The asset id.
    """
    endpoint = '/projects/{}/review_links'.format(project_id)
    return self.client._api_call('get', endpoint)

  def get(self, link_id, **kwargs):
    """
    Get a single review link

    :Args:
      link_id (string): The review link id.
    """
    endpoint = '/review_links/{}'.format(link_id)
    return self.client._api_call('get', endpoint, payload=kwargs)

  def get_assets(self, link_id):
    """
    Get items from a single review link.

    :Args:
      link_id (string): The review link id.

      Example::

        client.get_review_link_items(
          link_id="123"
        )
    """
    endpoint = '/review_links/{}/items'.format(link_id)
    return self.client._api_call('get', endpoint)

  def update_assets(self, link_id, **kwargs):
    """
    Add or update assets for a review link.

    :Args:
      link_id (string): The review link id.
    :Kwargs:
      kwargs: additional request parameters.

      Example::

        client.update_review_link_assets(
          link_id="123",
          asset_ids=["abc","def"]
        )
    """
    endpoint = '/review_links/{}/assets'.format(link_id)
    return self.client._api_call('post', endpoint, payload=kwargs)

  def update_settings(self, link_id, **kwargs):
    """
    Updates review link settings.

    :Args:
      link_id (string): The review link id.
    :Kwargs:
      kwargs: additional request parameters.

      Example::

        client.update_review_link(
          link_id,
          expires_at="2020-04-08T12:00:00+00:00",
          is_active=False,
          name="Review Link 123",
          password="my_fun_password",
        )
    """
    endpoint = '/review_links/{}'.format(link_id)
    return self.client._api_call('put', endpoint, payload=kwargs)


class PresentationLink(Service):
  def create(self, asset_id, **kwargs):
    """
    Create a presentation link.

    :Args:
      asset_id (string): The asset id.
    :Kwargs:
      kwargs: additional request parameters.

      Example::

        client.create_presentation_link(
          asset_id="9cee7966-4066-b326-7db1-f9e6f5e929e4",
          title="My fresh presentation",
          password="abc123"
        )
    """
    endpoint = '/assets/{}/presentations'.format(asset_id)
    return self.client._api_call('post', endpoint, payload=kwargs)
