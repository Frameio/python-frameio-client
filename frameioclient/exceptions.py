
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

class WatermarkIDDownloadException(Exception):
    """Exception raised when trying to download a file where there is no available
    download URL.
    """
    def __init__(
        self, 
        message="This file is unavailable for download due to security and permission settings."
    ):
        self.message = message
        super().__init__(self.message)

class DownloadException(Exception):
    """Exception raised when trying to download a file 
    """
    def __init__(
        self, 
        message="Generic Dowload exception."
    ):
        self.message = message
        super().__init__(self.message)

class AssetNotFullyUploaded(Exception):
    """Exception raised when trying to download a file that isn't yet fully upload.
    """
    def __init__(
        self, 
        message="Unable to download this asset because it not yet fully uploaded."
    ):
        self.message = message
        super().__init__(self.message)
