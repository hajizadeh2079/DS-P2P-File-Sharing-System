# gunicorn -w 1 -b 0.0.0.0:8080 main:app --reload

import logging
import sys
import os
import socket
import json
from threading import Thread
from time import sleep
from flask import Flask, render_template, request
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


def server_socket():
    s = socket.socket()
    s.bind(('', 12345))
    s.listen(5)
    while True:
        c, addr = s.accept()
        msg = c.recv(1024).decode()
        msg = json.loads(msg)
        src = msg['src']
        filename = msg['filename']
        ttl = msg['ttl'] - 1
        ip = lookup.find_file(filename, src, ttl)
        c.send(ip.encode())
        c.close()


server_thread = Thread(target=server_socket)
server_thread.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
