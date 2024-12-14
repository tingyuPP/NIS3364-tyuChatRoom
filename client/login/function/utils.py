import re
import socket
import json
import hashlib

def is_valid_password(password):
    """
    检查密码长度不少于8位，且只含字母和数字

    :param password: 要检查的密码字符串
    :return: 如果密码有效返回True，否则返回False
    """
    if len(password) < 8:
        return False
    if not re.match("^[A-Za-z0-9]+$", password):
        return False
    return True

def hash_password(password):
    """
    对密码进行SHA-256哈希加密

    :param password: 要加密的密码字符串
    :return: 加密后的密码哈希值
    """
    sha256 = hashlib.sha256()
    sha256.update(password.encode('utf-8'))
    return sha256.hexdigest()

class Client:
    def __init__(self):
        self.client_socket = None

    def connect(self, host, port):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))

    def send_data(self, data):
        self.client_socket.send(data.encode('utf-8'))

    def receive_data(self):
        data = self.client_socket.recv(1024).decode('utf-8')
        return data

    def close(self):
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None
