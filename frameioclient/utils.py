import xxhash
import sys
import re

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

def format_bytes(size, type="speed"):
    """
    Convert bytes to KB/MB/GB/TB/s
    """
    # 2**10 = 1024
    power = 2**10
    n = 0
    power_labels = {0 : 'B', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}

    while size > power:
        size /= power
        n += 1

    formatted = " ".join((str(round(size, 2)), power_labels[n]))

    if type == "speed":
        return formatted + "/s"
        
    elif type == "size":
        return formatted

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

def get_valid_filename(s):
    """
    Strip out invalid characters from a filename using regex
    """
    s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)

def normalize_filename(fn):
    """
    Normalize filename using pure python
    """
    validchars = "-_.() "
    out = ""

    if isinstance(fn, str):
        pass
    elif isinstance(fn, unicode):
        fn = str(fn.decode('utf-8', 'ignore'))
    else:
        pass

    for c in fn:
      if str.isalpha(c) or str.isdigit(c) or (c in validchars):
        out += c
      else:
        out += "_"
    return out
