from flask import g, Flask, render_template, request, jsonify
from database import get_posts
from models import Post, Uploader, Tags
import timeit
import math
from datetime import datetime
import json

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

# Custom Jinja2 filter function to convert Unix timestamp to local date
def unix_timestamp_to_local_date(timestamp):
    utc_datetime = datetime.utcfromtimestamp(timestamp)
    local_datetime = utc_datetime.replace(tzinfo=None)  # Assuming server is running in local timezone
    formatted_date = local_datetime.strftime('%b %d, %Y %H:%M')
    return formatted_date

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
    userstat = Uploader.get_stats(uploader_name)
    page_max = int(count / results)
    
    return render_template(
        'uploader.html',
        mode=mode,
        uploader=uploader_name,
        posts=posts,
        count=count,
        page_no=page_no,
        page_max=page_max,
        userstat=userstat
        )

@app.route('/linked')
def linked():
    page_no = request.args.get('page', 1, type=int)
    mode = request.args.get('mode', 'full', type=str)
    results = request.args.get('results', 25, type=int)
    include = request.args.get('include', 'all', type=str)
    
    post_ids, count = Post.get_all_linked(page=page_no - 1, qty=results, include=include)
    
    posts = Post.get_by_id(post_ids)
    print(len(post_ids), len(posts))
    
    page_max = int(count / results)
    
    return render_template(
        'tag.html',
        mode=mode,
        tag=f'Linked',
        posts=posts,
        count=count,
        page_no=page_no,
        page_max=page_max
        )

@app.route('/linkro/<what>/<thing>')
def linkto(what, thing):
    page_no = request.args.get('page', 1, type=int)
    mode = request.args.get('mode', 'full', type=str)
    results = request.args.get('results', 25, type=int)
    
    post_ids, count = Post.get_linked_to(thing, page=page_no - 1, qty=results)
    
    posts = Post.get_by_id(post_ids)
    
    page_max = int(count / results)
    
    return render_template(
        'tag.html',
        mode=mode,
        tag=f'Linking to {thing}',
        posts=posts,
        count=count,
        page_no=page_no,
        page_max=page_max
        )

@app.route('/linkfrom/<what>/<thing>')
def linkfrom(what, thing):
    page_no = request.args.get('page', 1, type=int)
    mode = request.args.get('mode', 'full', type=str)
    results = request.args.get('results', 25, type=int)
    
    post_ids, count = Post.get_linked_from(thing, page=page_no - 1, qty=results)
    posts = []
    for post_id in post_ids:
        post = Post.get_by_id(post_id)
        
        posts.append(post)
    
    page_max = int(count / results)
    
    return render_template(
        'tag.html',
        mode=mode,
        tag=f'Linked from {thing}',
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

@app.route('/query')
def query():
    return render_template('query.html')

@app.route('/data', methods=['GET', 'POST'])
def handle_post_request():
    try:
        data = json.loads(request.data)
    except:
        data = {}
    
    what = request.args.get('what', 'nothing', type=str)
    which = request.args.get('which', 'nothing', type=str)
    if 'which' in data:
        which = data['which']
    
    response_data = {'error': f'Cannot resolve {what}'}
    
    if what == 'users':
        response_data = Uploader.get_just_uploaders()
    
    elif what == 'posts':
        response_data = Post.get_just_posts()
    
    elif what == 'user_posts':
        posts, count = Post.get_by_uploader(which, None)
        response_data = [x.id for x in posts]
    
    elif what == 'post_info':
        response_data = {}
        for i in which.split(','):
            if not i:
                continue
            
            data = Post.get_by_id(i)
            if data:
                data = vars(data)
            response_data[i] = data
        
        if len(response_data) == 1:
            response_data = data
    
    # Return a JSON response
    return jsonify(response_data)


if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['FLASK_RUN_EXTRA_FILES'] = True
    app.jinja_env.filters['unix_to_local_date'] = unix_timestamp_to_local_date
    app.run(host='127.0.0.1', port=8970)
