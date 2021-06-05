class FrameioHelpers(object):
  def get_updated_assets(self, account_id, project_id, timestamp):
    """
    Get assets added or updated since timestamp.

    :Args:
      account_id (string): The account id.
      project_id (string): The project id.
      timestamp (string): ISO 8601 UTC format.
      (datetime.now(timezone.utc).isoformat())
    """
    payload = {
      "account_id": account_id,
      "page": 1,
      "page_size": 50,
      "include": "children",
      "sort": "-inserted_at",
      "filter": {
        "project_id": {
          "op": "eq",
          "value": project_id
        },
        "updated_at": {
          "op": "gte",
          "value": timestamp
        }
      }
    }
    endpoint = '/search/library'
    return self._api_call('post', endpoint, payload=payload)
