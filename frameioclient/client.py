from .upload import FrameioUploader
import requests

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
      return r.json()
    return r.raise_for_status()

  def get_me(self):
    """
    Get the current user.
    """
    return self._api_call('get', '/me')

  def get_teams(self, account_id):
    """
    Get teams owned by the account.

    :Args:
      account_id (string): The account id.
    """
    endpoint = '/accounts/{}/teams'.format(account_id)
    return self._api_call('get', endpoint)
  
  def get_projects(self, team_id):
    """
    Get projects owned by the team.

    :Args:
      team_id (string): The team id.
    """
    endpoint = '/teams/{}/projects'.format(team_id)
    return self._api_call('get', endpoint)
  
  def create_project(self, **kwargs):
    """
    Create a project.

    :Kwargs:
      (optional) kwargs: additional request parameters.

      Example::

        client.create_project(
          team_id="123",
          name="My Awesome Project",
        )
    """
    return self._api_call('post', '/projects', payload=kwargs)
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
  
  def get_asset_children(self, asset_id):
    """
    Get an assets children.

    :Args:
      asset_id (string): The asset id.
    """
    endpoint = '/assets/{}/children'.format(asset_id)
    return self._api_call('get', endpoint)

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
