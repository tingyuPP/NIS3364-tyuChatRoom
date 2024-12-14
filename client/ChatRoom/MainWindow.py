# -- coding: utf-8 --

import sys, os, json, threading
from PyQt5.QtWidgets import QWidget, QDesktopWidget
from .ChatRoom import ChatRoomWindow
from qfluentwidgets import (MSFluentWindow, FluentIcon, NavigationItemPosition, Flyout,
                            HyperlinkButton, FlyoutView, InfoBarIcon, FlyoutAnimationType)
from PyQt5.QtCore import Qt, QPoint, Q_ARG, QEvent, QObject, QCoreApplication
from .PersonInfo.PersonInfo_window import PersonInfoInterface

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from login.function.utils import Client 

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
        self.setFixedSize(1170, 900)
        # 添加子界面
        self.chatroomwindow = ChatRoomWindow()
        self.personalinfowindow = PersonInfoInterface()

        self.addSubInterface(self.chatroomwindow,FluentIcon.CHAT, "聊天室")
        self.addSubInterface(self.personalinfowindow, FluentIcon.EDIT, "编辑")
        self.center()                                         

        self.navigationInterface.addItem(
            routeKey="about",
            icon=FluentIcon.HELP,
            text="关于",
            onClick=self.showFlyout,
            selectable=False,
            position=NavigationItemPosition.BOTTOM
        )

        self.personalinfowindow.PersonalDescriptionCard.IntroReviseButton.clicked.connect(self.update_intro)

        self.receiver_thread = threading.Thread(target=self.receive_data, args=())
        self.receiver_thread.daemon = True
        self.receiver_thread.start()


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

    def show_success_flyout(self):
        Flyout.create(
            icon=InfoBarIcon.SUCCESS,
            title='修改成功',
            content="您已成功修改个人简介。",
            target=self.personalinfowindow.PersonalDescriptionCard.IntroReviseButton,
            isClosable=True,
            aniType=FlyoutAnimationType.PULL_UP
        )

    def show_failure_flyout(self):
        Flyout.create(
            icon=InfoBarIcon.ERROR,
            title='修改失败',
            content="个人简介应当少于12个字！",
            target=self.personalinfowindow.PersonalDescriptionCard.IntroReviseButton,
            isClosable=True,
            aniType=FlyoutAnimationType.PULL_UP
        )

    def update_intro(self):
        # 发送更新个人简介的请求到服务器
        new_intro = self.personalinfowindow.PersonalDescriptionCard.IntroTextEdit.text()
        data = json.dumps({
            'type': 'update_intro',
            'username': self.username,
            'intro': new_intro
        })
        self.client.send_data(data)

    def handle_data(self, data):
        # 处理接收到的数据
        print(f"Received data: {data}")
        # 根据数据类型执行相应操作
        # ...
        try:
            message = json.loads(data)
            if message['type'] == 'update_intro':
                if message['status'] == 'SUCCESS':
                    print("修改成功")
                    post_update_ui(self.show_success_flyout)
                elif message['status'] == 'FAILURE':
                    print("修改失败")
                    post_update_ui(self.show_failure_flyout)
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