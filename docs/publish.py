import os
import frontmatter
import contentful_management

token = os.getenv("CONTENTFUL_TOKEN")
docs_path = "./_build/jekyll/api"



def grab_docs(directory):
    docs_data = list()
    files = os.listdir(directory)
    for fn in files:
        fpath = os.path.join(directory, fn)
        with open(fpath) as f:
            post = frontmatter.load(f)
        docs_data.append(post)

    return docs_data


def get_published_docs():
    client = contentful_management.Client(token)
    pass


def update_doc():
    pass


def publish_new_docs():
    pass


def main():
    # Grab the old docs
    old_docs = get_published_docs()

    # Grab the new docs
    new_docs = grab_docs(docs_path)

    # Iterate over the new docs and if 
    for doc in docs:
        # print(doc.content)
        print(doc.keys())


if __name__ == "__main__":
    publish_latest()