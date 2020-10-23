import os
from frameioclient import FrameioClient, Asset, ClientVersion


token = os.getenv('FRAMEIO_TOKEN')
client = FrameioClient(token)

print(ClientVersion.version())

Asset(token).simple_upload(
    'dd8526ee-2c7d-4b48-9bf7-b847664666bb', 
    '/Users/jeff/Code/python-frameio-client/examples/downloads/accelerated_Test_Chart_5_Sec_embedded_meta_Mezzanine.mxf'
)