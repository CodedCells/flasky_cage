from fa_parser import parse_postpage, get_prop, strdate
import sqlite3
import os
import json
import re

DATABASE_NAME = '../db/posts.db'

def get_connection(name=DATABASE_NAME):
    return sqlite3.connect(name)

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

def get_desc(desc):
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
    

if __name__ == '__main__':
    DESCS = get_connection('../db/postdesc.db')
    LINKS = get_connection('../db/postdesc_links.db')
    
    desc_cursor = DESCS.cursor()
    link_cursor = LINKS.cursor()
    desc_cursor.execute(f"SELECT * FROM description")
    
    link_cursor.execute('''
        CREATE TABLE IF NOT EXISTS desc_posts (
            uuid STRING PRIMARY KEY,
            origin INTEGER,
            linking INTEGER
        )
    ''')
    link_cursor.execute('''
        CREATE TABLE IF NOT EXISTS desc_users (
            uuid STRING PRIMARY KEY,
            origin INTEGER,
            linking STRING
        )
    ''')
    
    while True:
        data = desc_cursor.fetchone()
        if not data:
            break
        
        sid, desc = data
        linkers = get_desc(desc)
        
        for table, to in linkers:
            link_cursor.execute(f'INSERT OR IGNORE INTO {table} (uuid, origin, linking) VALUES (?, ?, ?)',
            (f'[{sid}.{to}]', sid, to))
    
    LINKS.commit()