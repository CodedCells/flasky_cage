Web service for viewing data held in SQLITE3 Databases

Tabled:
db/posts.db
  posts
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

db/postdesc.db
  desciption
    id INTEGER PRIMARY KEY,
    body TEXT

db/temp.db (created at runtime for caching some expensive queries)
  tag_counts (this hold a list of tags, how many posts have it and the most highest ID for thumbnail)
    tag TEXT PRIMARY KEY,
    count INTEGER,
    thumb_id INTEGER

Very early WIP, requires seperate image server to be running.
