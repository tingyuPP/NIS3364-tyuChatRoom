from qfluentwidgets import CardWidget, AvatarWidget, BodyLabel, StrongBodyLabel
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout,QFrame
from PyQt5.QtCore import Qt

class UserCard(QFrame):
    def __init__(self, title, content, parent=None):
        super().__init__(parent)    
        self.titleLabel = StrongBodyLabel(title, self)
        self.bioLabel = BodyLabel(content, self)
        
        
        self.avatar = AvatarWidget()
        self.avatar.setText(title)

        self.avatar.setRadius(25)
        
        self.setFixedHeight(75)

        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()

        self.hBoxLayout.setContentsMargins(20, 11, 11, 11)
        self.hBoxLayout.setSpacing(15)
        self.hBoxLayout.addWidget(self.avatar)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(5)
        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignVCenter)
        self.vBoxLayout.addWidget(self.bioLabel, 0, Qt.AlignVCenter)
        self.vBoxLayout.setAlignment(Qt.AlignVCenter)
        self.hBoxLayout.addLayout(self.vBoxLayout)

        self.hBoxLayout.addStretch(1)

        
