import os
import requests


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

    def find_file(self, filename, src=None):
        if src is None:
            src = self.ip
        for row in self.table:
            if row[0] == filename:
                return ip
        for ip in self.neighbours:
            if ip == src:
                continue
            url = f'{ip}:5000/find'
            data = {
                'src': src,
                'filename': filename,
                'ttl': 5
            }
            resp = requests.post(url, data=data)
            if resp is not None:
                return ip
        return None
