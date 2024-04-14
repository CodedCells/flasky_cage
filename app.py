from flask import g, Flask, render_template, request
from database import get_posts
from models import Post, Uploader, Tags
import timeit
import math
from datetime import datetime

app = Flask(__name__)

@app.before_request
def before_request():
    g.start = timeit.default_timer()

@app.after_request
def after_request(response):
    diff = timeit.default_timer() - g.start
    if ((response.response) and
        (200 <= response.status_code < 300) and
        (response.content_type.startswith('text/html'))):
        
        message = f'''
Server Time: {datetime.now().strftime("%c")}<br>
Served in {math.ceil(diff*1000):,}ms'''
        
        response.set_data(response.get_data().replace(
            b'__EXECUTION_TIME__', bytes(message, 'utf-8')))
    
    return response

@app.route('/')
def index():
    return render_template('index.html', posts=[])

@app.route('/view/<int:post_id>')
def post(post_id):
    post = Post.get_by_id(post_id)
    return render_template('post.html', post=post)

@app.route('/users')
def uploaders():
    page_no = request.args.get('page', 1, type=int)
    results = request.args.get('results', 25, type=int)
    posts, count = Uploader.get_uploaders(page=page_no - 1, qty=results)
    page_max = int(count / results)
    
    return render_template(
        'uploaders.html',
        uploaders=posts,
        count=count,
        page_no=page_no,
        page_max=page_max
        )

@app.route('/tags')
def tags():
    page_no = request.args.get('page', 1, type=int)
    results = request.args.get('results', 25, type=int)
    posts, count = Tags.get_tags(page=page_no - 1, qty=results)
    page_max = int(count / results)
    
    return render_template(
        'tags.html',
        tags=posts,
        count=count,
        page_no=page_no,
        page_max=page_max
        )

@app.route('/user/<uploader_name>')
def uploader(uploader_name):
    page_no = request.args.get('page', 1, type=int)
    mode = request.args.get('mode', 'full', type=str)
    results = request.args.get('results', 25, type=int)
    posts, count = Post.get_by_uploader(uploader_name, page=page_no - 1, qty=results)
    page_max = int(count / results)
    
    return render_template(
        'uploader.html',
        mode=mode,
        uploader=uploader_name,
        posts=posts,
        count=count,
        page_no=page_no,
        page_max=page_max
        )

@app.route('/tag/<tag_name>')
def tag(tag_name):
    page_no = request.args.get('page', 1, type=int)
    mode = request.args.get('mode', 'full', type=str)
    results = request.args.get('results', 25, type=int)
    posts, count = Post.get_by_tag(tag_name, page=page_no - 1, qty=results)
    page_max = int(count / results)
    
    return render_template(
        'tag.html',
        mode=mode,
        tag=tag_name,
        posts=posts,
        count=count,
        page_no=page_no,
        page_max=page_max
        )

if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['FLASK_RUN_EXTRA_FILES'] = True
    app.run(host='127.0.0.1', port=8970)
