import xxhash
import sys

KB = 1024
MB = KB * KB

def stream(func, page=1, page_size=20):
    """
    Accepts a lambda of a call to a client list method, and streams the results until
    the list has been exhausted

    :Args:
        fun (function): A 1-arity function to apply during the stream

        Example:: 
            stream(lambda pagination: client.get_collaborators(project_id, **pagination))
    """
    total_pages = page
    while page <= total_pages:
        result_list = func(page=page, page_size=page_size)
        total_pages = result_list.total_pages
        for res in result_list:
            yield res

        page += 1

def format_bytes(size):
    """
    Convert bytes to KB/MB/GB/TB/s
    """
    # 2**10 = 1024
    power = 2**10
    n = 0
    power_labels = {0 : 'B/s', 1: 'KB/s', 2: 'MB/s', 3: 'GB/s', 4: 'TB/s'}

    while size > power:
        size /= power
        n += 1

    return " ".join((str(round(size, 2)), power_labels[n]))

def calculate_hash(file_path):
    """
    Calculate an xx64hash
    """
    xxh64_hash = xxhash.xxh64()
    b = bytearray(MB * 8)
    f = open(file_path, "rb")
    while True:
        numread = f.readinto(b)
        if not numread:
            break
        xxh64_hash.update(b[:numread])
    
    xxh64_digest = xxh64_hash.hexdigest()

    return xxh64_digest

def compare_items(dict1, dict2):
    """
    Python 2 and 3 compatible way of comparing 2x dictionaries
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