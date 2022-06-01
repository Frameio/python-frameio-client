import os
import json
from pprint import pprint
import time
from typing import Optional
from dotenv import find_dotenv, load_dotenv
from frontmatter import load
from frameioclient import FrameioClient, Utils

# load_dotenv(find_dotenv())
load_dotenv('/Users/jeff/Code/developer-relations/python-frameio-client/.env')
token = os.getenv("FRAMEIO_TOKEN")

def get_audit_logs(account_id: str, event_type: Optional[str] = None):
    logs = list()

    start_time = time.time()
    client = FrameioClient(token)
    endpoint = f"/accounts/{account_id}/audit_logs"

    if event_type != None:
        endpoint += f'?filter[action]={event_type}'

    for log_page in Utils.stream_results(endpoint, client=client):
        logs.append(log_page)
        print(f"{len(logs)} logs fetched")

    # Write the file
    with open("audit_logs.json", "w") as out_file:
        json.dump(logs, out_file)

    duration = time.time() - start_time
    
    print(f"Took {duration} seconds to complete.")

if __name__ == "__main__":
    account_id = 'f6365640-575c-42e5-8a7f-cd9e2d6b9273'
    get_audit_logs(account_id, 'AssetCreated')


