try:
    from importlib import metadata
except ImportError:
    # Running on pre-3.8 Python; use importlib-metadata package
    import importlib_metadata as metadata


class ClientVersion:
    @staticmethod
    def version():
        return metadata.version("frameioclient")
