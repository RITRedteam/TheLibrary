from flask import Flask, jsonify, request, flash, abort, make_response
from flask import redirect, url_for, render_template, send_file
from werkzeug.utils import secure_filename
from Link import Link

import os
import random
import string
import time

app = Flask(__name__)
app.secret_key = b'i dont care about this key'


USERNAME = os.environ.get("LIBRARY_USER", 'admin')
PASSWORD = os.environ.get("LIBRARY_PASS", 'password')
COOKIE_KEY = os.environ.get("LIBRARY_COOKIE_KEY", 'redteam-cookie')
COOKIE_VALUE = os.environ.get("LIBRARY_COOKIE_VAL", 'super-secret')

COOKIE_KEY
link_map = {}

def gen_rand_str():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))

app.jinja_env.globals.update(gen_rand_str=gen_rand_str)
app.jinja_env.globals.update(COOKIE_KEY=COOKIE_KEY)
app.jinja_env.globals.update(COOKIE_VALUE=COOKIE_VALUE)

@app.template_filter('ctime')
def timectime(s):
    if s == 0.0:
        return "Never"
    return time.ctime(s)

@app.after_request
def set_response_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

def clean_map():
    global link_map
    expired_links = []
    for url, link in link_map.items():
        if link.timeout < time.time() and link.timeout != 0.0:
            expired_links.append(url)
        if link.clicks < 1:
            expired_links.append(url)
    for expired_link in expired_links:
        del link_map[expired_link]

@app.route('/l/<req_path>')
def file_handler(req_path):
    clean_map()
    striped_path = req_path.replace("l/", "")
    # BASIC directory traversal mitigation
    if ".." in req_path:
        time.sleep(35)
        return abort(400)
    # Joining the base and the requested path
    abs_path = 'files/' + req_path
    # Return 404 if path doesn't exist
    if not os.path.exists(abs_path):
        if req_path not in link_map:
            time.sleep(35)
            return abort(404)
    print(link_map[striped_path].clicks)
    # Check if path is a file and serve
    if striped_path in link_map and os.path.isfile('files/' + link_map[striped_path].filename):
        return link_map[striped_path].send_file()

    time.sleep(35)
    abort(400)

@app.route('/', defaults={'req_path': ''})
@app.route('/<req_path>')
def main(req_path):
    abs_path = 'files/' + req_path
    if req_path == 'favicon.ico':
        return redirect(url_for('static',filename='images/favicon.ico'))

    if COOKIE_KEY in request.cookies and request.cookies[COOKIE_KEY] == COOKIE_VALUE:
        if os.path.isfile(abs_path):
            return send_file(abs_path)
    
        # Show directory contents
        files = os.listdir('files/')
        files.remove('.gitkeep')
        return render_template('index.html', files=files)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username==USERNAME and password==PASSWORD:
            resp = make_response(redirect(url_for('main')))
            resp.set_cookie(COOKIE_KEY, COOKIE_VALUE)
            return resp
        flash('Incorrect Username or Password')
        return redirect(request.url)
    return render_template('login.html')

@app.route('/logout')
def logout():
    resp = make_response(redirect(url_for('login')))
    resp.set_cookie(COOKIE_KEY, COOKIE_VALUE, expires=0)
    return resp

@app.route('/link_gen', methods=['GET', 'POST'])
def link_gen():
    if COOKIE_KEY in request.cookies and request.cookies[COOKIE_KEY] == COOKIE_VALUE:
        if request.method == 'POST':
            link = request.form['link']
            real_file = request.form['real_file']
            clicks = request.form['clicks']
            timeout = request.form['timeout']
            if link is None or real_file is None or clicks is None or timeout is None:
                abort(400)
            new_link = Link(real_file, clicks, timeout)
            global link_map
            link_map[link] = new_link
            redirect(request.url)
        files = os.listdir('files/')
        files.remove('.gitkeep')
        return render_template('link_gen.html', files=files)
    return redirect(url_for('login'))

@app.route('/link_table')
def link_table():
    if COOKIE_KEY in request.cookies and request.cookies[COOKIE_KEY] == COOKIE_VALUE:
        clean_map()
        return render_template('link_table.html', link_map=link_map)
    return redirect(url_for('login'))

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if COOKIE_KEY in request.cookies and request.cookies[COOKIE_KEY] == COOKIE_VALUE:
        if request.method == 'POST':
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file sent')
                return redirect(request.url)
            file = request.files['file']
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join('files/', filename))
                return redirect(url_for('main'))
        return render_template('upload.html')
    return redirect(url_for('login'))


if __name__ == '__main__':
    host = os.environ.get("FLASK_HOST", "0.0.0.0")
    try:
        port = os.environ.get("FLASK_PORT", "5000")
        port = int(port)
    except ValueError:
        port = 5000
    debug = os.environ.get("FLASK_DEBUG", "True")
    debug = debug.lower().strip() in ["true", "yes", "1", "t"]
    app.run(debug=debug, host=host, port=port)
