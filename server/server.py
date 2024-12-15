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
        self.user_info = {}  # 用于存储用户简介的字典，键为用户名，值为简介

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
                print(f"Received data from {client_address}: {data}")
                message = json.loads(data)
                if message['type'] == 'login':
                    username = message['username']
                    password_hash = message['password_hash']
                    if self.authenticate_user(username, password_hash):
                        client_socket.send(json.dumps({'type': 'login', 'status': 'SUCCESS'}).encode('utf-8'))
                        self.clients[username] = client_socket
                        print(f"{username} connected from {client_address}")
                        self.broadcast_user_list()
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
                
                elif message['type'] == 'quit':
                    username = message['username']
                    self.clients.pop(username)
                    print(f"{username} disconnected")
                    self.broadcast_user_list()
                    break

                elif message['type'] == 'update_intro':
                    username = message['username']
                    new_intro = message['intro']
                    if self.update_intro(username, new_intro):
                        print("hello")
                        client_socket.send(json.dumps({'type': 'update_intro', 'status': 'SUCCESS'}).encode('utf-8'))
                        self.broadcast_user_list()
                    else:
                        print("Failed to update intro")
                        client_socket.send(json.dumps({'type': 'update_intro', 'status': 'FAILURE'}).encode('utf-8'))
                
                elif message['type'] == 'update_password':
                    old_password_hash = message['old_password_hash']
                    new_password_hash = message['new_password_hash']
                    if self.update_password(username, old_password_hash, new_password_hash):
                        client_socket.send(json.dumps({'type': 'update_password', 'status': 'SUCCESS'}).encode('utf-8'))
                    else:
                        client_socket.send(json.dumps({'type': 'update_password', 'status': 'FAILURE'}).encode('utf-8'))

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
    
    def update_intro(self, username, new_intro):
        try:
            print(f"Updating intro for {username} to {new_intro}")  # 添加调试信息
            cursor = self.connection.cursor()  # 使用相同的数据库连接和游标对象
            cursor.execute("UPDATE users SET bio = ? WHERE username = ?", (new_intro, username))
            self.connection.commit()
            print("Updated intro successfully")
            return True
        except sqlite3.Error as e:
            print(f"Error updating intro: {e}")
            return False
        
    def update_password(self, username, old_password_hash, new_password_hash):
        try:
            cursor = self.connection.cursor()
            # 检查旧密码哈希值是否正确
            cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
            result = cursor.fetchone()
            if result and result[0] == old_password_hash:
                # 更新密码哈希值
                cursor.execute("UPDATE users SET password_hash = ? WHERE username = ?", (new_password_hash, username))
                self.connection.commit()
                print(f"Password updated successfully for {username}")
                return True
            else:
                print(f"Old password is incorrect for {username}")
                return False
        except sqlite3.Error as e:
            print(f"Error updating password: {e}")
            return False
        
    def get_user_bio(self, username):
        try:
            cursor = self.connection.cursor()
            query = "SELECT bio FROM users WHERE username = ?"
            cursor.execute(query, (username,))
            result = cursor.fetchone()
            if result:
                return result[0]
            return '这个人暂无简介'
        except sqlite3.Error as e:
            print(f"Error getting user bio: {e}")
            return '这个人暂无简介'
        
    def broadcast_user_list(self):
        user_list = [{'username': username, 'bio': self.get_user_bio(username)} for username in self.clients.keys()]
        for client_socket in self.clients.values():
            try:
                client_socket.send(json.dumps({'type': 'update_user_list', 'users': user_list}).encode('utf-8'))
            except Exception as e:
                print(f"Error broadcasting user list: {e}")

if __name__ == '__main__':

    connection = sqlite3.connect('ChatRoom.db')

    try:
        cursor = connection.cursor()
        
        # 创建用户信息表
        create_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            bio TEXT DEFAULT '这个人暂无简介'   -- 添加个人简介字段，长度不超过12个汉字
        )
        """
        cursor.execute(create_table_query)
        
        # 提交更改
        connection.commit()
    finally:
        connection.close()

    server = ChatServer('127.0.0.1', 12345)
    server.run()
