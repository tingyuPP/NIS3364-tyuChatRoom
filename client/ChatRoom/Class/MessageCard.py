from qfluentwidgets import CardWidget, AvatarWidget, StrongBodyLabel, SubtitleLabel
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QFrame
from PyQt5.QtCore import Qt

class MessageCard(QFrame):
    def __init__(self, sender, timestamp, content, parent=None):
        super().__init__(parent)
        self.senderLabel = StrongBodyLabel(f"{sender} - {timestamp}", self)
        
        self.contentCard = CardWidget(self)
        self.contentLabel = StrongBodyLabel(content, self.contentCard)
        
        self.avatar = AvatarWidget()
        self.avatar.setText(sender)
        self.avatar.setRadius(25)
        
        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()

        self.hBoxLayout.setContentsMargins(20, 11, 11, 11)
        self.hBoxLayout.setSpacing(15)
        self.hBoxLayout.addWidget(self.avatar)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(5)
        self.vBoxLayout.addWidget(self.senderLabel, 0, Qt.AlignVCenter)
        self.vBoxLayout.addWidget(self.contentCard, 0, Qt.AlignVCenter)
        self.vBoxLayout.setAlignment(Qt.AlignVCenter)
        self.hBoxLayout.addLayout(self.vBoxLayout)

        self.hBoxLayout.addStretch(1)

        self.contentCard.setContentsMargins(10, 10, 10, 10)
        self.contentCard.setLayout(QVBoxLayout())
        self.contentCard.layout().addWidget(self.contentLabel)