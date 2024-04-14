from database import get_connection

def paginate_me(page, qty, count):
    start = page * qty
    get = qty
    if start + get + (qty-1) >= count:
        get += qty
    
    return start, get

def other_paginate_me(page, qty, count):
    start = page * qty
    get = qty + start
    
    if get + qty >= count:
        get = None
    
    return start, get

class Tags:
    def __init__(self, tag, post_count, thumb_id):
        self.tag = tag
        self.post_count = post_count
        self.thumb_id = thumb_id
    
    @classmethod
    def get_tags(cls, page=0, qty=25):
        temp_conn = get_connection('temp.db')
        t = temp_conn.cursor()
        
        t.execute('''CREATE TABLE IF NOT EXISTS tag_counts (
            tag TEXT PRIMARY KEY,
            count INTEGER,
            thumb_id INTEGER)''')
        
        t.execute("SELECT COUNT(*) FROM tag_counts")
        count = t.fetchone()[0]
        
        if count == 0:# must be created
            conn = get_connection()
            c = conn.cursor()
            c.execute("SELECT tags, id, ext FROM posts")
            
            posts = c.fetchall()
            
            # Initialize a dictionary to store tag counts
            tag_counts = {}
            
            # Count the occurrences of each tag
            for post in posts:
                tags = post[0].split(',')  # Split the comma-separated tags
                for tag in tags:
                    tag = tag.strip()  # Remove leading/trailing whitespace
                    if tag in tag_counts:
                        tag_counts[tag][0] += 1
                    else:
                        tag_counts[tag] = [1, post[1]]
            
            # Update the tag_counts table
            for tag, [count, thumb_id] in tag_counts.items():
                t.execute("INSERT OR REPLACE INTO tag_counts (tag, count, thumb_id) VALUES (?, ?, ?)", (tag, count, thumb_id))
            
            # Commit the changes to the database
            temp_conn.commit()
        
        t.execute("SELECT COUNT(*) FROM tag_counts")
        count = t.fetchone()[0]
        
        start, qty = paginate_me(page, qty, count)
        
        t.execute(f"""
    SELECT tag, count, thumb_id
    FROM tag_counts
    ORDER BY count DESC
    LIMIT {start},{qty}""")
        
        rows = t.fetchall()
        
        temp_conn.close()
        return [cls(*row) for row in rows], count

class Uploader:
    def __init__(self, uploader, post_count):
        self.name = uploader
        self.post_count = post_count
    
    @classmethod
    def get_uploaders(cls, page=0, qty=25):
        conn = get_connection()
        c = conn.cursor()
        
        c.execute("CREATE INDEX IF NOT EXISTS idx_uploader ON posts(uploader)")
        
        c.execute("SELECT COUNT(DISTINCT uploader) AS unique_uploaders_count FROM posts")
        unique = c.fetchone()[0]
        
        start, qty = paginate_me(page, qty, unique)
        
        c.execute(f"""
    SELECT uploader, COUNT(*) AS post_count
    FROM posts
    GROUP BY uploader
    ORDER BY post_count DESC
    LIMIT {start},{qty}""")
        rows = c.fetchall()
        
        conn.close()
        return [cls(*row) for row in rows], unique


class Post:
    def __init__(self, post_id, uploader, title, filedate, uploaddate, ext, rating, tags, folders, media_width, media_height, media_bytes, desclen, descwords):
        self.id = post_id
        self.uploader = uploader
        self.users_mentioned = [uploader]
        self.title = title
        
        self.filedate = filedate
        self.uploaddate = uploaddate
        
        self.ext = ext
        self.rating = rating
        
        self.tags = tags.split(',')
        self.folders = []
        if folders:
            self.folders = [int(x) for x in folders.split(',')]
        
        self.media_size = [media_width, media_height]
        self.media_bytes = media_bytes
        
        self.desclen = desclen
        self.descwords = descwords

    @classmethod
    def get_by_id(cls, post_id):
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM posts WHERE id=?", (post_id,))
        row = c.fetchone()
        conn.close()
        if row:
            return cls(*row)
        
        return None

    @classmethod
    def get_by_uploader(cls, uploader_name, page=0, qty=25):
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM posts WHERE uploader=?", (uploader_name,))
        rows = c.fetchall()
        conn.close()
        
        count = len(rows)
        start, off = other_paginate_me(page, qty, count)
        
        return [cls(*row) for row in rows[start:off]], count

    @classmethod
    def get_by_tag(cls, tag_name, page=0, qty=25):
        conn = get_connection()
        c = conn.cursor()
        
        c.execute("SELECT * FROM posts WHERE tags LIKE ?", ('%'+tag_name+'%',))
        rows = c.fetchall()
        conn.close()
        
        count = len(rows)
        start, off = other_paginate_me(page, qty, count)
        return [cls(*row) for row in rows[start:off]], count