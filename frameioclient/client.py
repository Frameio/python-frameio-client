from .upload import FrameioUploader
import requests

class PaginatedResponse(object):
  def __init__(self, results=[], page=0, page_size=0, total=0, total_pages=0):
    super(PaginatedResponse, self).__init__()
    self.results = results
    self.page = int(page)
    self.page_size = int(page_size)
    self.total = int(total)
    self.total_pages = int(total_pages)
  
  def __iter__(self):
    return iter(self.results)

class FrameioClient(object):
  def __init__(self, token, host='https://api.frame.io'):
    self.token = token
    self.host = host

  def _api_call(self, method, endpoint, payload={}):
    url = '{}/v2{}'.format(self.host, endpoint)

    headers = {
      'Authorization': 'Bearer {}'.format(self.token)
    }

    r = requests.request(
      method,
      url,
      json=payload,
      headers=headers,
    )

    if r.ok:
      if r.headers.get('page-number'):
        return PaginatedResponse(
          results=r.json(), 
          page=r.headers['page-number'], 
          page_size=r.headers['per-page'],
          total_pages=r.headers['total-pages'],
          total=r.headers['total']
        )

      return r.json()
    return r.raise_for_status()

  def get_me(self):
    """
    Get the current user.
    """
    return self._api_call('get', '/me')

  def get_teams(self, account_id, **kwargs):
    """
    Get teams owned by the account. 
    (To return all teams, use get_all_teams())
    
    :Args:
      account_id (string): The account id.
    """
    endpoint = '/accounts/{}/teams'.format(account_id)
    return self._api_call('get', endpoint, kwargs)
  
  def get_team(self, team_id):
    """
    Get's a team by id

    :Args:
      team_id (string): the team's id
    """
    endpoint  = '/teams/{}'.format(team_id)
    return self._api_call('get', endpoint)

  def get_all_teams(self, **kwargs):
    """
    Get all teams for the authenticated user.

    :Args:
      account_id (string): The account id.
    """
    endpoint = '/teams'
    return self._api_call('get', endpoint, kwargs)

  def get_projects(self, team_id, **kwargs):
    """
    Get projects owned by the team.

    :Args:
      team_id (string): The team id.
    """
    endpoint = '/teams/{}/projects'.format(team_id)
    return self._api_call('get', endpoint, kwargs)
  
  def get_project(self, project_id):
    """
    Get an individual project

    :Args:
      project_id (string): the project's id
    """
    endpoint = '/projects/{}'.format(project_id)
    return self._api_call('get', endpoint)
  
  def get_collaborators(self, project_id, **kwargs):
    """
    Get collaborators for a project

    :Args:
      project_id (string): the project's id
    """
    endpoint = "/projects/{}/collaborators".format(project_id)
    return self._api_call('get', endpoint, kwargs)

  def get_pending_collaborators(self, project_id, **kwargs):
    """
    Get pending collaborators for a project

    :Args:
      project_id (string): the project's id
    """
    endpoint = "/projects/{}/pending_collaborators".format(project_id)
    return self._api_call('get', endpoint, kwargs)

  def create_project(self, team_id, **kwargs):
    """
    Create a project.

    :Args:
      team_id (string): The team id.
    :Kwargs:
      (optional) kwargs: additional request parameters.

      Example::

        client.create_project(
          team_id="123",
          name="My Awesome Project",
        )
    """
    endpoint = '/teams/{}/projects'.format(team_id)
    return self._api_call('post', endpoint, payload=kwargs)

  def get_project(self, project_id):
    """
    Get a project by id.

    :Args:
      project_id (string): The project id.
    """
    endpoint = '/projects/{}'.format(project_id)
    return self._api_call('get', endpoint)

  def get_asset(self, asset_id):
    """
    Get an asset by id.

    :Args:
      asset_id (string): The asset id.
    """
    endpoint = '/assets/{}'.format(asset_id)
    return self._api_call('get', endpoint)

  def get_asset_children(self, asset_id, **kwargs):
    """
    Get an asset's children.

    :Args:
      asset_id (string): The asset id.
    """
    endpoint = '/assets/{}/children'.format(asset_id)
    return self._api_call('get', endpoint, kwargs)

  def create_asset(self, parent_asset_id, **kwargs):
    """
    Create an asset.

    :Args:
      parent_asset_id (string): The parent asset id.
    :Kwargs:
      (optional) kwargs: additional request parameters.

      Example::

        client.create_asset(
          parent_asset_id="123abc",
          name="ExampleFile.mp4",
          type="file",
          filetype="video/mp4",
          filesize=123456
        )
    """
    endpoint = '/assets/{}/children'.format(parent_asset_id)
    return self._api_call('post', endpoint, payload=kwargs)
  
  def update_asset(self, asset_id, **kwargs):
    """
    Updates an asset

    :Args:
      asset_id (string): the asset's id
    :Kwargs:
      the fields to update

      Example::
        client.update_asset("adeffee123342", name="updated_filename.mp4")
    """
    endpoint = '/assets/{}/children'.format(asset_id)
    return self._api_call('put', endpoint, kwargs)

  def upload(self, asset, file):
    """
    Upload an asset. The method will exit once the file is uploaded.

    :Args:
      asset (object): The asset object.
      file (file): The file to upload.

      Example::

        client.upload(asset, open('example.mp4'))
    """
    uploader = FrameioUploader(asset, file)
    uploader.upload()

  def get_comments(self, asset_id, **kwargs):
    """
    Get an asset's comments.

    :Args:
      asset_id (string): The asset id.
    """
    endpoint = '/assets/{}/comments'.format(asset_id)
    return self._api_call('get', endpoint, **kwargs)

  def create_comment(self, asset_id, **kwargs):
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
    return self._api_call('post', endpoint, payload=kwargs)

  def update_comment(self, comment_id, **kwargs):
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
    return self._api_call('post', endpoint, payload=kwargs)

  def delete_comment(self, comment_id):
    """
    Delete a comment.

    :Args:
      comment_id (string): The comment id.
    """
    endpoint = '/comments/{}'.format(comment_id)
    return self._api_call('delete', endpoint)

  def get_review_links(self, project_id):
    """
    Get the review links of a project

    :Args:
      asset_id (string): The asset id.
    """
    endpoint = '/projects/{}/review_links'.format(project_id)
    return self._api_call('get', endpoint)

  def create_review_link(self, project_id, **kwargs):
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
    return self._api_call('post', endpoint, payload=kwargs)

  def get_review_link(self, link_id, **kwargs):
    """
    Get a single review link

    :Args:
      link_id (string): The review link id.
    """
    endpoint = '/review_links/{}'.format(link_id)
    return self._api_call('get', endpoint, payload=kwargs)

  def update_review_link_assets(self, link_id, **kwargs):
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
    return self._api_call('post', endpoint, payload=kwargs)

  def get_review_link_items(self, link_id):
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
    return self._api_call('get', endpoint)
