from fa_parser import parse_postpage, get_prop, strdate
import sqlite3
import os
import json
import re

DATABASE_NAME = '../db/posts.db'

def get_connection(name=DATABASE_NAME):
    return sqlite3.connect(name)

def pad(x):
    if x.startswith(','):
        x = x[1:]
    if x.endswith(','):
        x = x[:-1]
    
    if not x:
        return ''
    
    return f',{x},'

if __name__ == '__main__':
    old = get_connection('../db/o-posts.db')
    new = get_connection()
    
    oc = old.cursor()
    oc.execute(f"SELECT * FROM posts")
    
    nc = new.cursor()
    nc.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY,
            uploader TEXT,
            title TEXT,
            filedate INTEGER,
            uploaddate INTEGER,
            ext TEXT,
            rating TEXT,
            tags TEXT,
            folders TEXT,
            media_width INTEGER,
            media_height INTEGER,
            media_bytes INTEGER,
            desclen INTEGER,
            descwords INTEGER
        )
    ''')
    
    while True:
        data = oc.fetchone()
        if not data:
            break
        
        data = list(data)
        
        data[7] = pad(data[7])
        data[8] = pad(data[8])
        
        nc.execute('INSERT OR IGNORE INTO posts (id, uploader, title, filedate, uploaddate, ext, rating, tags, folders, media_width, media_height, media_bytes, desclen, descwords) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            tuple(data))
    
    new.commit()