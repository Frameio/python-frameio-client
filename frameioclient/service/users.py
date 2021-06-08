from .service import Service

class User(Service):
    def get_me(self):
        """
        Get the current user.
        """
        return self.client._api_call('get', '/me')