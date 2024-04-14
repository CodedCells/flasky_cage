import sqlite3

DATABASE_NAME = 'db/posts.db'

def get_connection(name=DATABASE_NAME):
    return sqlite3.connect(name)

def get_posts():
    return []
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM posts")
    posts = c.fetchall()
    conn.close()
    return posts
