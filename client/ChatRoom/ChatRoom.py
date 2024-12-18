import sys
import json
import datetime
from PyQt5.QtWidgets import (QApplication, QWidget, QMenu, QAction, QListWidgetItem, QVBoxLayout
                            , QPushButton)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QColor
from qfluentwidgets import FluentIcon, RoundMenu
from .ChatRoom_ui import Ui_ChatRoom_Window
from .Class.UserCard import UserCard
from .Class.MessageCard import MessageCard


class ChatRoomWindow(QWidget):
    def __init__(self):
        super(ChatRoomWindow, self).__init__()
        self.ui = Ui_ChatRoom_Window()
        self.ui.setupUi(self)                                         # 1
        self.ui.EmojiButton.setIcon(FluentIcon.EMOJI_TAB_SYMBOLS)
        self.ui.FileButton.setIcon(FluentIcon.FOLDER)
        # self.ui.PhotoButton.setIcon(FluentIcon.PHOTO)
        self.ui.MessageScrollArea.setStyleSheet("QScrollArea{background: transparent; border: none}")
        self.ui.scrollAreaWidgetContents.setStyleSheet("QWidget#scrollAreaWidgetContents{background: transparent}")
        self.ui.MessageScrollArea.verticalScrollBar().rangeChanged.connect(
            lambda: self.ui.MessageScrollArea.verticalScrollBar().setValue(
                self.ui.MessageScrollArea.verticalScrollBar().maximum()
            )
        )
        # self.ui.MessageEdit.
        self.layout = QVBoxLayout(self.ui.scrollAreaWidgetContents)
        self.layout.setAlignment(Qt.AlignTop)

        self.add_user("世界聊天室", '这是一个公共频道')

        # 创建一个菜单
        self.emoji_menu = RoundMenu(self)

        self.emoji_menu.setItemHeight(40)

        # 添加一些emoji表情到菜单中
        emojis = ["😀", "😂", "😍", "😎", "😭", "😡"]
        for emoji in emojis:
            action = QAction(emoji, self)
            action.triggered.connect(lambda checked, e=emoji: self.insert_emoji(e))
            self.emoji_menu.addAction(action)

        # 将菜单添加到EmojiButton
        self.ui.EmojiButton.setMenu(self.emoji_menu)

        # 连接EmojiButton的点击信号到自定义槽函数
        self.ui.EmojiButton.clicked.connect(self.show_emoji_menu)
        

    def add_user(self, username, bio):
        user_card = UserCard(username, bio)
        list_item = QListWidgetItem(self.ui.UserListWidget)
        list_item.setSizeHint(user_card.sizeHint())
        self.ui.UserListWidget.addItem(list_item)
        self.ui.UserListWidget.setItemWidget(list_item, user_card)

    def add_message(self, sender, timestamp, content, username):
        timeStr = self.timestamp_to_str(timestamp)
        message_card = MessageCard(sender, timeStr, content)
        if sender == username:
            message_card.senderLabel.setTextColor('#0099FF')
            message_card.contentCard.setBackgroundColor(QColor('#0099FF'))
            message_card.contentLabel.setTextColor('#FFFFFF')
        self.layout.addWidget(message_card)
        self.ui.MessageScrollArea.verticalScrollBar().setValue(self.ui.MessageScrollArea.verticalScrollBar().maximum())

    def get_selected_user(self):
        current_item = self.ui.UserListWidget.currentItem()
        if current_item:
            user_card = self.ui.UserListWidget.itemWidget(current_item)
            if user_card:
                return user_card.titleLabel.text()
        return None

    def show_emoji_menu(self):
        # 获取EmojiButton的位置和大小
        button_rect = self.ui.EmojiButton.rect()
        # 计算菜单显示的位置，使其底部高于表情按钮
        menu_pos = self.ui.EmojiButton.mapToGlobal(button_rect.topLeft()) - QPoint(0, self.emoji_menu.sizeHint().height())
        # 显示菜单
        self.emoji_menu.exec_(menu_pos)

    def insert_emoji(self, emoji):
        # 在消息编辑框中插入表情
        cursor = self.ui.MessageEdit.textCursor()
        cursor.insertText(emoji)

    def timestamp_to_str(self, timestamp):
        dt = datetime.datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")

if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    w = ChatRoomWindow()
    w.show()
    sys.exit(app.exec_())