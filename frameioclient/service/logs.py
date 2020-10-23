from .service import Service

class AuditLogs(Service):
  def list(self, account_id):
    """
    Get audit logs for the currently authenticated account.

    :Args:

      Example::

        client.get_audit_logs(
          account_id="6bdcb4d9-9a2e-a765-4548-ae6b27a6c024"
        )
    """
    endpoint = '/accounts/{}/audit_logs'.format(account_id)
    return self.client._api_call('get', endpoint)
