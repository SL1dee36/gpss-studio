from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem, QStyle, QTableWidget, QFrame


class NoFocusDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        opt = QStyleOptionViewItem(option)
        opt.state &= ~QStyle.State_HasFocus
        super().paint(painter, opt, index)


class ClickableTableWidget(QTableWidget):
    ctrlClickedRow = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setFrameShape(QFrame.NoFrame)
        self.horizontalHeader().setHighlightSections(False)
        self.verticalHeader().setHighlightSections(False)
        self.setAlternatingRowColors(False)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setItemDelegate(NoFocusDelegate(self))

    def mousePressEvent(self, event):
        pos_y = int(event.position().y()) if hasattr(event, "position") else event.y()
        row = self.rowAt(pos_y)
        if event.button() == Qt.LeftButton and (event.modifiers() & Qt.ControlModifier):
            if row >= 0:
                self.ctrlClickedRow.emit(row)
                event.accept()
                return
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            row = self.currentRow()
            if row >= 0:
                self.ctrlClickedRow.emit(row)
                event.accept()
                return
        super().keyPressEvent(event)
