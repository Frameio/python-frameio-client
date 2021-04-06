import speedtest
import sys, time, io, requests


def speed_test(size=1024, ipv="ipv4", port=80):
    if size == 1024:
        size = "1GB"
    else:
        size = f"{size}MB"

    url = f"http://{ipv}.download.thinkbroadband.com:{port}/{size}.zip"

    with io.BytesIO() as f:
        start = time.time()
        r = requests.get(url, stream=True)
        total_length = r.headers.get('content-length')
        dl = 0
        if total_length is None: # no content length header
            f.write(r.content)
        else:
            for chunk in r.iter_content(1024 * 8):
                dl += len(chunk)
                f.write(chunk)
                done = int(30 * dl / int(total_length))
                sys.stdout.write("\r[%s%s] %s Mib/s" % ('=' * done, ' ' * (30-done), dl//(time.time() - start) / 100000))
        f.seek(0)

        with open('dump.mp4', 'wb') as outfile:
            outfile.write(f.read())

    print( f"\n{total_length} = {(time.time() - start):.2f} seconds")

def check_speed_with_speedtest():
    st = speedtest.Speedtest()
    print(f'1) Download Speed: {round(st.download(threads=10) * (1.192 * 10 ** -7), 2)} MB/s')
    print(f'2) Upload speed: {round(st.upload(threads=10) * (1.192 * 10 ** -7), 2)} MB/s')
    servernames = []
    st.get_servers(servernames)
    print(f'3) Ping: {st.results.ping} ms')

check_speed_with_speedtest()
