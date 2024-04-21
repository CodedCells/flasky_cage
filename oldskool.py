from fa_parser import parse_postpage, get_prop, strdate
import sqlite3
import os
import json
import re
import requests

DATABASE_NAME = 'db/posts.db'

def get_connection(name=DATABASE_NAME):
    return sqlite3.connect(name)

def get_ids(conn, table, col='id'):
    c = conn.cursor()
        
    c.execute(f"SELECT {col} FROM {table}")
    
    return [x[0] for x in c.fetchall()]

def terminate_number(i, allow_negative=False, allow_decimal=False):
    # function to terminate when we hit a non-numerical digit
    
    ret = ''
    for c in i.strip():
        
        if c == '-' and allow_negative and not ret:
            pass
        
        elif c == '.' and allow_decimal and '.' not in ret:
            pass
        
        elif not c.isdigit():
            break
        
        ret += c
    
    return ret

def get_linking(desc):
    ret = {'desc_posts': set(), 'desc_users': set()}
    
    for linky in ['view/', 'full/']:
        if linky not in desc:
            continue
        
        for x in desc.split(linky)[1:]:
            x = terminate_number(x.split('"')[0])
            if x:
                ret['desc_posts'].add(int(x))
    
    for linky in ['user/', 'gallery/', 'scraps/']:
        if linky not in desc:
            continue
        
        for x in desc.split(linky)[1:]:
            x = x.split('"')[0].lower()
            
            if '/' in x:
                x = x.split('/')[0]
            
            ret['desc_users'].add(x)
    
    listed = []
    for k, v in ret.items():
        listed += [[k, i] for i in v]
    
    return listed


def add_to_db(fn, sid, post_db, desc_db):
    parser = parse_postpage()
    parser.load(fn)
    
    data = parser.get_all()
    print(sid)
    #with open(f'dump-{sid}.txt', 'w') as fh:
    #    json.dump(data, fh, indent='\t')
    
    desc = data['desc']
    desc = '\n'.join([x.strip() for x in desc.split('\\n')])
    desc = '\n'.join([x.strip() for x in desc.split('\n')])

    post_cur = post_db.cursor()
        
    media_width, media_height = -1, -1
    if data.get('resolution'):
        media_width, media_height = data['resolution']
    
    if 'Server Time: ' in data:
        file_date = get_prop('Server Time: ', data, t='</div').strip()
        file_date = strdate(file_date).timestamp()
    
    else:
        file_date = -1
    
    media_bytes = -1
    media_fol = int(str(sid)[-2:])
    media_path = f'/media/fa/{media_fol:02d}/{sid}.{data["ext"]}'
    
    if os.path.isfile(media_path):
        sbytes = os.path.getsize(media_path)
    
    post_cur.execute(
        'INSERT OR IGNORE INTO posts (id, uploader, title, filedate, uploaddate, ext, rating, tags, folders, media_width, media_height, media_bytes, desclen, descwords) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (
        data['id'],
        data['uploader'],
        data['title'],
        file_date,
        data['upload_date'],
        data['ext'],
        data['rating'],
        ',' + ','.join(data['tags']) + ',',
        ',' + ','.join(data.get('folders', {}).keys()) + ',',
        media_width,
        media_height,
        media_bytes,
        len(desc),
        data['descwc']
        ))
    post_db.commit()
    
    desc_cur = desc_db.cursor()
    desc_cur.execute(
        'INSERT OR IGNORE INTO description (id, body) VALUES (?, ?)',
        (
        sid,
        desc
        ))
    desc_db.commit()
    
    link_db = get_connection('db/postdesc_links.db')
    link_cur = link_db.cursor()
    
    linkers = get_linking(desc)
    for table, to in linkers:
        link_cursor.execute(f'INSERT OR IGNORE INTO {table} (uuid, origin, linking) VALUES (?, ?, ?)',
        (f'[{sid}.{to}]', sid, to))
    link_db.commit()

if __name__ == '__main__':
    POSTS = get_connection()
    DESCS = get_connection('db/postdesc.db')
    
    desc_list = set(get_ids(DESCS, 'description'))
    got_list = set([x for x in get_ids(POSTS, 'posts') if x in desc_list])
    # must have in both lists
    del desc_list
    
    with open('dump.txt', 'a') as fh:
        fh.write('\n')
    
    for i in range(100):
        fol_path = f'/stra/onefad/pm/{i:02d}/'
        for fn in os.listdir(fol_path):
            sid = int(fn.split('_')[0])
            if sid not in got_list:
                with open('dump.txt', 'a') as fh:
                    fh.write(f'\n{sid}')
                    
                add_to_db(fol_path + fn, sid, POSTS, DESCS)
    
    try:
        x = requests.post('http://192.168.0.138:6991/rebuild')
    
    except:
        print('Offline.')