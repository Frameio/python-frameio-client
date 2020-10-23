import warnings
from .service import Service

class Team(Service):
  def create(self, account_id, **kwargs):
    """
    Create a Team.

    :Args:
      account_id (string): The account id you want to create this Team under.
    :Kwargs:
      (optional) kwargs: additional request parameters.

      Example::

        client.create_team(
          account_id="6bdcb4d9-4548-4548-4548-27a6c024ae6b",
          name="My Awesome Project",
        )
    """
    warnings.warn('Note: Your token must support team.create scopes')
    endpoint = '/accounts/{}/teams'.format(account_id)
    return self.client._api_call('post', endpoint, payload=kwargs)

  def list(self, account_id, **kwargs):
    """
    Get teams owned by the account. 
    (To return all teams, use get_all_teams())
    
    :Args:
      account_id (string): The account id.
    """
    endpoint = '/accounts/{}/teams'.format(account_id)
    return self.client._api_call('get', endpoint, kwargs)
  
  def list_all(self, **kwargs):
    """
    Get all teams for the authenticated user.

    :Args:
      account_id (string): The account id.
    """
    endpoint = '/teams'
    return self.client._api_call('get', endpoint, kwargs)

  def get(self, team_id):
    """
    Get's a team by id

    :Args:
      team_id (string): the team's id
    """
    endpoint  = '/teams/{}'.format(team_id)
    return self.client._api_call('get', endpoint)

  def get_members(self, team_id):
    """
    Get the member list for a given team_id.

    :Args:
      team_id (string): The team id.
    """
    endpoint = '/teams/{}/members'.format(team_id)
    return self.client._api_call('get', endpoint)  

  def list_projects(self, team_id, **kwargs):
    """
    Get projects owned by the team.

    :Args:
      team_id (string): The team id.
    """
    endpoint = '/teams/{}/projects'.format(team_id)
    return self.client._api_call('get', endpoint, kwargs)
