from typing import Union
from uuid import UUID

from ..lib.service import Service


class AuditLogs(Service):
    def list(self, account_id: Union[str, UUID]):
        """
        Get audit logs for the currently authenticated account.

        :param account_id: Account ID you want to get audit logs for.

        Example::

          client.logs.list(
            account_id="6bdcb4d9-9a2e-a765-4548-ae6b27a6c024"
          )

        Returns:
            list: List of audit logs.
        """
        endpoint = "/accounts/{}/audit_logs".format(account_id)
        return self.client._api_call("get", endpoint)
