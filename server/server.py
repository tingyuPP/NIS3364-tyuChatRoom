import socket
import threading
import sqlite3

class ChatServer:
    def __init__(self, host, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(5)
        self.clients = {}  # 用于存储在线用户的字典，键为用户名，值为套接字

        # 连接到SQLite数据库
        self.connection = sqlite3.connect('chat_app.db', check_same_thread=False)

    def run(self):
        pass


if __name__ == '__main__':

    connection = sqlite3.connect('ChatRoom.db')

    try:
        cursor = connection.cursor()
        
        # 创建用户信息表
        create_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL
        )
        """
        cursor.execute(create_table_query)
        
        # 提交更改
        connection.commit()
    finally:
        connection.close()

    server = ChatServer('127.0.0.1', 12345)
    server.run()
