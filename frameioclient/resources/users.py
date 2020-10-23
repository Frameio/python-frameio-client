from ..client import FrameioClient

class User(FrameioClient):
    def get_me(self):
        """
        Get the current user.
        """
        return self._api_call('get', '/me')