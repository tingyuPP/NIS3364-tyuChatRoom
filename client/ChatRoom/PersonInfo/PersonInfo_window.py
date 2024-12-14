import sys
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import (ScrollArea, SettingCardGroup, FolderListSettingCard, HeaderCardWidget, ExpandLayout,
                            LineEdit, PrimaryPushButton)
from PyQt5.QtWidgets import QWidget, QLabel, QFontDialog, QFileDialog, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QMenu, QAction


class PersonInfoInterface(ScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("PersonInfoInterface")
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        # setting label
        self.settingLabel = QLabel(self.tr("设置"), self)

        self.PersonalInfoGroup = SettingCardGroup(
            self.tr("修改个人信息"), self.scrollWidget)
        self.PersonalDescriptionCard = HeaderCardWidget()
        self.PersonalDescriptionCard.setFixedHeight(160)
        self.PersonalDescriptionCard.setTitle(self.tr("修改个人简介"))

        self.PersonalDescriptionCard.IntroTextEdit = LineEdit()
        self.PersonalDescriptionCard.IntroTextEdit.setFixedHeight(40)
        self.PersonalDescriptionCard.IntroTextEdit.setPlaceholderText(
            self.tr("请输入新的个人简介"))
        self.PersonalDescriptionCard.IntroReviseButton = PrimaryPushButton(FIF.UPDATE, '确认修改')

        self.PersonalDescriptionCard.hBoxLayout = QHBoxLayout()

        self.PersonalDescriptionCard.hBoxLayout.setSpacing(10)
        self.PersonalDescriptionCard.hBoxLayout.addWidget(self.PersonalDescriptionCard.IntroTextEdit)
        self.PersonalDescriptionCard.hBoxLayout.addWidget(self.PersonalDescriptionCard.IntroReviseButton)

        self.PersonalDescriptionCard.viewLayout.addLayout(self.PersonalDescriptionCard.hBoxLayout)

                # 初始化修改密码卡片
        self.PasswordChangeCard = HeaderCardWidget()
        self.PasswordChangeCard.setFixedHeight(150)
        self.PasswordChangeCard.setTitle(self.tr("修改密码"))
        self.PasswordChangeCard.OldPasswordEdit = LineEdit()
        self.PasswordChangeCard.OldPasswordEdit.setFixedHeight(40)
        self.PasswordChangeCard.OldPasswordEdit.setPlaceholderText(self.tr("请输入旧密码"))
        self.PasswordChangeCard.NewPasswordEdit = LineEdit()
        self.PasswordChangeCard.NewPasswordEdit.setFixedHeight(40)
        self.PasswordChangeCard.NewPasswordEdit.setPlaceholderText(self.tr("请输入新密码"))
        self.PasswordChangeCard.ConfirmPasswordEdit = LineEdit()
        self.PasswordChangeCard.ConfirmPasswordEdit.setFixedHeight(40)
        self.PasswordChangeCard.ConfirmPasswordEdit.setPlaceholderText(self.tr("请确认新密码"))
        self.PasswordChangeCard.PasswordReviseButton = PrimaryPushButton(FIF.UPDATE, '确认修改')
        self.PasswordChangeCard.hBoxLayout = QHBoxLayout()
        self.PasswordChangeCard.hBoxLayout.setSpacing(10)
        self.PasswordChangeCard.hBoxLayout.addWidget(self.PasswordChangeCard.OldPasswordEdit)
        self.PasswordChangeCard.hBoxLayout.addWidget(self.PasswordChangeCard.NewPasswordEdit)
        self.PasswordChangeCard.hBoxLayout.addWidget(self.PasswordChangeCard.ConfirmPasswordEdit)
        self.PasswordChangeCard.hBoxLayout.addWidget(self.PasswordChangeCard.PasswordReviseButton)
        self.PasswordChangeCard.viewLayout.addLayout(self.PasswordChangeCard.hBoxLayout)


        self.__initWidget()

    def __initWidget(self):
        self.resize(1100, 859)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 120, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)

        # initialize layout
        self.__initLayout()

        self.setStyleSheet("""
        SettingInterface, #scrollWidget {
            background-color: rgb(249, 249, 249);
        }

        QScrollArea {
            background-color: rgb(249, 249, 249);
            border: none;
        }

        /* 标签 */
        QLabel#settingLabel {
            font: 33px 'Microsoft YaHei Light';
            background-color: transparent;
            font-weight: bold;
        }
        """)

        self.__setQss()
        
    def __initLayout(self):
        self.settingLabel.move(60, 63)
        
        self.PersonalInfoGroup.addSettingCard(self.PersonalDescriptionCard)
        self.PersonalInfoGroup.addSettingCard(self.PasswordChangeCard)

    # add setting card group to layout
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(60, 10, 60, 0)
        self.expandLayout.addWidget(self.PersonalInfoGroup)

    def __setQss(self):
        """ set style sheet """
        self.scrollWidget.setObjectName('scrollWidget')
        self.settingLabel.setObjectName('settingLabel')

if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    w = PersonInfoInterface()
    w.show()
    sys.exit(app.exec_())