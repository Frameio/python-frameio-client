import os
import math
import time
import enlighten
import requests
import concurrent.futures

from .utils import Utils
from .telemetry import Event
from .logger import SDKLogger

from .exceptions import (
    DownloadException,
    AssetChecksumMismatch,
    AssetChecksumNotPresent,
)

from .bandwidth import NetworkBandwidth, DiskBandwidth
from .transport import HTTPClient


class AWSClient(HTTPClient, object):
    def __init__(self, concurrency=None, progress=True):
        super().__init__()  # Initialize via inheritance
        self.progress = progress
        self.progress_manager = None
        self.destination = None
        self.request_logs = []

        # Ensure this is a valid number before assigning
        if concurrency is not None and type(concurrency) == int and concurrency > 0:
            self.concurrency = concurrency
        else:
            self.concurrency = self._optimize_concurrency()

        if self.progress:
            self.progress_manager = enlighten.get_manager()

    @staticmethod
    def check_cdn(url):
        # TODO improve this algo
        if "assets.frame.io" in url:
            return "Cloudfront"
        elif "s3" in url:
            return "S3"
        else:
            return None

    def _create_file_stub(self):
        try:
            fp = open(self.destination, "w")
            # fp.write(b"\0" * self.file_size) # Disabled to prevent pre-allocatation of disk space
            fp.close()
        except FileExistsError as e:
            if self.replace == True:
                os.remove(self.destination)  # Remove the file
                self._create_file_stub()  # Create a new stub
            else:
                print(e)
                raise e
        except TypeError as e:
            print(e)
            raise e
        return True

    def _optimize_concurrency(self):
        """
        This method looks as the net_stats and disk_stats that we've run on \
            the current environment in order to suggest the best optimized \
            number of concurrent TCP connections.

        Example::
            AWSClient._optimize_concurrency()
        """

        net_stats = NetworkBandwidth
        disk_stats = DiskBandwidth

        # Algorithm ensues
        #
        #

        return 5

    def _get_byte_range(self, url, start_byte=0, end_byte=2048):
        """
        Get a specific byte range from a given URL. This is **not** optimized \
            for heavily-threaded operations currently.

        :Args:
            url (string): The URL you want to fetch a byte-range from
            start_byte (int): The first byte you want to request
            end_byte (int): The last byte you want to extract

        Example::
            AWSClient().get_byte_range(asset, "~./Downloads")
        """

        range_header = {"Range": "bytes=%d-%d" % (start_byte, end_byte)}

        headers = {**self.shared_headers, **range_header}

        br = requests.get(url, headers=headers).content
        return br

    def _download_whole(self, url):
        start_time = time.time()
        print(
            "Beginning download -- {} -- {}".format(
                self.asset["name"], Utils.format_bytes(self.file_size, type="size")
            )
        )

        # Downloading
        r = self.session.get(url, stream=True)

        # Downloading
        with open(self.destination, "wb") as handle:
            try:
                # TODO make sure this approach works for SBWM download
                for chunk in r.iter_content(chunk_size=4096):
                    if chunk:
                        handle.write(chunk)
            except requests.exceptions.ChunkedEncodingError as e:
                raise e

        download_time = time.time() - start_time
        download_speed = Utils.format_bytes(math.ceil(self.file_size / (download_time)))
        print(
            "Downloaded {} at {}".format(
                Utils.format_bytes(self.file_size, type="size"), download_speed
            )
        )

        return self.destination, download_speed

    def _download_chunk(self, task):
        # Download a particular chunk
        # Called by the threadpool executor

        # Destructure the task object into its parts
        url = task[0]
        start_byte = task[1]
        end_byte = task[2]

        # Set the initial chunk_size, but prepare to overwrite
        chunk_size = end_byte - start_byte

        if self.bytes_started + (chunk_size) > self.file_size:
            difference = abs(
                self.file_size - (self.bytes_started + chunk_size)
            ) # should be negative
            chunk_size = chunk_size - difference
            print(f"Chunk size as done via math: {chunk_size}")
        else:
            pass

        # Set chunk size in a smarter way
        self.bytes_started += chunk_size

        # Specify the start and end of the range request
        headers = {"Range": "bytes=%d-%d" % (start_byte, end_byte)}

        # Grab the data as a stream
        r = self.session.get(url, headers=headers, stream=True)

        # Write the file to disk
        with open(self.destination, "r+b") as fp:
            fp.seek(start_byte)  # Seek to the right spot in the file
            chunk_size = len(r.content)  # Get the final chunk size
            fp.write(r.content)  # Write the data

        # Save requests logs
        self.request_logs.append(
            {
                "headers": r.headers,
                "http_status": r.status_code,
                "bytes_transferred": len(r.content),
            }
        )

        # Increase the count for bytes_completed, but only if it doesn't overrun file length
        self.bytes_completed += chunk_size
        if self.bytes_completed > self.file_size:
            self.bytes_completed = self.file_size

        # After the function completes, we report back the # of bytes transferred
        return chunk_size

    def multi_thread_download(self, url):
        start_time = time.time()

        # Generate stub
        try:
            self._create_file_stub()
        except Exception as e:
            raise DownloadException(message=e)

        offset = math.ceil(self.file_size / self.chunks)
        in_byte = 0  # Set initially here, but then override

        SDKLogger("downloads").info(
            "Multi-part download -- {} -- {}".format(
                self.asset["name"], Utils.format_bytes(self.file_size, type="size")
            )
        )

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.aws_client.concurrency
        ) as executor:
            for i in range(int(self.chunks)):
                out_byte = offset * (i + 1) # Increment by the iterable + 1 so we don't mutiply by zero
                task = (url, in_byte, out_byte, i) # Create task tuple
                if i < self.aws_client.concurrency: # Stagger start for each chunk by 0.1 seconds
                    time.sleep(0.1)
                self.futures.append(executor.submit(self._download_chunk, task)) # Append tasks to futures list
                in_byte = out_byte # Reset new in byte equal to last out byte

            for future in concurrent.futures.as_completed(self.futures):
                try:
                    chunk_size = future.result()
                except Exception as exc:
                    print(exc)

            # Calculate and print stats
            download_time = round((time.time() - start_time), 2)
            download_speed = round((self.file_size / download_time), 2)

            if self.checksum_verification == True:
                # Check for checksum, if not present throw error
                if self._get_checksum() == None:
                    raise AssetChecksumNotPresent

                # Calculate the file hash
                if (
                    Utils.calculate_hash(
                        self.destination
                    )
                    != self.original_checksum
                ):
                    raise AssetChecksumMismatch

            # Log completion event
            SDKLogger("downloads").info(
                "Downloaded {} at {}".format(
                    Utils.format_bytes(self.file_size, type="size"), download_speed
                )
            )

            # Submit telemetry
            transfer_stats = {
                "speed": download_speed,
                "time": download_time,
                "cdn": AWSClient.check_cdn(url),
            }

            Event(self.user_id, 'python-sdk-download-stats', transfer_stats)

            # If stats = True, we return a dict with way more info, otherwise \
            if self.stats:
                # We end by returning a dict with info about the download
                dl_info = {
                    "destination": self.destination,
                    "speed": download_speed,
                    "elapsed": download_time,
                    "cdn": AWSClient.check_cdn(url),
                    "concurrency": self.aws_client.concurrency,
                    "size": self.file_size,
                    "chunks": self.chunks,
                }
                return dl_info
            else:
                return self.destination

class TransferJob(AWSClient):
    # These will be used to track the job and then push telemetry
    def __init__(self, job_info):
        self.job_info = job_info  # < - convert to JobInfo class
        self.cdn = "S3"  # or 'CF' - use check_cdn to confirm
        self.progress_manager = None


class DownloadJob(TransferJob):
    def __init__(self):
        self.asset_type = "review_link"  # we should use a dataclass here
        # Need to create a re-usable job schema
        # Think URL -> output_path
        pass


class UploadJob(TransferJob):
    def __init__(self, destination):
        self.destination = destination
        # Need to create a re-usable job schema
        # Think local_file path and remote Frame.io destination
        pass
