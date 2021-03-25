from .service import Service

class Project(Service):
  def create(self, team_id, **kwargs):
    """
    Create a project.

    :Args:
      team_id (string): The team id.
    :Kwargs:
      (optional) kwargs: additional request parameters.

      Example::

        client.projects.create_project(
          team_id="123",
          name="My Awesome Project",
        )
    """
    endpoint = '/teams/{}/projects'.format(team_id)
    return self.client._api_call('post', endpoint, payload=kwargs)

  def get_project(self, project_id):
    """
    Get an individual project

    :Args:
      project_id (string): the project's id
    """
    endpoint = '/projects/{}'.format(project_id)
    return self.client._api_call('get', endpoint)
  
  def get_collaborators(self, project_id, **kwargs):
    """
    Get collaborators for a project

    :Args:
      project_id (string): the project's id
    """
    endpoint = "/projects/{}/collaborators?include=project_role".format(project_id)
    return self.client._api_call('get', endpoint, kwargs)

  def get_pending_collaborators(self, project_id, **kwargs):
    """
    Get pending collaborators for a project

    :Args:
      project_id (string): the project's id
    """
    endpoint = "/projects/{}/pending_collaborators".format(project_id)
    return self.client._api_call('get', endpoint, kwargs)
