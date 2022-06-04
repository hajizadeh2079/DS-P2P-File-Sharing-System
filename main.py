# gunicorn -b 0.0.0.0:8080 main:app --reload

import logging
import sys
import os
from threading import Thread
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

from system_manager import SystemManager
from config import Config
from my_socket import ServerSocket


app = Flask(__name__)

handler = logging.StreamHandler(sys.stdout)
app.logger.addHandler(handler)

system_manager = SystemManager()


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        Config.connection_type = request.form['connection_type']
        server_thread = Thread(target=server_socket)
        server_thread.start()
    return render_template('home.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        file.save(os.path.join(Config.upload_folder, filename))
        system_manager.add_file(filename)
        return 'File Uploaded'
    return render_template('upload.html')


@app.route('/connect', methods=['GET', 'POST'])
def connect():
    if request.method == 'POST':
        addr = request.form['addr']
        system_manager.add_neighbour(addr)
        return 'Neighbour Added'
    return render_template('connect.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        filename = request.form['filename']
        addr = system_manager.find_file(filename)
        if addr != '':
            system_manager.get_file(filename, addr)
            return 'File Downoaded'
        return 'File Not Found'
    return render_template('search.html')


def server_socket():
    s = ServerSocket()
    while True:
        s.accept()
        msg = s.recv_msg()
        if msg['type'] == 'find':
            src = msg['src']
            filename = msg['filename']
            ttl = msg['ttl'] - 1
            addr = system_manager.find_file(filename, src, ttl)
            msg = {
                'addr': addr
            }
            s.send_msg(msg)
        elif msg['type'] == 'get':
            filename = msg['filename']
            s.send_file(filename)
        s.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

# TODO exit mechanism + ls files + seacrh/download + similarity maching
