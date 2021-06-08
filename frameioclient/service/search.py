from .service import Service

class Search(Service):
  def library(self, query, type=None, project_id=None, account_id=None, team_id=None, uploader=None, sort=None, filter=None, page_size=10, page=1):
    """
    Search for assets using the library search endpoint, documented here \
        https://developer.frame.io/docs/workflows-assets/search-for-assets.
    
    For more information check out https://developer.frame.io/api/reference/operation/assetSearchPost/.

    :Args:
        query (string): The search keyword you want to search with.
        account_id (string): The account ID you want to be searching within. #TODO, confirm that this is required or not, could we use self.me?

    :Kwargs:
        type (string): The type of frame.io asset you want to search: [file, folder, review_link, presentation].
        project_id (uuid): The frame.io project you want to constrain your search to.
        account_id (uuid): The frame.io account want you to contrain your search to (you may only have one, but some users have 20+ that they have acces to).
        team_id (uuid): The frame.io team you want to constrain your search to.
        uploader (string): The name of the uploader, this includes first + last name with a space.
        sort (string): The field you want to sort by.
        filter (string): This is only necessary if you want to build a fully custom query, the most common functionality is exposed using other kwargs though.
        page_size (int): Useful if you want to increase the number of items returned by the search API here.
        page (int): The page of results you're requesting.

        Example::
            client.assets.search(
                query="Final",
                type="file",
                sort="name",
                
            )
    """

    # Define base payload
    payload = {
        "account_id": account_id,
        "q": query,
        "sort": sort,
        "page_size": page_size,
        "page": page
    }

    # Add fully custom filter
    if filter is not None:
        payload['filter'] = filter

    # Add simple filters
    if project_id is not None:
        payload['filter']['project_id'] = {
            "op": "eq",
            "value": project_id
        }
    if team_id is not None:
        payload['filter']['team_id'] = {
            "op": "eq",
            "value": team_id
        }
    if type is not None:
        payload['filter']['type'] = {
            "op": "eq",
            "value": type
        }
    if uploader is not None:
        payload['filter']['creator.name'] = {
            "op": "match",
            "value": uploader
        }

    # Add sorting
    if sort is not None:
        payload['sort'] = sort

    endpoint = '/search/assets'
    return self.client._api_call('post', endpoint, payload=payload)
