import os
import sys
import argparse

from frameioclient import FrameioClient


def main():
    parser = argparse.ArgumentParser(
        prog="fiocli", description="Frame.io Python SDK CLI"
    )

    ## Define args
    parser.add_argument(
        "--token",
        action="store",
        metavar="token",
        type=str,
        nargs="+",
        help="Developer Token",
    )
    parser.add_argument(
        "--target",
        action="store",
        metavar="target",
        type=str,
        nargs="+",
        help="Target: remote project or folder, or alternatively a local file/folder",
    )
    parser.add_argument(
        "--destination",
        action="store",
        metavar="destination",
        type=str,
        nargs="+",
        help="Destination: remote project or folder, or alternatively a local file/folder",
    )
    parser.add_argument(
        "--threads",
        action="store",
        metavar="threads",
        type=int,
        nargs="+",
        help="Number of threads to use",
    )

    ## Parse args
    args = parser.parse_args()

    if args.threads:
        threads = args.threads[0]
    else:
        threads = 5

    ## Handle args
    if args.token:
        client = None
        # print(args.token)
        try:
            client = FrameioClient(args.token[0], progress=True, threads=threads)
        except Exception as e:
            print("Failed")
            print(e)
            sys.exit(1)

        # If args.op == 'upload':
        if args.target:
            if args.destination:
                # Check to see if this is a local target and thus a download
                if os.path.isdir(args.destination[0]):
                    try:
                        asset = client.assets.get(args.target[0])
                        return client.assets.download(
                            asset, args.destination[0], progress=True, multi_part=True
                        )
                    except Exception as e:
                        print(e)
                        client.projects.download(args.target[0], args.destination[0])

                else:  # This is an upload
                    if os.path.isdir(args.target[0]):
                        return client.assets.upload_folder(
                            args.target[0], args.destination[0]
                        )
                    else:
                        return client.assets.upload(args.destination[0], args.target[0])
            else:
                print("No destination supplied")
        else:
            print("No target supplied")
