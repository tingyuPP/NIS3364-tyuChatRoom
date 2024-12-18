import sys
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from qframelesswindow import FramelessWindow, StandardTitleBar
from qfluentwidgets import setThemeColor, Flyout, InfoBarIcon, FlyoutAnimationType
from login_window_ui import Ui_LoginWindow

from function.login import _login, _register
from function.utils import is_valid_password



class LoginWindow(FramelessWindow, Ui_LoginWindow):
    def __init__(self):
        super(LoginWindow, self).__init__()
        self.setupUi(self)                      
        
        self.setTitleBar(StandardTitleBar(self))
        self.titleBar.raise_()        # 1    # 2
        self.setWindowTitle("login")
        self.setWindowIcon(QIcon('image/logo.png'))
        self.setFixedSize(1327, 629)

        #setThemeColor("#EE82EE")
        
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
        if not username or not password:
            Flyout.create(
            icon=InfoBarIcon.ERROR,
            title='输入有误',
            content="账号或密码不能为空！",
            target=self.LoginButton,
            parent=self,
            isClosable=True,
            aniType=FlyoutAnimationType.PULL_UP
            )
            return
        _login(username, password, self)
    
    def register(self):
        username = self.UsernameEdit.text()
        password = self.PasswordEdit.text()
        if not username or not password:
            Flyout.create(
            icon=InfoBarIcon.ERROR,
            title='输入有误',
            content="账号或密码不能为空！",
            target=self.RegisterButton,
            parent=self,
            isClosable=True,
            aniType=FlyoutAnimationType.PULL_UP
            )
            return
        if not is_valid_password(password):
            Flyout.create(
            icon=InfoBarIcon.ERROR,
            title='输入有误',
            content="密码长度应不少于8位，且只含字母和数字！",
            target=self.RegisterButton,
            parent=self,
            isClosable=True,
            aniType=FlyoutAnimationType.PULL_UP
            )
            return
        _register(username, password, self)

if __name__ == '__main__':

    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)
    demo = LoginWindow()
    demo.show()
    sys.exit(app.exec_())