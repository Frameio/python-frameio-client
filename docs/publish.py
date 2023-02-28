import os
import hashlib
import frontmatter
import contentful_management

TOKEN = os.getenv("CONTENTFUL_TOKEN")
SPACE_ID = os.getenv("CONTENTFUL_SPACE_ID")
SDK_ID = os.getenv("CONTENTFUL_SDK_ID")

docs_path = "./dist/jekyll/api"


def transform_path(path):
    # The paths generated automatically need modifying.
    # This function should be localized to each SDK.

    if path == '/api-frameioclient':
        new_path = 'package'
    else:
        new_path = path.split('/api-frameioclient-')[1].lower()
    
    return new_path


def transform_title(docname):
    if docname == 'api/frameioclient':
        new_title = 'Frame.io Python SDK'
    else:
        print(docname)
        new_title = docname.split('.')[1].title()

    return new_title


def load_local(directory):
    # Load in the local docs
    docs_data = list()
    files = os.listdir(directory)
    for fn in files:
        fpath = os.path.join(directory, fn)
        with open(fpath) as f:
            post = frontmatter.load(f)
            post['path'] = transform_path(post['path'])
            post['title'] = transform_title(post['docname'])
        docs_data.append(post)

    return docs_data


def load_remote():
    # Create the client
    client = contentful_management.Client(TOKEN)

    # Grab all the autoDocs
    autoDoc = client.content_types(SPACE_ID, 'master').find('autoDoc')
    entries = autoDoc.entries().all()

    # Filter out the ones that aren't the right programming language
    relevant_docs = list()
    for entry in entries:
        # entry = autoDoc.entries().find(entry.id)
        entry.sys['locale'] = 'en-US'
        sdk = entry.programming_language.id
        if sdk == SDK_ID:
            relevant_docs.append(entry)

    return relevant_docs


def hash_content(content):
    # Returns an SHA-256 hash of the stringified content provided
    hash_object = hashlib.sha256(bytes(content, 'utf-8'))
    sha256 = hash_object.hexdigest()
    return sha256


def update_doc():
    pass


def publish_new_docs(docs, publish=False):
    client = contentful_management.Client(TOKEN)

    for new_entry in docs:
        entry_attributes = {
            'content_type_id': 'autoDoc',
            'fields': {
                'title': {
                    'en-US': new_entry['title']
                },
                'slug': {
                    'en-US': new_entry['slug']
                },
                'content': {
                    'en-US': new_entry['content']
                },
                'programmingLanguage': {
                    'en-US': {
                        'sys': {
                            "id": SDK_ID,
                            "type": "Link",
                            "linkType": "Entry"
                        }
                    }
                }
            }
        }

        new_entry = client.entries(SPACE_ID, 'master').create(
            attributes=entry_attributes
        )

        # Only publish the new stuff is `publish=True`
        if publish == True:
            new_entry.publish()

        print(f"Submitted {entry_attributes['fields']['title']}")
    
    print("Done submitting")


def compare_docs(local, remote):
    # Compare the remote docs and the local docs

    # Enrich local docs
    enriched_local = dict()
    for doc in local:
        # print(doc.keys())
        enriched_local[hash_content(doc.content)] = {
            "date": doc['date'],
            "title": doc['title'],
            "slug": doc['path'],
            "content": doc.content,
            "hash": hash_content(doc.content)
        }

    # Enrich remote docs
    enriched_remote = dict()
    for doc in remote:
        # print(doc.fields())
        enriched_remote[hash_content(doc.fields()['content'])] = {
            "date": doc.sys['updated_at'],
            "title": doc.fields()['title'],
            "slug": doc.fields()['slug'],
            "content": doc.fields()['content'],
            "hash": hash_content(doc.fields()['content'])
        }


    # Compare titles and content hashes, update only ones in which the hashes are different

    # Declare our now list that we'll be appending to shortly
    docs_to_update = list()
    docs_to_maybe_publish = list()
    docs_to_definitely_publish = list()

    # Iterate over keys
    for doc_hash in enriched_local.keys():
        # If key found in remote keys, skip it
        if doc_hash in enriched_remote.keys():
            print(f"Local and remote match for {enriched_remote[doc_hash]['title']}, skipping...")
            continue
        else:
            docs_to_maybe_publish.append(enriched_local[doc_hash])

    # return docs_to_update, docs_to_publish
    return docs_to_maybe_publish


def main():
    # Grab the remote docs
    remote_docs = load_remote()

    # Grab the local docs
    local_docs = load_local(docs_path)

    # docs_to_update, docs_to_publish = compare_docs(local=local_docs, remote=remote_docs)
    docs_to_publish = compare_docs(local=local_docs, remote=remote_docs)

    # Publish those docs!
    publish_new_docs(docs_to_publish)

    # Iterate over the new docs and if 
    # for doc in new_docs:
    #     # print(doc.content)
    #     print(doc.keys())


if __name__ == "__main__":
    main()