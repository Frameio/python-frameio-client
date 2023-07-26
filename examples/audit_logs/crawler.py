import os

from dotenv import load_dotenv
from frameioclient import FrameioClient, Utils

load_dotenv("/Users/jeff/Code/developer-relations/python-frameio-client/.env")

client = FrameioClient(os.getenv("FRAMEIO_TOKEN"))

def get_audit_logs(account_id: str):
    logs = []

    for chunk in Utils.stream_results(
        f"/accounts/{account_id}/audit_logs", client=client
    ):
        logs.append(chunk)

        try:
            print(chunk.keys())
        except Exception as e:
            print(e)

    print(len(logs))

    for log in logs:
        print(log.keys())


if __name__ == "__main__":
    my_account_id = client.me['account_id']
    get_audit_logs(my_account_id)
