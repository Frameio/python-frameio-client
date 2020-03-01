from frameioclient import FrameioClient
import os
import json


def main():
    client = FrameioClient("fio-u-dRujJIgcBN_-wMV3mMuN2iRxMVi9arIr8wKQUshPTl6cf_sTvkofr-vJFQZUfotb")
    me = client.get_me()
    print('--- Account', me['account_id'])

    table = []

    if not os.path.exists('cache_all.json'):
        comments = client.get_comments('bacac75a-1234-40aa-ae22-9b6c665dba97')
        comments = [comment for comment in comments]
    else:
        comments = json.load(open('cache_all.json'))

    for i, v in enumerate(comments):
        print('--- Comment', comments[i]['text'], '\n\n')

        # sub comments
        if comments[i]['has_replies']:
            if 'replies' not in comments[i]:
                replies = [rep for rep in client.get_replies(comments[i]['id'])]
                comments[i]['replies'] = replies
        else:
            comments[i]['replies'] = []

        assigned = ''
        for sub in comments[i]['replies']:
            assigned = []
            if 'МОНТАЖ' in comments[i]['text']:
                assigned.append('Max')
            if 'misha' in sub['text'].lower():
                assigned.append('Misha')
            if 'max' in sub['text'].lower():
                assigned.append('Max')
            if 'vlad' in sub['text'].lower():
                assigned.append('Vlad')
            if 'raf' in sub['text'].lower():
                assigned.append('Raf')
            print('--- ASS', assigned)

        table.append({
            'task': comments[i]['text'],
            'image': comments[i]['thumb'],
            'assigned': assigned,
            'completed': comments[i]['completed'],
            'frame': comments[i]['frame'],
        })

    json.dump(comments, open('cache_all.json', 'w'))
    json.dump(table, open('table.json', 'w'))


if __name__ == "__main__":
    main()
