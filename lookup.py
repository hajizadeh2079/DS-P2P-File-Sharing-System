import os
import socket
import json


class LookUp:

    def __init__(self):
        self.ip = os.environ.get('MY_IP')
        self.table = list()
        self.neighbours = list()
        self.client_socket = socket.socket()

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
                print("kir")
                return row[1]
        for ip in self.neighbours:
            if ip == src:
                continue
            self.client_socket.connect((ip, 12345))
            data = {
                'src': src,
                'filename': filename,
                'ttl': ttl
            }
            encode_data = json.dumps(data).encode('utf-8')
            self.client_socket.send(encode_data)
            res = self.client_socket.recv(1024).decode()
            self.client_socket.close()
            if res != '':
                return res
        return ''
