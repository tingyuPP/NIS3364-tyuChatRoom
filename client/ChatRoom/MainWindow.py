import sys
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget
from ChatRoom import ChatRoomWindow
from qfluentwidgets import MSFluentWindow, FluentIcon
from PyQt5.QtCore import Qt

class MainWindow(MSFluentWindow):
    def __init__(self):
        super(MainWindow, self).__init__() 
        self.setWindowTitle("tyuChatRoom")
        self.setFixedSize(1170, 900)
        # 添加子界面
        self.chatroomwindow = ChatRoomWindow()

        self.addSubInterface(self.chatroomwindow,FluentIcon.CHAT, "聊天室")
        self.center()                                         

    def center(self):
        # 获取屏幕的中心点
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2, (screen.height() - size.height()) // 2)


if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())