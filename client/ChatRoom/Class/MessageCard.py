from qfluentwidgets import CardWidget, AvatarWidget, StrongBodyLabel, SubtitleLabel
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QFrame, QSizePolicy
from PyQt5.QtCore import Qt, pyqtProperty
from PyQt5.QtGui import QColor, QPainter, QPainterPath

class MyCardWidget(CardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._backgroundColor = self._normalBackgroundColor()

    def getBackgroundColor(self):
        return self._backgroundColor

    def setBackgroundColor(self, color: QColor):
        self._backgroundColor = color
        self.update()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        r = self.borderRadius
        d = 2 * r

        # draw top border
        path = QPainterPath()
        path.arcMoveTo(1, h - d - 1, d, d, 240)
        path.arcTo(1, h - d - 1, d, d, 225, -60)
        path.lineTo(1, r)
        path.arcTo(1, 1, d, d, -180, -90)
        path.lineTo(w - r, 1)
        path.arcTo(w - d - 1, 1, d, d, 90, -90)
        path.lineTo(w - 1, h - r)
        path.arcTo(w - d - 1, h - d - 1, d, d, 0, -60)

        topBorderColor = QColor(0, 0, 0, 20)

        painter.strokePath(path, topBorderColor)

        # draw bottom border
        path = QPainterPath()
        path.arcMoveTo(1, h - d - 1, d, d, 240)
        path.arcTo(1, h - d - 1, d, d, 240, 30)
        path.lineTo(w - r - 1, h - 1)
        path.arcTo(w - d - 1, h - d - 1, d, d, 270, 30)

        bottomBorderColor = topBorderColor
        if self.isHover and not self.isPressed:
            bottomBorderColor = QColor(0, 0, 0, 27)

        painter.strokePath(path, bottomBorderColor)

        # draw background
        painter.setPen(Qt.NoPen)
        rect = self.rect().adjusted(1, 1, -1, -1)
        painter.setBrush(self._backgroundColor)
        painter.drawRoundedRect(rect, r, r)

    backgroundColor = pyqtProperty(QColor, getBackgroundColor, setBackgroundColor)

class MessageCard(QFrame):
    def __init__(self, sender, timestamp, content, parent=None):
        super().__init__(parent)
        self.senderLabel = StrongBodyLabel(f"{sender} - {timestamp}", self)
        
        self.contentCard = MyCardWidget(self)
        self.contentLabel = StrongBodyLabel(content, self.contentCard)
        self.contentLabel.setWordWrap(True)
        self.contentLabel.setTextInteractionFlags(Qt.TextSelectableByMouse)
        # self.contentLabel.setMinimumWidth(100)  # 设置最小宽度
        # self.contentLabel.setMaximumWidth(800)  # 设置最大宽度
        self.contentLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
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