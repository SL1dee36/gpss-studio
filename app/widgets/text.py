from PySide6.QtGui import QTextBlockUserData


class BlockUserData(QTextBlockUserData):
    def __init__(self, label=""):
        super().__init__()
        self.label = label
