# gunicorn -b 0.0.0.0:8080 main:app --reload

import logging
import sys
import os
import json
from threading import Thread
from flask import Flask, render_template, request, url_for, redirect
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
        return render_template('upload_success.html')
    return render_template('upload.html')


@app.route('/connect', methods=['GET', 'POST'])
def connect():
    if request.method == 'POST':
        addr = request.form['addr']
        system_manager.add_neighbour(addr)
        return render_template('connect_success.html')
    return render_template('connect.html')


@app.route('/download', methods=['GET', 'POST'])
def download():
    if request.method == 'POST':
        filename = request.form['filename']
        addr = request.form['addr']
        system_manager.get_file(filename, addr)
        return render_template('download_success.html')
    messages = json.loads(request.args['messages'])
    return render_template('download.html', filename=messages['filename'], addr=messages['addr'])


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        filename = request.form['filename']
        addr = system_manager.find_file(filename)
        if addr != '':
            messages = json.dumps({
                'addr': addr,
                'filename': filename
            })
            return redirect(url_for('.download', messages=messages))
        return render_template('search_failed.html')
    return render_template('search.html')


def server_socket():
    s = ServerSocket()
    while True:
        s.accept()
        msg = s.recv_msg()
        app.logger.error(msg)
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

# TODO exit mechanism + similarity maching
