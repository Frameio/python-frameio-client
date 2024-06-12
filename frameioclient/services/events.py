from typing import Union
from uuid import UUID

from ..lib.service import Service


class Events(Service):
    def list_for_account(self, account_id: Union[str, UUID]):
        """
        Get a list of Event logs for the specified account_id.

        :param account_id: Account ID you want to get event logs for.

        Example::

          client.events.list(
            account_id="6bdcb4d9-9a2e-a765-4548-ae6b27a6c024"
          )

        Returns:
            list: List of event logs.
        """
        endpoint = "/events/{}".format(account_id)
        return self.client._api_call("get", endpoint)

    def list_for_user(self, user_id: Union[str, UUID]):
        """
        Get a list of Event logs for the specified user_id (really only works if you're said user due to permissions).

        :param user_id: User ID you want to get event logs for.

        Example::

          client.events.list(
            user_id="6bdcb4d9-9a2e-a765-4548-ae6b27a6c024"
          )

        Returns:
            list: List of event logs.
        """
        endpoint = "/events/{}".format(user_id)
        return self.client._api_call("get", endpoint)
