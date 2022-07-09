import socket
import json
import os
from config import Config


class ClientSocket:
    def __init__(self, addr):
        if Config.connection_type == 'wifi':
            self.s = socket.socket()
            self.s.connect((addr, Config.port))
        if Config.connection_type == 'bluetooth':
            self.s = socket.socket(socket.AF_BLUETOOTH,
                                   socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
            self.s.connect((addr, Config.channel))

    def send_msg(self, msg):
        encode_msg = json.dumps(msg).encode('utf-8')
        self.s.send(encode_msg)

    def recv_msg(self):
        msg = self.s.recv(1024).decode()
        msg = json.loads(msg)
        return msg

    def recv_file(self, filename):
        with open(os.path.join(Config.upload_folder, filename), 'wb') as f:
            while True:
                data = self.s.recv(1024)
                if not data:
                    f.close()
                    break
                f.write(data)

    def close(self):
        self.s.close()

    @staticmethod
    def health_check(addr, port):
        if Config.connection_type == 'wifi':
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if Config.connection_type == 'bluetooth':
            s = socket.socket(socket.AF_BLUETOOTH,
                              socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        result = s.connect_ex((addr, port))
        s.close()
        if result == 0:
            return True
        else:
            return False


class ServerSocket:
    def __init__(self):
        if Config.connection_type == 'wifi':
            self.s = socket.socket()
            self.s.bind(('', Config.port))
        if Config.connection_type == 'bluetooth':
            self.s = socket.socket(socket.AF_BLUETOOTH,
                                   socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
            self.s.bind((Config.addr, Config.channel))
        self.s.listen(5)

    def accept(self):
        self.c, addr = self.s.accept()

    def send_msg(self, msg):
        encode_msg = json.dumps(msg).encode('utf-8')
        self.c.send(encode_msg)

    def recv_msg(self):
        msg = self.c.recv(1024).decode()
        msg = json.loads(msg)
        return msg

    def send_file(self, filename):
        f = open(os.path.join(Config.upload_folder, filename), 'rb')
        while True:
            l = f.read(1024)
            while (l):
                self.c.send(l)
                l = f.read(1024)
            if not l:
                f.close()
                break

    def close(self):
        self.c.close()
