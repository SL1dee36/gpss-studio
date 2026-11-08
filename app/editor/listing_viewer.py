from PySide6.QtCore import QSize, QRect, Qt
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtWidgets import QWidget, QPlainTextEdit


class ListingLineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)


class ListingViewer(QPlainTextEdit):
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self.main_window = main_window
        self.setObjectName("lis_viewer")
        self.setReadOnly(True)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.theme = "dark"
        self.line_number_area = ListingLineNumberArea(self)

        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.update_line_number_area_width(0)

    def line_number_area_width(self):
        digits = max(3, len(str(self.blockCount())))
        space = 10 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def update_line_number_area_width(self, _=0):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(cr.left(), cr.top(), self.line_number_area_width(), cr.height())

    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        is_dark = (self.theme == "dark")
        bg_color = QColor("#121718" if is_dark else "#f6f8fa")
        pen_line_num = QColor("#61717e" if is_dark else "#8c959f")
        pen_sep = QColor("#292f30" if is_dark else "#d0d7de")

        painter.fillRect(event.rect(), bg_color)
        painter.setFont(self.font())
        fm = self.fontMetrics()

        block = self.firstVisibleBlock()
        block_num = block.blockNumber() + 1
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        w = self.line_number_area_width()
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                painter.setPen(pen_line_num)
                num_rect = QRect(0, top, w - 8, fm.height())
                painter.drawText(num_rect, Qt.AlignRight | Qt.AlignVCenter, str(block_num))
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_num += 1

        painter.setPen(QPen(pen_sep, 1))
        painter.drawLine(w - 1, event.rect().top(), w - 1, event.rect().bottom())

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            delta = event.angleDelta().y()
            main_win = self.main_window or self.window()
            if hasattr(main_win, "zoom_in") and hasattr(main_win, "zoom_out"):
                if delta > 0:
                    main_win.zoom_in()
                elif delta < 0:
                    main_win.zoom_out()
                event.accept()
                return
        super().wheelEvent(event)
