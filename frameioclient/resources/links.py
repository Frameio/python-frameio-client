from typing import Union
from uuid import UUID
from ..lib.utils import ApiReference
from ..lib.service import Service


class ReviewLink(Service):
    @ApiReference(operation="#reviewLinkCreate")
    def create(self, project_id: Union[str, UUID], **kwargs):
        """
        Create a review link.

        Args:
          project_id (string): The project id.

        :Keyword Arguments:
          kwargs: additional request parameters.

        Example::

          client.review_links.create(
            project_id="123",
            name="My Review Link",
            password="abc123"
          )
        """
        endpoint = "/projects/{}/review_links".format(project_id)
        return self.client._api_call("post", endpoint, payload=kwargs)

    @ApiReference(operation="#reviewLinksList")
    def list(self, project_id: Union[str, UUID]):
        """
        Get the review links of a project

        Args:
          asset_id (string): The asset id.
        """
        endpoint = "/projects/{}/review_links".format(project_id)
        return self.client._api_call("get", endpoint)

    @ApiReference(operation="#reviewLinkGet")
    def get(self, link_id: Union[str, UUID], **kwargs):
        """
        Get a single review link

        Args:
          link_id (string): The review link id.
        """
        endpoint = "/review_links/{}".format(link_id)
        return self.client._api_call("get", endpoint, payload=kwargs)

    @ApiReference(operation="#reviewLinkItemsList")
    def get_assets(self, link_id: Union[str, UUID]):
        """
        Get items from a single review link.

        Args:
          link_id (string): The review link id.

        Example::

          client.review_links.get_assets(
            link_id="123"
          )
        """
        endpoint = "/review_links/{}/items".format(link_id)
        return self.client._api_call("get", endpoint)

    @ApiReference(operation="#reviewLinkItemsUpdate")
    def update_assets(self, link_id: Union[str, UUID], **kwargs):
        """
        Add or update assets for a review link.

        Args:
          link_id (string): The review link id.

        :Keyword Arguments:
          kwargs: additional request parameters.

        Example::

          client.review_links.update_assets(
            link_id="123",
            asset_ids=["abc","def"]
          )
        """
        endpoint = "/review_links/{}/assets".format(link_id)
        return self.client._api_call("post", endpoint, payload=kwargs)

    @ApiReference(operation="#reviewLinkUpdate")
    def update_settings(self, link_id: Union[str, UUID], **kwargs):
        """
        Updates review link settings.

        Args:
          link_id (string): The review link id.

        :Keyword Arguments:
          kwargs: additional request parameters.

        Example::

          client.review_links.update_settings(
            link_id,
            expires_at="2020-04-08T12:00:00+00:00",
            is_active=False,
            name="Review Link 123",
            password="my_fun_password",
          )
        """
        endpoint = "/review_links/{}".format(link_id)
        return self.client._api_call("put", endpoint, payload=kwargs)


class PresentationLink(Service):
    @ApiReference(operation="#createPresentation")
    def create(self, asset_id: Union[str, UUID], **kwargs):
        """
        Create a presentation link.

        Args:
          asset_id (string): The asset id.

        :Keyword Arguments:
          kwargs: additional request parameters.

        Example::

          client.presentation_links.create(
            asset_id="9cee7966-4066-b326-7db1-f9e6f5e929e4",
            title="My fresh presentation",
            password="abc123"
          )
        """
        endpoint = "/assets/{}/presentations".format(asset_id)
        return self.client._api_call("post", endpoint, payload=kwargs)

    def update(self, presentation_id: Union[str, UUID], **kwargs):
        """
        Update a presentation link.

        Args:
          presentation_id (string): The presentation id.

        :Keyword Arguments:
          kwargs: additional request parameters.

        Example::

          client.presentation_links.update(
            presentation_id="9cee7966-4066-b326-7db1-f9e6f5e929e4",
            name="My fresh presentation",
            enabled=False
          )
        """
        endpoint = "/presentations/{}".format(presentation_id)
        return self.client._api_call("put", endpoint, payload=kwargs)
