from flask import Flask, jsonify, request, flash, abort
from flask import redirect, url_for, render_template, send_file
from werkzeug.utils import secure_filename

import os
import random
import string

app = Flask(__name__)
app.secret_key = b'i dont care about this key'

link_map = {}

def gen_rand_str():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
app.jinja_env.globals.update(gen_rand_str=gen_rand_str)


@app.route('/', defaults={'req_path': ''})
@app.route('/<path:req_path>')
def main(req_path):
    # BASIC directory traversal mitigation
    if ".." in req_path:
        return abort(400)

    # Joining the base and the requested path
    abs_path = os.path.join('files/', req_path)

    # Return 404 if path doesn't exist
    if not os.path.exists(abs_path):
        return abort(404)

    # Check if path is a file and serve
    if os.path.isfile(abs_path):
        return send_file(abs_path)

    # Show directory contents
    files = os.listdir(abs_path)
    files.remove('.gitkeep')
    return render_template('index.html', files=files)

@app.route('/link_gen')
def link_gen():
    return render_template('link_gen.html')

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
