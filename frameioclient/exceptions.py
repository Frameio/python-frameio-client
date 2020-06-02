
class PresentationException(Exception):
    """Exception raised when you try to create a Presentation Link for an asset
    that already has one.
    """

    def __init__(
        self, 
        message="Your asset already has a presentation link associated with it."
    ):
        self.message = message
        super().__init__(self.message)
