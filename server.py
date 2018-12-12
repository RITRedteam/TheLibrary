from flask import Flask, jsonify, request, flash, abort
from flask import redirect, url_for, render_template, send_file
from werkzeug.utils import secure_filename
from Link import Link

import os
import random
import string
import time

app = Flask(__name__)
app.secret_key = b'i dont care about this key'

link_map = {}

def gen_rand_str():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=25))
app.jinja_env.globals.update(gen_rand_str=gen_rand_str)

@app.template_filter('ctime')
def timectime(s):
    if s > time.time() + 3500000:
        return "Never"
    return time.ctime(s)

@app.route('/', defaults={'req_path': ''})
@app.route('/<req_path>')
def main(req_path):
    # BASIC directory traversal mitigation
    if ".." in req_path:
        return abort(400)

    # Joining the base and the requested path
    abs_path = 'files/' + req_path

    # Return 404 if path doesn't exist
    if not os.path.exists(abs_path):
        if req_path not in link_map:
            return abort(404)

    # Check if path is a file and serve
    if os.path.isfile(abs_path):
        return send_file(abs_path)
    if req_path in link_map and os.path.isfile('files/' + link_map[req_path].filename):
        return link_map[req_path].send_file()

    # Show directory contents
    files = os.listdir(abs_path)
    files.remove('.gitkeep')
    return render_template('index.html', files=files)

@app.route('/link_gen', methods=['GET', 'POST'])
def link_gen():
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

@app.route('/link_table')
def link_table():
    global link_map
    expired_links = []
    for url, link in link_map.items():
        if link.timeout < time.time():
            expired_links.append(url)
        if link.clicks < 1:
            expired_links.append(url)
    for expired_link in expired_links:
        del link_map[expired_link]
    return render_template('link_table.html', link_map=link_map)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
