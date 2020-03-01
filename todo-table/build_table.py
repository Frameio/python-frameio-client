from frameioclient import FrameioClient
import os
import json


def write_xlsx(table):
    """ Export to excel
    """
    import xlsxwriter
    import io
    import urllib.request

    workbook = xlsxwriter.Workbook('web/output.xlsx')
    worksheet = workbook.add_worksheet()

    # Widen the first column to make the text clearer.
    worksheet.set_column('A:A', 7)  # time
    worksheet.set_column('B:B', 36)  # image
    worksheet.set_column('C:C', 40)  # desc
    worksheet.set_column('D:D', 10)  # assign
    top = workbook.add_format({'valign': 'top', 'text_wrap': True})

    for i, t in enumerate(table):
        k = i + 1
        # Insert an image
        print('A%i' % k)
        worksheet.write_string('A%i' % k, t['timestamp'], top)
        image_data = io.BytesIO(urllib.request.urlopen(t['image']).read())
        worksheet.insert_image('B%i' % k, t['image'], {'image_data': image_data, 'x_scale': 0.171, 'y_scale': 0.2})
        worksheet.write_string('C%i' % k, t['desc'], top)
        worksheet.write_string('D%i' % k, ','.join(t['assigned']), top)
        worksheet.set_row(i, 200)

    workbook.close()


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
    write_xlsx(table)

    json.dump(comments, open('cache_all.json', 'w'))
    json.dump(table, open('web/table.json', 'w'))


if __name__ == "__main__":
    main()
