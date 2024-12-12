import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from qframelesswindow import FramelessWindow, StandardTitleBar
from qfluentwidgets import setThemeColor
from test_ui import Ui_LoginWindow

from function.login import __login, __register



class LoginWindow(FramelessWindow, Ui_LoginWindow):
    def __init__(self):
        super(LoginWindow, self).__init__()
        self.setupUi(self)                      
        
        self.setTitleBar(StandardTitleBar(self))
        self.titleBar.raise_()        # 1    # 2
        self.setWindowTitle("login")

        self.setFixedSize(1327, 629)

        setThemeColor("#EE82EE")
        
        self.center()
        self.titleBar.titleLabel.setStyleSheet("""
            QLabel{
                background: transparent;
                font: 13px 'Segoe UI';
                padding: 0 4px;
                color: white;
            }
        """)

        self.LoginButton.clicked.connect(self.login)
        self.RegisterButton.clicked.connect(self.register)

    def center(self):
        # 获取屏幕的中心点
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2, (screen.height() - size.height()) // 2)
        
    def login(self):
        username = self.UsernameEdit.text()
        password = self.PasswordEdit.text()
        __login(username, password)
    
    def register(self):
        username = self.UsernameEdit.text()
        password = self.PasswordEdit.text()
        __register(username, password)

if __name__ == '__main__':

    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)
    demo = LoginWindow()
    demo.show()
    sys.exit(app.exec_())