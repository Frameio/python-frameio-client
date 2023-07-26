import warnings
from ..lib.service import Service


class Team(Service):
    def create(self, account_id, **kwargs):
        """
        Create a Team

        Args:
          account_id (string): The account id you want to create this team under.

        :Keyword Arguments::
          (optional) kwargs: additional request parameters.

        Example::

          client.teams.create(
            account_id="6bdcb4d9-4548-4548-4548-27a6c024ae6b",
            name="My Awesome Project",
          )
        """
        warnings.warn("Note: Your token must support the team.create scope")
        endpoint = "/accounts/{}/teams".format(account_id)
        return self.client._api_call("post", endpoint, payload=kwargs)

    def list(self, account_id, **kwargs):
        """
        Get teams owned by the specified account. \
          (To return all teams, use list_all())
        
        Args:
          account_id (string): The account id.
        """
        endpoint = "/accounts/{}/teams".format(account_id)
        return self.client._api_call("get", endpoint, kwargs)

    def list_all(self, **kwargs):
        """
        Get all teams for the authenticated user.

        Args:
          account_id (string): The account id.
        """
        endpoint = "/teams"
        return self.client._api_call("get", endpoint, kwargs)

    def get(self, team_id):
        """
        Get team by id

        Args:
          team_id (string): the team's id
        """
        endpoint = "/teams/{}".format(team_id)
        return self.client._api_call("get", endpoint)

    def get_members(self, team_id):
        """
        Get the member list for a given team.

        Args:
          team_id (string): The team id.
        """
        endpoint = "/teams/{}/members".format(team_id)
        return self.client._api_call("get", endpoint)

    def list_projects(self, team_id, **kwargs):
        """
        Get projects owned by the team.

        Args:
          team_id (string): The team id.
        """
        endpoint = "/teams/{}/projects".format(team_id)
        return self.client._api_call("get", endpoint, kwargs)

    def add_members(self, team_id, emails):
        """
        Add a list of users via their e-mail address to a given team.

        Args:
            team_id (string): The team id.
            emails (list): The e-mails you want to add.
        """
        payload = dict()
        payload["batch"] = list(map(lambda email: {"email": email}, emails))

        endpoint = "/batch/teams/{}/members".format(team_id)
        return self.client._api_call("post", endpoint, payload=payload)

    def remove_members(self, team_id, emails):
        """
        Remove a list of users via their e-mail address from a given team.

        Args:
            team_id (string): The team id.
            emails (list): The e-mails you want to add.
        """

        # TODO: Implement pagination here since the batch size is 20?

        payload = dict()
        payload["batch"] = list(map(lambda email: {"email": email}, emails))

        endpoint = "/batch/teams/{}/members".format(team_id)
        return self.client._api_call("delete", endpoint, payload=payload)
