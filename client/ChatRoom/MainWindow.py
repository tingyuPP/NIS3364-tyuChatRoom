# -- coding: utf-8 --

import sys, os, json, threading, base64, socket
from PyQt5.QtWidgets import QDesktopWidget,QFileDialog
from .ChatRoom import ChatRoomWindow
from qfluentwidgets import (MSFluentWindow, FluentIcon, NavigationItemPosition, Flyout,
                            HyperlinkButton, FlyoutView, InfoBarIcon, FlyoutAnimationType,
                            MessageBox)
from PyQt5.QtCore import Qt, QPoint, QEvent, QObject, QCoreApplication
from PyQt5.QtGui import QIcon
from .PersonInfo.PersonInfo_window import PersonInfoInterface

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from login.function.utils import Client, hash_password, is_valid_password

class UpdateUIEvent(QEvent):
    def __init__(self, callback, *args):
        super().__init__(QEvent.User)
        self.callback = callback
        self.args = args

    def execute(self):
        self.callback(*self.args)

class UIUpdater(QObject):
    def event(self, event):
        if isinstance(event, UpdateUIEvent):
            event.execute()
            return True
        return super().event(event)

ui_updater = UIUpdater()

def post_update_ui(callback, *args):
    event = UpdateUIEvent(callback, *args)
    QCoreApplication.postEvent(ui_updater, event)

class MainWindow(MSFluentWindow):
    def __init__(self, client: Client, username):
        super(MainWindow, self).__init__() 
        self.client = client
        self.username = username
        self.setWindowTitle("tyuChatRoom")
        self.setWindowIcon(QIcon('image/logo.png'))
        self.setFixedSize(1177, 900)
        # 添加子界面
        self.chatroomwindow = ChatRoomWindow()
        self.personalinfowindow = PersonInfoInterface()

        self.addSubInterface(self.chatroomwindow,FluentIcon.CHAT, "聊天")
        self.addSubInterface(self.personalinfowindow, FluentIcon.SETTING, "设置")
        self.center() 

        self.navigationInterface.addItem(
            routeKey="about",
            icon=FluentIcon.HELP,
            text="关于",
            onClick=self.showFlyout,
            selectable=False,
            position=NavigationItemPosition.BOTTOM
        )

        self.chatroomwindow.ui.SendMessageButton.clicked.connect(self.send_message)
        self.chatroomwindow.ui.FileButton.clicked.connect(self.open_file_dialog)

        self.personalinfowindow.PersonalDescriptionCard.IntroReviseButton.clicked.connect(self.update_intro)
        self.personalinfowindow.PasswordChangeCard.PasswordReviseButton.clicked.connect(self.update_password)

        self.receiver_thread = threading.Thread(target=self.receive_data, args=())
        self.receiver_thread.daemon = True
        self.receiver_thread.start()
        self.chatroomwindow.ui.UserListWidget.itemClicked.connect(self.on_user_selected)

    def center(self):
        # 获取屏幕的中心点
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2, (screen.height() - size.height()) // 2)

    def showFlyout(self):
        view = FlyoutView(
            title='关于本项目',
            content="本项目前端基于qfluentwidgets库，后端使用sqlite数据库，使用Socket实现实时通信。",
            image = 'image/fuhua2.jpg',
            isClosable=True
        ) 

        GithubButton = HyperlinkButton(FluentIcon.LINK, "https://github.com/tingyuPP/NIS3364-tyuChatRoom", "仓库地址")

        GithubButton.setFixedWidth(120)

        view.addWidget(GithubButton, align=Qt.AlignRight)

        # 调整布局
        view.widgetLayout.insertSpacing(1, 5)
        view.widgetLayout.addSpacing(5)

        window_geometry = self.geometry()
        window_bottom_left = QPoint(window_geometry.left(), window_geometry.bottom() - 400)

        # 显示弹出窗口
        w = Flyout.make(view, window_bottom_left, self)
        view.closed.connect(w.close)

    def show_success_intro_flyout(self):
        Flyout.create(
            icon=InfoBarIcon.SUCCESS,
            title='修改成功',
            content="您已成功修改个人简介。",
            target=self.personalinfowindow.PersonalDescriptionCard.IntroReviseButton,
            isClosable=True,
            aniType=FlyoutAnimationType.PULL_UP
        )

    def show_failure_intro_flyout(self):
        Flyout.create(
            icon=InfoBarIcon.ERROR,
            title='修改失败',
            content="个人简介应当少于12个字！",
            target=self.personalinfowindow.PersonalDescriptionCard.IntroReviseButton,
            isClosable=True,
            aniType=FlyoutAnimationType.PULL_UP
        )
    
    def show_success_password_flyout(self):
        Flyout.create(
            icon=InfoBarIcon.SUCCESS,
            title='修改成功',
            content="您已成功修改密码。",
            target=self.personalinfowindow.PasswordChangeCard.PasswordReviseButton,
            isClosable=True,
            aniType=FlyoutAnimationType.PULL_UP
        )

    def show_failure_password_flyout(self):
        Flyout.create(
            icon=InfoBarIcon.ERROR,
            title='修改失败',
            content="旧密码错误！",
            target=self.personalinfowindow.PasswordChangeCard.PasswordReviseButton,
            isClosable=True,
            aniType=FlyoutAnimationType.PULL_UP
        )

    def on_user_selected(self):
        selected_user = self.chatroomwindow.get_selected_user()
        if selected_user == "世界聊天室":
            data = json.dumps({
                'type': 'refresh_world_messages',
                'username': self.username
            })
        else:
            data = json.dumps({
                'type': 'refresh_messages',
                'username': self.username,
                'chat': selected_user
            })
        self.client.send_data(data)

    def update_intro(self):
        # 发送更新个人简介的请求到服务器
        new_intro = self.personalinfowindow.PersonalDescriptionCard.IntroTextEdit.text()

        if not new_intro:
            Flyout.create(
                icon=InfoBarIcon.ERROR,
                title='修改失败',
                content="个人简介不能为空！",
                target=self.personalinfowindow.PersonalDescriptionCard.IntroReviseButton,
                isClosable=True,
                aniType=FlyoutAnimationType.PULL_UP
            )
            return

        data = json.dumps({
            'type': 'update_intro',
            'username': self.username,
            'intro': new_intro
        })
        self.client.send_data(data)
        self.personalinfowindow.PersonalDescriptionCard.IntroTextEdit.clear()

    def update_password(self):
        # 发送更新密码的请求到服务器
        old_password = self.personalinfowindow.PasswordChangeCard.OldPasswordEdit.text()
        new_password = self.personalinfowindow.PasswordChangeCard.NewPasswordEdit.text()
        confirm_password = self.personalinfowindow.PasswordChangeCard.ConfirmPasswordEdit.text()

        if not old_password or not new_password or not confirm_password:
            Flyout.create(
                icon=InfoBarIcon.ERROR,
                title='修改失败',
                content="有字段为空！",
                target=self.personalinfowindow.PasswordChangeCard.PasswordReviseButton,
                isClosable=True,
                aniType=FlyoutAnimationType.PULL_UP
            )
            return

        if not is_valid_password(new_password):
            Flyout.create(
                icon=InfoBarIcon.ERROR,
                title='修改失败',
                content="新密码长度应只含字母和数字，且不少于8位！",
                target=self.personalinfowindow.PasswordChangeCard.PasswordReviseButton,
                isClosable=True,
                aniType=FlyoutAnimationType.PULL_UP
            )
            return

        if new_password != confirm_password:
            Flyout.create(
                icon=InfoBarIcon.ERROR,
                title='修改失败',
                content="两次输入的新密码不一致！",
                target=self.personalinfowindow.PasswordChangeCard.PasswordReviseButton,
                isClosable=True,
                aniType=FlyoutAnimationType.PULL_UP
            )
            return
        
        old_password_hash = hash_password(old_password)
        new_password_hash = hash_password(new_password)

        data = json.dumps({
            'type': 'update_password',
            'username': self.username,
            'old_password_hash': old_password_hash,
            'new_password_hash': new_password_hash,
        })
        self.client.send_data(data)
        self.personalinfowindow.PasswordChangeCard.OldPasswordEdit.clear()
        self.personalinfowindow.PasswordChangeCard.NewPasswordEdit.clear()
        self.personalinfowindow.PasswordChangeCard.ConfirmPasswordEdit.clear()

    def update_user_list(self, users):
        current_chat = self.chatroomwindow.get_selected_user()
        self.chatroomwindow.ui.UserListWidget.clear()
        
        # 添加 "世界聊天室" 选项
        self.chatroomwindow.add_user("世界聊天室", "这是一个公共聊天室")

        # 添加其他用户
        user_list = [user['username'] for user in users]
        for user in users:
            self.chatroomwindow.add_user(user['username'], user['bio'])

        if current_chat not in user_list and current_chat != "世界聊天室":
            self.clear_messages()
        

    def send_message(self):
        receiver = self.chatroomwindow.get_selected_user()
        message = self.chatroomwindow.ui.MessageEdit.toPlainText()
        if not receiver:
            Flyout.create(
                icon=InfoBarIcon.ERROR,
                title='发送失败',
                content="请选择一个会话！",
                target=self.chatroomwindow.ui.SendMessageButton,
                isClosable=True,
                aniType=FlyoutAnimationType.PULL_UP
            )
            return
        if not message:
            Flyout.create(
                icon=InfoBarIcon.ERROR,
                title='发送失败',
                content="消息不能为空！",
                target=self.chatroomwindow.ui.SendMessageButton,
                isClosable=True,
                aniType=FlyoutAnimationType.PULL_UP
            )
            return
        if len(message) > 100:
            Flyout.create(
                icon=InfoBarIcon.ERROR,
                title='发送失败',
                content="消息长度应不超过100字！",
                target=self.chatroomwindow.ui.SendMessageButton,
                isClosable=True,
                aniType=FlyoutAnimationType.PULL_UP
            )
            return
        self.chatroomwindow.ui.MessageEdit.clear()
        if receiver == "世界聊天室":
            data = json.dumps({
                'type': 'world_message',
                'sender': self.username,
                'content': message
            })
        else:
            data = json.dumps({
                'type': 'message',
                'sender': self.username,
                'receiver': receiver,
                'content': message
            })
        self.client.send_data(data)

    def clear_messages(self):
        for i in reversed(range(self.chatroomwindow.layout.count())):
            widget = self.chatroomwindow.layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

    def add_messages(self, messages):
        # print(f"add message: {messages}")
        for message in messages:
            self.chatroomwindow.add_message(message['sender'], message['timestamp'], message['content'], self.username)

    def add_one_message(self, message):
        if message['sender'] == self.chatroomwindow.get_selected_user() or message['receiver'] == self.chatroomwindow.get_selected_user():
            self.chatroomwindow.add_message(message['sender'], message['timestamp'], message['content'], self.username)

    def add_one_world_message(self, message):
        if '世界聊天室' == self.chatroomwindow.get_selected_user():
            self.chatroomwindow.add_message(message['sender'], message['timestamp'], message['content'], self.username)

    def open_file_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_path, _ = QFileDialog.getOpenFileName(self, "选择文件", "", "所有文件 (*);;文本文件 (*.txt)", options=options)
        if file_path:
            print(f"Selected file: {file_path}")
            # 这里可以添加处理选中文件的逻辑，例如发送文件
            self.send_file(file_path)

    def send_file(self, file_path):
        receiver = self.chatroomwindow.get_selected_user()
        if not receiver:
            Flyout.create(
                icon=InfoBarIcon.ERROR,
                title='发送失败',
                content="请选择一个会话！",
                target=self.chatroomwindow.ui.FileButton,
                isClosable=True,
                aniType=FlyoutAnimationType.PULL_UP
            )
            return
        elif receiver == "世界聊天室":
            Flyout.create(
                icon=InfoBarIcon.ERROR,
                title='发送失败',
                content="无法向世界聊天室发送文件！",
                target=self.chatroomwindow.ui.FileButton,
                isClosable=True,
                aniType=FlyoutAnimationType.PULL_UP
            )
            return
        
        # 读取文件内容并计算文件大小
        file_size = os.path.getsize(file_path)
        file_size_str = self.format_file_size(file_size)
        with open(file_path, 'rb') as file:
            file_content = file.read()

        file_content_base64 = base64.b64encode(file_content).decode('utf-8')

        # 构建文件传输消息
        file_name = os.path.basename(file_path)
        message = {
            'type': 'file_transfer',
            'sender': self.username,
            'receiver': receiver,
            'file_name': file_name,
            'file_path': file_path,
            'file_size': file_size_str,
            # 'file_content': file_content_base64  # 将二进制文件内容转换为字符串
        }
        self.client.send_data(json.dumps(message))

    def send_file_data(self, receiver_address, file_path):
        receiver_ip = receiver_address[0]
        receiver_port = 19999  # 固定端口号
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((receiver_ip, receiver_port))
            with open(file_path, 'rb') as file:
                while True:
                    chunk = file.read(4096)
                    if not chunk:
                        break
                    s.send(chunk)
        print(f"File {file_path} sent to {receiver_address}")
    
    def receive_file_data(self, file_name, save_path):
        def receive_file():
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', 19999))  # 绑定到一个随机端口
                s.listen(1)

                conn, addr = s.accept()
                print("Hello receive_file_data")
                with conn:
                    with open(save_path, 'wb') as file:
                        while True:
                            chunk = conn.recv(4096)
                            if not chunk:
                                break
                            file.write(chunk)
            print(f"File received and saved to {save_path}")

        # 在单独的线程中运行接收文件的逻辑
        threading.Thread(target=receive_file).start()

    def format_file_size(self, size):
        # 将文件大小格式化为 KB、MB、GB 等
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
            
    def show_file_transfer_request(self, sender, file_name, file_size, file_path_hash):
        w = MessageBox("文件传输请求", f"{sender} 向您发送了文件：{file_name} ({file_size})，是否接收？", self)
        if w.exec():
            # 接收文件
            # file_content = base64.b64decode(file_content)
            options = QFileDialog.Options()
            options |= QFileDialog.ReadOnly
            save_path, _ = QFileDialog.getSaveFileName(self, "保存文件", file_name, "所有文件 (*)", options=options)
            # if save_path:
            self.client.send_data(json.dumps({
                'type': 'file_transfer_response',
                'sender': sender,
                'receiver': self.username,
                'file_name': file_name,
                'status': 'ACCEPT',
                'file_path_hash': file_path_hash
            }))
            print("Hello here")
            self.receive_file_data(file_name, save_path)
                # with open(save_path, 'wb') as file:
                    # file.write(file_content)


        else:
            # 拒绝接收文件
            self.client.send_data(json.dumps({
                'type': 'file_transfer_response',
                'sender': sender,
                'receiver': self.username,
                'file_name': file_name,
                'status': 'REJECT'
            }))
    
    def show_file_transfer_status(self, receiver, status):
        if status == 'ACCEPT':
            w = MessageBox("文件传输结果", f"{receiver} 已接收文件。", self)
            w.cancelButton.hide()
            w.buttonLayout.insertStretch(1)
            if w.exec():
                pass
            else:
                pass
        else:
            w = MessageBox("文件传输结果", f"{receiver} 拒绝接收文件。", self)
            w.cancelButton.hide()
            w.buttonLayout.insertStretch(1)
            if w.exec():
                pass
            else:
                pass

    def handle_data(self, data):
        # 处理接收到的数据
        print(f"Received data: {data}")
        # 根据数据类型执行相应操作
        # ...
        try:
            message = json.loads(data)
            if message['type'] == 'update_intro':
                if message['status'] == 'SUCCESS':
                    post_update_ui(self.show_success_intro_flyout)
                elif message['status'] == 'FAILURE':
                    post_update_ui(self.show_failure_intro_flyout)

            elif message['type'] == 'update_password':
                if message['status'] == 'SUCCESS':
                    post_update_ui(self.show_success_password_flyout)
                elif message['status'] == 'FAILURE':
                    post_update_ui(self.show_failure_password_flyout)

            elif message['type'] == 'update_user_list':
                users = message['users']
                post_update_ui(self.update_user_list, users)

            elif message['type'] == 'refresh_messages':
                post_update_ui(self.clear_messages)

            elif message['type'] == 'add_messages':
                post_update_ui(self.add_messages, message['messages'])

            elif message['type'] == 'new_message':
                post_update_ui(self.add_one_message, message['message'])

            elif message['type'] == 'new_world_message':
                post_update_ui(self.add_one_world_message, message['message'])

            elif message['type'] == 'file_transfer_request':
                # 接收到文件传输请求
                sender = message['sender']
                file_name = message['file_name']
                file_size = message['file_size']
                file_path_hash = message['file_path_hash']
                # file_content = message['file_content']
                # 显示文件传输请求的弹出窗口
                post_update_ui(self.show_file_transfer_request, sender, file_name, file_size, file_path_hash)
            
            elif message['type'] == 'file_transfer_status':
                receiver = message['receiver']
                status = message['status']
                filepath = message['file_path']
                if status == 'ACCEPT':
                    receiver_address = (message['receiver_address'])
                    self.send_file_data(receiver_address, filepath)
                post_update_ui(self.show_file_transfer_status, receiver, status)

        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}") 

    def receive_data(self):
        while True:
            try:
                data = self.client.receive_data()
                if data:  # 检查数据是否为空
                    self.handle_data(data)
                else:
                    print("Received empty data")
            except Exception as e:
                print(f"Error receiving data: {e}")
                break

    def closeEvent(self, event):
        # 发送退出信号到服务器
        data = json.dumps({
            'type': 'quit',
            'username': self.username
        })
        self.client.send_data(data)
        self.client.close()
        event.accept()