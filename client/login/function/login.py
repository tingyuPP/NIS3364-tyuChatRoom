import socket
import threading
import json
from qfluentwidgets import Flyout, InfoBarIcon, FlyoutAnimationType
from .utils import hash_password


def _login(username, password, login_window):
    password_hash = hash_password(password)
    data = f"{username},{password_hash}"
    data = json.dumps({
        'type': 'login',
        'username': username,
        'password_hash': password_hash
    })
    
    try:
        # 连接到服务器
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('127.0.0.1', 12345))
        
        # 发送数据到服务器
        client_socket.send(data.encode('utf-8'))
        
        # 接收服务器返回的结果
        result = json.loads(client_socket.recv(1024).decode('utf-8'))
        client_socket.close()
        
        if result['status'] == 'FAILURE':
            Flyout.create(
                icon=InfoBarIcon.ERROR,
                title='登录失败',
                content="账号或密码错误！",
                target=login_window.LoginButton,
                parent=login_window,
                isClosable=True,
                aniType=FlyoutAnimationType.PULL_UP
            )
    except socket.error as e:
        Flyout.create(
            icon=InfoBarIcon.ERROR,
            title='连接失败',
            content="无法连接到服务器！",
            target=login_window.LoginButton,
            parent=login_window,
            isClosable=True,
            aniType=FlyoutAnimationType.PULL_UP
        )
    
def _register(username, password, login_window):
    password_hash = hash_password(password)
    data = f"{username},{password_hash}"
    data = json.dumps({
        'type': 'register',
        'username': username,
        'password_hash': password_hash
    })

    try:
        # 连接到服务器
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('127.0.0.1', 12345))
        
        # 发送数据到服务器
        client_socket.send(data.encode('utf-8'))
        
        # 接收服务器返回的结果
        result = json.loads(client_socket.recv(1024).decode('utf-8'))
        client_socket.close()
        
        if result['status'] == 'FAILURE':
            Flyout.create(
                icon=InfoBarIcon.ERROR,
                title='注册失败',
                content="用户名重复!",
                target=login_window.LoginButton,
                parent=login_window,
                isClosable=True,
                aniType=FlyoutAnimationType.PULL_UP
            )
        
        elif result['status'] == 'SUCCESS':
            Flyout.create(
                icon=InfoBarIcon.SUCCESS,
                title='注册成功',
                content="账号已成功注册！",
                target=login_window.LoginButton,
                parent=login_window,
                isClosable=True,
                aniType=FlyoutAnimationType.PULL_UP
            )
    except socket.error as e:
        Flyout.create(
            icon=InfoBarIcon.ERROR,
            title='连接失败',
            content="无法连接到服务器！",
            target=login_window.LoginButton,
            parent=login_window,
            isClosable=True,
            aniType=FlyoutAnimationType.PULL_UP
        )
    