from typing import Optional, Union
from uuid import UUID

from ..lib.service import Service


class Search(Service):
    def library(
        self,
        query: str,
        type: Optional[str] = None,
        project_id: Union[str, UUID] = None,
        account_id: Union[str, UUID] = None,
        team_id: Union[str, UUID] = None,
        uploader: Optional[str] = None,
        sort: Optional[str] = None,
        filter: Optional[str] = None,
        page_size: Optional[int] = 10,
        page: Optional[int] = 1,
    ):
        """
        Search for assets using the library search endpoint, documented at https://developer.frame.io/docs/workflows-assets/search-for-assets.
        For more information check out https://developer.frame.io/api/reference/operation/librarySearchPost/.

        :param query: The search keyword you want to search with.
        :param account_id: The frame.io account want you to contrain your search to (you may only have one, but some users have 20+ that they have acces to).
        :param type: The type of frame.io asset you want to search: [file, folder, review_link, presentation].
        :param project_id: The frame.io project you want to constrain your search to.
        :param team_id: The frame.io team you want to constrain your search to.
        :param uploader: The name of the uploader, this includes first + last name with a space.
        :param sort: The field you want to sort by.
        :param filter: This is only necessary if you want to build a fully custom query, the most common functionality is exposed using other kwargs though.
        :param page_size: Useful if you want to increase the number of items returned by the search API here.
        :param page: The page of results you're requesting.

        Example::

            client.search.library(
                query="Final",
                type="file",
                sort="name"
            )
        """

        # Define base payload
        payload = {
            "account_id": account_id,
            "q": query,
            "sort": sort,
            "page_size": page_size,
            "page": page,
        }

        # Add fully custom filter
        if filter is not None:
            payload["filter"] = filter

        # Add simple filters
        if project_id is not None:
            payload["filter"]["project_id"] = {"op": "eq", "value": project_id}
        if team_id is not None:
            payload["filter"]["team_id"] = {"op": "eq", "value": team_id}
        if type is not None:
            payload["filter"]["type"] = {"op": "eq", "value": type}
        if uploader is not None:
            payload["filter"]["creator.name"] = {"op": "match", "value": uploader}

        # Add sorting
        if sort is not None:
            payload["sort"] = sort

        endpoint = "/search/library"
        return self.client._api_call("post", endpoint, payload=payload)

    def users(self, account_id: str, query: str):
        """Search for users within a given account

        Args:
            account_id (str): UUID for the account you want to search within, must be one you have access to
            query (str): The query string you want to seach with, usually an email or a name

        Returns:
            List[Dict]: List of user resources found via your search  
        """
 
        endpoint = "/search/users"
        payload = {
            "account_id": account_id,
            "q": query
        }
        return self.client._api_call("post", endpoint, payload=payload)
