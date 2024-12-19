import socket
import threading
import sqlite3
import json
import time
import hashlib

class ChatServer:
    def __init__(self, host, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(5)
        self.clients = {}  # 用于存储在线用户的字典，键为用户名，值为套接字
        self.file_path_map = {}

        # 连接到SQLite数据库
        self.connection = sqlite3.connect('ChatRoom.db', check_same_thread=False)

    def run(self):
        print("Server started...")
        while True:
            client_socket, client_address = self.server.accept()
            threading.Thread(target=self.handle_client, args=(client_socket, client_address)).start()

    def handle_client(self, client_socket, client_address):
        buffer = "" # 用于存储接收到的数据
        try:
            while True:
                try:
                    data = client_socket.recv(1024).decode('utf-8')
                    if not data:
                        break
                    buffer += data
                    while "\n" in buffer:
                        message, buffer = buffer.split("\n", 1)
                        print(f"Received data from {client_address}: {message}")
                        message = json.loads(message)

                        if message['type'] == 'login':
                            username = message['username']
                            password_hash = message['password_hash']
                            if self.authenticate_user(username, password_hash):
                                if username in self.clients:
                                    client_socket.send((json.dumps({'type': 'login', 'status': 'ALREADY_LOGGED_IN'}) + "\n").encode('utf-8'))
                                    client_socket.close()
                                    break
                                else:
                                    client_socket.send((json.dumps({'type': 'login', 'status': 'SUCCESS'}) + "\n").encode('utf-8'))
                                    # self.clients[username] = client_socket
                                    # print(f"{username} connected from {client_address}")
                                    # self.broadcast_user_list()
                            else:
                                client_socket.send((json.dumps({'type': 'login', 'status': 'FAILURE'}) + "\n").encode('utf-8'))
                                client_socket.close()
                                break
                        
                        elif message['type'] == 'init':
                            username = message['username']
                            self.clients[username] = client_socket
                            print(f"{username} connected from {client_address}")
                            self.broadcast_user_list()

                        elif message['type'] == 'register':
                            username = message['username']
                            password_hash = message['password_hash']
                            if self.register_user(username, password_hash):
                                client_socket.send((json.dumps({'type': 'register', 'status': 'SUCCESS'}) + "\n").encode('utf-8'))
                            else:
                                client_socket.send((json.dumps({'type': 'register', 'status': 'FAILURE'}) + "\n").encode('utf-8'))
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
                                client_socket.send((json.dumps({'type': 'update_intro', 'status': 'SUCCESS'}) + "\n").encode('utf-8'))
                                self.broadcast_user_list()
                            else:
                                print("Failed to update intro")
                                client_socket.send((json.dumps({'type': 'update_intro', 'status': 'FAILURE'}) + "\n").encode('utf-8'))
                        
                        elif message['type'] == 'update_password':
                            old_password_hash = message['old_password_hash']
                            new_password_hash = message['new_password_hash']
                            if self.update_password(username, old_password_hash, new_password_hash):
                                client_socket.send((json.dumps({'type': 'update_password', 'status': 'SUCCESS'}) + "\n").encode('utf-8'))
                            else:
                                client_socket.send((json.dumps({'type': 'update_password', 'status': 'FAILURE'}) + "\n").encode('utf-8'))

                        elif message['type'] == 'message':
                            print("Received message")
                            sender = message['sender']
                            receiver = message['receiver']
                            content = message['content']
                            print(f"Received message from {sender} to {receiver}: {content}")
                            timestamp = self.save_message(sender, receiver, content)
                            new_message = {'sender': sender, 'receiver': receiver, 'content': content, 'timestamp': timestamp}
                            if sender == receiver:
                                response = {'type': 'new_message', 'message': new_message}
                                client_socket.send((json.dumps(response) + "\n").encode('utf-8'))
                            elif receiver == '世界聊天室':
                                response = {'type': 'new_message', 'message': new_message}
                                for client__socket in self.clients.values():
                                    client__socket.send((json.dumps(response) + "\n").encode('utf-8'))
                            else:
                                if sender in self.clients:
                                    response = {'type': 'new_message', 'message': new_message}
                                    self.clients[sender].send((json.dumps(response) + "\n").encode('utf-8'))
                                if receiver in self.clients:
                                    response = {'type': 'new_message', 'message': new_message}
                                    self.clients[receiver].send((json.dumps(response) + "\n").encode('utf-8'))

                        elif message['type'] == 'refresh_messages':
                            client_socket.send((json.dumps({'type': 'refresh_messages', 'status': 'SUCCESS'}) + "\n").encode('utf-8'))
                            username = message['username']
                            chat = message['chat']
                            messages = self.giveback_messages(username, chat)
                            response = {'type': 'add_messages', 'messages': messages}
                            client_socket.send((json.dumps(response) + "\n").encode('utf-8'))
                        
                        elif message['type'] == 'refresh_world_messages':
                            client_socket.send((json.dumps({'type': 'refresh_messages', 'status': 'SUCCESS'}) + "\n").encode('utf-8'))
                            messages = self.giveback_world_messages()
                            response = {'type': 'add_messages', 'messages': messages}
                            client_socket.send((json.dumps(response) + "\n").encode('utf-8'))

                        elif message['type'] == 'file_transfer':
                            sender = message['sender']
                            receiver = message['receiver']
                            filename = message['file_name']
                            filesize = message['file_size']
                            filepath = message['file_path']
                            # file_content = message['file_content']
                            # 计算文件路径的哈希值
                            file_path_hash = hashlib.sha256(filepath.encode('utf-8')).hexdigest()
                            # 存储哈希值与文件路径的对应关系
                            self.file_path_map[file_path_hash] = filepath 
        
                            print(f"Received file from {sender} to {receiver}: {filename}")

                            confirm_request = {
                                'type': 'file_transfer_request',
                                'sender': sender,
                                'file_name': filename,
                                'file_size': filesize,
                                'file_path_hash': file_path_hash
                            }
                            self.clients[receiver].send((json.dumps(confirm_request) + "\n").encode('utf-8'))

                        elif message['type'] == 'file_transfer_response':
                            sender = message['sender']
                            receiver = message['receiver']
                            filename = message['file_name']
                            response = message['status']
                            file_path_hash = message['file_path_hash']
                            if response == 'ACCEPT':
                                print(f"{receiver} accepted the file transfer request from {sender}")
                                accept_message = {
                                    'type': 'file_transfer_status',
                                    'status': 'ACCEPT',
                                    'receiver': receiver,
                                    'receiver_address': self.clients[receiver].getpeername(),
                                    'file_path': self.file_path_map[file_path_hash]
                                }
                                #print(filepath)
                                self.clients[sender].send((json.dumps(accept_message) + "\n").encode('utf-8'))
                            else:
                                print(f"{receiver} declined the file transfer request from {sender}")
                                reject_message = {
                                    'type': 'file_transfer_status',
                                    'status': 'REJECT',
                                    'receiver': receiver,
                                    'file_path': self.file_path_map[file_path_hash]
                                }
                                self.clients[sender].send((json.dumps(reject_message) + "\n").encode('utf-8'))

                except socket.error as e:
                    print(f"Socket error: {e}")
                    break
        except Exception as e:
            print(f"Error handling client message: {e}")

        finally:
            # 在捕获到异常或客户端断开连接时，从在线列表中删除客户端
            for username, sock in list(self.clients.items()):
                if sock == client_socket:
                    del self.clients[username]
                    print(f"{username} removed from online list")
                    self.broadcast_user_list()
                    break
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
                client_socket.send((json.dumps({'type': 'update_user_list', 'users': user_list}) + "\n").encode('utf-8'))
            except Exception as e:
                print(f"Error broadcasting user list: {e}")
    
    def save_message(self, sender, receiver, content):
        try:
            cursor = self.connection.cursor()
            timestamp = int(time.time())  # 获取当前时间的 Linux 时间戳
            query = "INSERT INTO messages (sender, receiver, content, timestamp) VALUES (?, ?, ?, ?)"
            cursor.execute(query, (sender, receiver, content, timestamp))
            self.connection.commit()
            print(f"Message from {sender} to {receiver} saved successfully.")
            return timestamp
        except sqlite3.Error as e:
            print(f"Error saving message: {e}")
    
    def save_world_message(self, sender, content):
        try:
            cursor = self.connection.cursor()
            timestamp = int(time.time())
            query = "INSERT INTO world_messages (sender, content, timestamp) VALUES (?, ?, ?)"
            cursor.execute(query, (sender, content, timestamp))
            self.connection.commit()
            print(f"World message from {sender} saved successfully.")
            return timestamp
        except sqlite3.Error as e:
            print(f"Error saving world message: {e}")

    def giveback_messages(self, username, chat):
        try:
            cursor = self.connection.cursor()
            query = """
            SELECT sender, receiver, content, timestamp FROM messages
            WHERE (sender = ? AND receiver = ?) OR (sender = ? AND receiver = ?)
            ORDER BY timestamp
            """
            cursor.execute(query, (username, chat, chat, username))
            messages = cursor.fetchall()
            return [{'sender': msg[0], 'receiver': msg[1], 'content': msg[2], 'timestamp': msg[3]} for msg in messages]
        except sqlite3.Error as e:
            print(f"Error getting messages: {e}")
            return []
    
    def giveback_world_messages(self):
        try:
            cursor = self.connection.cursor()
            query = """
            SELECT sender, content, timestamp 
            FROM messages 
            WHERE receiver = '世界聊天室' 
            ORDER BY timestamp
            """
            cursor.execute(query)
            messages = cursor.fetchall()
            return [{'sender': msg[0], 'content': msg[1], 'timestamp': msg[2]} for msg in messages]
        except sqlite3.Error as e:
            print(f"Error getting world messages: {e}")
            return []

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
        
        # 创建消息表
        create_message_table_query = """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT NOT NULL,
            receiver TEXT NOT NULL,
            content TEXT NOT NULL CHECK(length(content) <= 100),
            timestamp INTEGER NOT NULL,
            FOREIGN KEY (sender) REFERENCES users(username),
            FOREIGN KEY (receiver) REFERENCES users(username)
        )
        """
        cursor.execute(create_message_table_query)
        
        # 插入“世界聊天室”用户
        insert_world_chatroom_query = """
        INSERT OR IGNORE INTO users (username, password_hash, bio)
        VALUES ('世界聊天室', '111', '这是一个公共聊天室')
        """
        cursor.execute(insert_world_chatroom_query)
        
        # 提交更改
        connection.commit()
    finally:
        connection.close()

    server = ChatServer('127.0.0.1', 12345)
    server.run()
