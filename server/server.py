import socket
import threading
import sqlite3
import json

class ChatServer:
    def __init__(self, host, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(5)
        self.clients = {}  # 用于存储在线用户的字典，键为用户名，值为套接字

        # 连接到SQLite数据库
        self.connection = sqlite3.connect('ChatRoom.db', check_same_thread=False)

    def run(self):
        print("Server started...")
        while True:
            client_socket, client_address = self.server.accept()
            threading.Thread(target=self.handle_client, args=(client_socket, client_address)).start()

    def handle_client(self, client_socket, client_address):
        try:
            while True:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                message = json.loads(data)
                if message['type'] == 'login':
                    username = message['username']
                    password_hash = message['password_hash']
                    if self.authenticate_user(username, password_hash):
                        client_socket.send(json.dumps({'type': 'login', 'status': 'SUCCESS'}).encode('utf-8'))
                        self.clients[username] = client_socket
                        print(f"{username} connected from {client_address}")
                    else:
                        client_socket.send(json.dumps({'type': 'login', 'status': 'FAILURE'}).encode('utf-8'))
                        client_socket.close()
                        break

                elif message['type'] == 'register':
                    username = message['username']
                    password_hash = message['password_hash']
                    if self.register_user(username, password_hash):
                        client_socket.send(json.dumps({'type': 'register', 'status': 'SUCCESS'}).encode('utf-8'))
                    else:
                        client_socket.send(json.dumps({'type': 'register', 'status': 'FAILURE'}).encode('utf-8'))
                        client_socket.close()
                        break
                elif message['type'] == 'message':
                    self.broadcast(message['content'], message['username'])
        except:
            client_socket.close()

    def authenticate_user(self, username, password_hash):
        try:
            cursor = self.connection.cursor()
            query = "SELECT password_hash FROM users WHERE username = ?"
            cursor.execute(query, (username,))
            result = cursor.fetchone()
            if result and result[0] == password_hash:
                return True
        except Exception as e:
            print(f"Error during authentication: {e}")
        return False

    def register_user(self, username, password_hash):
        try:
            cursor = self.connection.cursor()
            query = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
            cursor.execute(query, (username, password_hash))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error during registration: {e}")
        return False

if __name__ == '__main__':

    connection = sqlite3.connect('ChatRoom.db')

    try:
        cursor = connection.cursor()
        
        # 创建用户信息表
        create_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            bio TEXT DEFAULT '这个人暂无简介' CHECK(length(bio) <= 12)  -- 添加个人简介字段，长度不超过12个汉字
        )
        """
        cursor.execute(create_table_query)
        
        # 提交更改
        connection.commit()
    finally:
        connection.close()

    server = ChatServer('127.0.0.1', 12345)
    server.run()
