from frameioclient import FrameioClient
import os
import json


def main():
    client = FrameioClient(open('token.txt').read())
    me = client.get_me()
    print('--- Account', me['account_id'])

    me = client.get_comments('bacac75a-1234-40aa-ae22-9b6c665dba97')
    print('Total comments', me.total)

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

        assigned = []
        if 'МОНТАЖ' in comments[i]['text']:
            assigned.append('Монтажер')
        for sub in comments[i]['replies']:
            if 'misha' in sub['text'].lower():
                assigned.append('Misha')
            if 'max' in sub['text'].lower():
                assigned.append('Max')
            if 'vlad' in sub['text'].lower():
                assigned.append('Vlad')
            if 'raf' in sub['text'].lower():
                assigned.append('Raf')
            print('--- ASS', assigned)

        frame = comments[i]['frame']
        if frame is None:
            continue  # it's a reply to root comment, skip it
        else:
            total = frame / 25.0
            minute = int(total / 60)
            sec = total - minute * 60

        table.append({
            'desc': comments[i]['text'],
            'image': comments[i]['thumb'],
            'assigned': assigned,
            'completed': comments[i]['completed'],
            'frame': comments[i]['frame'],
            'time': total,
            'timestamp': '{0:02.0f}'.format(minute) + ':' + '{0:02.0f}'.format(int(sec))
        })

    table = sorted(table, key=lambda k: k['frame'])
    json.dump(comments, open('cache_all.json', 'w'))
    json.dump(table, open('web/table.json', 'w'))


if __name__ == "__main__":
    main()
