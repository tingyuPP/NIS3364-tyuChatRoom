import sys
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget
from ChatRoom import ChatRoomWindow
from qfluentwidgets import (MSFluentWindow, FluentIcon, NavigationItemPosition, Flyout,
                            HyperlinkButton, FlyoutView)
from PyQt5.QtCore import Qt, QPoint
from PersonInfo.PersonInfo_window import PersonInfoInterface

class MainWindow(MSFluentWindow):
    def __init__(self):
        super(MainWindow, self).__init__() 
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

    def center(self):
        # 获取屏幕的中心点
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2, (screen.height() - size.height()) // 2)

    def showFlyout(self):
        view = FlyoutView(
            title='关于本项目',
            content="本项目前端基于qfluentwidgets库，后端使用sqlite数据库，使用Socket实现实时通信。",
            image = 'image/fuhua.jpg',
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

if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())