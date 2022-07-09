import os
from fuzzywuzzy import fuzz

from my_socket import ClientSocket
from config import Config


class SystemManager:

    def __init__(self):
        self.addr = Config.addr
        self.table = list()
        filenames = os.listdir(Config.upload_folder)
        for filename in filenames:
            self.table.append([filename, self.addr])
        self.neighbours = list()

    def add_file(self, filename, addr=None):
        if addr is None:
            addr = self.addr
        self.table.append([filename, addr])

    def add_neighbour(self, addr):
        self.neighbours.append(addr)

    def get_neighbours(self):
        return self.neighbours

    def find_file(self, filename, src=None, ttl=5):
        if src is None:
            src = self.addr
        for row in self.table:
            if fuzz.token_set_ratio(filename, row[0]) > Config.similarity_th:
                return {'filename': row[0], 'addr': row[1]}
        if ttl >= 0:
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
                    self.add_file(filename, msg['addr'])
                    return msg
        return {'filename': '', 'addr': ''}

    def get_file(self, filename, addr):
        s = ClientSocket(addr)
        msg = {
            'type': 'get',
            'filename': filename
        }
        s.send_msg(msg)
        s.recv_file(filename)
        s.close()
