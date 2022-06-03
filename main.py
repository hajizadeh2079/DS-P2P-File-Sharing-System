# gunicorn -w 1 -b 0.0.0.0:5000 main:app --reload

from fileinput import filename
import logging
import sys
import os
from flask import Flask, render_template, request, Request
from werkzeug.utils import secure_filename

from lookup import LookUp


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'files'

handler = logging.StreamHandler(sys.stdout)
app.logger.addHandler(handler)

lookup = LookUp()

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        lookup.add_file(filename)
        return 'File Uploaded'
    return render_template('upload.html')

@app.route('/connect', methods=['GET', 'POST'])
def connect():
    if request.method == 'POST':
        ip = request.form['ip']
        lookup.add_neighbour(ip)
        return 'Neighbour Added'
    return render_template('connect.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        filename = request.form['filename']
        ip = lookup.find_file(filename)
        return ip
    return render_template('search.html')

@app.post('/find')
async def collect_metrics(request: Request):
    request = await request.json()
    src = request['src']
    filename = request['filename']
    dst = lookup.find_file(filename, src)
    return dst

if __name__ == '__main__':
    app.run(host="0.0.0.0")
