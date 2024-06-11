class PresentationException(Exception):
    """Exception raised when you try to create a Presentation Link for an asset
    that already has one.
    """

    def __init__(
        self, message="Your asset already has a presentation link associated with it."
    ):
        self.message = message
        super().__init__(self.message)


class WatermarkIDDownloadException(Exception):
    """Exception raised when trying to download a file where there is no available
    download URL.
    """

    def __init__(
        self,
        message="This file is unavailable for download due to security and permission settings.",
    ):
        self.message = message
        super().__init__(self.message)


class DownloadException(Exception):
    """Exception raised when trying to download a file"""

    def __init__(self, message="Generic Dowload exception."):
        self.message = message
        super().__init__(self.message)


class AssetNotFullyUploaded(Exception):
    """Exception raised when trying to download a file that isn't yet fully upload."""

    def __init__(
        self, message="Unable to download this asset because it not yet fully uploaded."
    ):
        self.message = message
        super().__init__(self.message)


class AssetChecksumNotPresent(Exception):
    """Exception raised when there's no checksum present for the Frame.io asset."""

    def __init__(
        self,
        message="""No checksum found on Frame.io for this asset. This could be because it was uploaded \ 
            before we introduced the feature, the media pipeline failed to process the asset, or the asset has yet to finish being processed.""",
    ):
        self.message = message
        super().__init__(self.message)


class AssetChecksumMismatch(Exception):
    """Exception raised when the checksum for the downloaded file doesn't match what's found on Frame.io."""

    def __init__(
        self,
        message="Checksum mismatch, you should re-download the asset to resolve any corrupt bits.",
    ):
        self.message = message
        super().__init__(self.message)
