import enum
import os
import re
import sys
from typing import Any, Dict, Generator, Optional

import xxhash
from furl import furl

KB = 1024
MB = KB * KB
ENV = os.getenv("FRAMEIO_ENVIRONMENT", "prod")


def ApiReference(*args, **kwargs):
    def inner(func):
        """
        do operations with func
        """
        if ENV == "build":
            print("API Operation: {}".format(kwargs.get("operation")))

        return func

    return inner


class FormatTypes(enum.Enum):
    SPEED = 0
    SIZE = 1


class Utils:
    @staticmethod
    def stream(func, page=1, page_size=50):
        """
        Accepts a lambda of a call to a client list method, and streams the results until \
        the list has been exhausted.

        Args:
            fun (function): A 1-arity function to apply during the stream

        Example::
        
            stream(lambda pagination: client.get_collaborators(project_id, **pagination))
        """
        total_pages = page
        while page <= total_pages:
            result_list = func(page=page, page_size=page_size)
            if type(result_list) == PaginatedResponse:
                total_pages = result_list.total_pages
                for res in result_list:
                    yield res
            else:
                yield res

            page += 1

    @staticmethod
    def stream_results(
        endpoint, page=1, page_size=50, client=None, **_kwargs
    ) -> Generator:
        def fetch_page(page=1, page_size=50):
            return client._api_call(
                "get", furl(endpoint).add({"page": page, "page_size": page_size}).url
            )

        for result in Utils.stream(fetch_page, page=page, page_size=page_size):
            yield result

    @staticmethod
    def format_value(value: int, type: FormatTypes = FormatTypes.SIZE) -> str:
        """
        Convert bytes to KB/MB/GB/TB/s

        :param value: a numeric value
        :param type: the FormatType specified
        """
        # 2**10 = 1024
        power = 2 ** 10
        n = 0
        power_labels = {0: "B", 1: "KB", 2: "MB", 3: "GB", 4: "TB"}

        while value > power:
            value /= power
            n += 1

        formatted = " ".join((str(round(value, 2)), power_labels[n]))

        if type == FormatTypes.SPEED:
            return formatted + "/s"

        elif type == FormatTypes.SIZE:
            return formatted

    @staticmethod
    def calculate_hash(file_path: str, progress_callback: Optional[Any] = None):
        """
        Calculate an xx64hash

        :param file_path: The path on your system to the file you'd like to checksum
        :param progress_callback: A progress callback to use when you want to callback w/ progress
        """
        xxh64_hash = xxhash.xxh64()
        b = bytearray(MB * 8)
        f = open(file_path, "rb")
        while True:
            numread = f.readinto(b)
            if not numread:
                break

            xxh64_hash.update(b[:numread])

            if progress_callback:
                # Should only subtract 1 here when necessary, not every time!
                progress_callback(float(numread - 1), force=True)

        xxh64_digest = xxh64_hash.hexdigest()

        return xxh64_digest

    @staticmethod
    def compare_items(dict1: Dict, dict2: Dict) -> bool:
        """
        Python 2 and 3 compatible way of comparing 2x dictionaries

        :param dict1: Dictionary 1 for comparison
        :param dict2: Dictionary 2 for comparison
        """
        comparison = None

        if sys.version_info.major >= 3:
            import operator

            comparison = operator.eq(dict1, dict2)

        else:
            if dict1 == dict2:
                comparison = True

        if comparison == False:
            print("File mismatch between upload and download")

        return comparison

    @staticmethod
    def get_valid_filename(s: str) -> str:
        """
        Strip out invalid characters from a filename using regex

        :param s: Filename to remove invalid characters from
        """
        s = str(s).strip().replace(" ", "_")
        return re.sub(r"(?u)[^-\w.]", "", s)

    @staticmethod
    def normalize_filename(fn: str) -> str:
        """
        Normalize filename using pure python

        :param fn: Filename to normalize using pure python
        """
        validchars = "-_.() "
        out = ""

        if isinstance(fn, str):
            pass
        elif isinstance(fn, unicode):
            fn = str(fn.decode("utf-8", "ignore"))
        else:
            pass

        for c in fn:
            if str.isalpha(c) or str.isdigit(c) or (c in validchars):
                out += c
            else:
                out += "_"
        return out

    @staticmethod
    def format_headers(token: str, version: str) -> Dict:
        """[summary]

        :param token: Frame.io OAuth/Dev Token to use
        :param version: The version of the frameioclient sdk to add to our HTTP header
        """
        return {
            "Authorization": f"Bearer {token}",
            "x-frameio-client": f"python/{version}",
        }


class PaginatedResponse(object):
    def __init__(
        self,
        results=[],
        limit=None,
        page_size=0,
        total=0,
        total_pages=0,
        endpoint=None,
        method=None,
        payload={},
        client=None,
    ):
        self.results = results

        self.limit = limit
        self.page_size = int(page_size)
        self.total = int(total)
        self.total_pages = int(total_pages)

        self.endpoint = endpoint
        self.method = method
        self.payload = payload
        self.client = client

        self.asset_index = 0  # Index on current page
        self.returned = 0  # Total returned count
        self.current_page = 1

    def __iter__(self):
        return self

    def __next__(self):
        # Reset if we've reached end
        if self.returned == self.limit or self.returned == self.total:
            self.asset_index = 0
            self.returned = 0
            self.current_page = 1

            self.results = self.client.get_specific_page(
                self.method, self.endpoint, self.payload, page=1
            ).results
            raise StopIteration

        if self.limit is None or self.returned < self.limit:
            if self.asset_index < self.page_size and self.returned < self.total:
                self.asset_index += 1
                self.returned += 1
                return self.results[self.asset_index - 1]
                raise StopIteration

            if self.current_page < self.total_pages:
                self.current_page += 1
                self.asset_index = 1
                self.returned += 1

                self.results = self.client.get_specific_page(
                    self.method, self.endpoint, self.payload, self.current_page
                ).results

                return self.results[self.asset_index - 1]
            raise StopIteration

        raise StopIteration

    def next(self):  # Python 2
        return self.__next__()

    def __len__(self):
        if self.limit and self.limit < self.total:
            return self.limit

        return self.total


class ProgressBar(object):
    def __init__(self, parent=None, total=0, iterable=[]):
        self.parent = parent
        self.total = total
        self.iterable = iterable

    def create(self):
        pass

    def update(self):
        pass
