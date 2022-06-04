import os

from my_socket import ClientSocket
from config import Config


class SystemManager:

    def __init__(self):
        self.addr = Config.addr
        self.table = list()
        self.neighbours = list()

    def add_file(self, filename, addr=None):
        if addr is None:
            addr = self.addr
        self.table.append([filename, addr])

    def add_neighbour(self, addr):
        self.neighbours.append(addr)

    def find_file(self, filename, src=None, ttl=5):
        if src is None:
            src = self.addr
        for row in self.table:
            if row[0] == filename:
                return row[1]
        for addr in self.neighbours:
            if addr == src:
                continue
            s = ClientSocket(addr)
            msg = {
                'type': 'find',
                'src': src,
                'filename': filename,
                'ttl': ttl
            }
            s.send_msg(msg)
            msg = s.recv_msg()
            s.close()
            if msg['addr'] != '':
                return msg['addr']
        return ''

    def get_file(self, filename, addr):
        s = ClientSocket(addr)
        msg = {
            'type': 'get',
            'filename': filename
        }
        s.send_msg(msg)
        s.recv_file(filename)
        s.close()
