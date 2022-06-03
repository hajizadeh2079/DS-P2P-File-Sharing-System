import os
import socket
import json


class LookUp:

    def __init__(self):
        self.ip = os.environ.get('MY_IP')
        self.table = list()
        self.neighbours = list()

    def add_file(self, filename, ip=None):
        if ip is None:
            ip = self.ip
        self.table.append([filename, ip])

    def add_neighbour(self, ip):
        self.neighbours.append(ip)

    def find_file(self, filename, src=None, ttl=5):
        if src is None:
            src = self.ip
        for row in self.table:
            if row[0] == filename:
                return row[1]
        for ip in self.neighbours:
            if ip == src:
                continue
            s = socket.socket()
            s.connect((ip, 12345))
            data = {
                'type': 'find',
                'src': src,
                'filename': filename,
                'ttl': ttl
            }
            encode_data = json.dumps(data).encode('utf-8')
            s.send(encode_data)
            res = s.recv(1024).decode()
            s.close()
            if res != '':
                return res
        return ''

    def get_file(self, filename, ip):
        s = socket.socket()
        s.connect((ip, 12345))
        data = {
            'type': 'get',
            'filename': filename
        }
        encode_data = json.dumps(data).encode('utf-8')
        s.send(encode_data)
        with open(os.path.join('files', filename), 'wb') as f:
            while True:
                data = s.recv(1024)
                if not data:
                    f.close()
                    break
                f.write(data)
        s.close()
