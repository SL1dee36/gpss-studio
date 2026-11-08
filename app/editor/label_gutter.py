from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtWidgets import QWidget, QLineEdit

from app.widgets.text import BlockUserData


class LabelGutter(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
        self.show_line_numbers = False
        self.inline_edit = QLineEdit(self)
        self.inline_edit.setMaxLength(8)
        self.inline_edit.hide()
        self.inline_edit.returnPressed.connect(self._finish_edit)
        self.inline_edit.editingFinished.connect(self._finish_edit)

        def inline_key_press(event):
            if event.key() == Qt.Key_Escape:
                self.editing_block = None
                self.inline_edit.hide()
                self.editor.setFocus()
                return
            QLineEdit.keyPressEvent(self.inline_edit, event)

        self.inline_edit.keyPressEvent = inline_key_press
        self.editing_block = None

    def update_inline_style(self):
        is_dark = (self.editor.theme == "dark")
        bg = "#1f2426" if is_dark else "#ffffff"
        fg = "#bcdfff" if is_dark else "#0969da"
        border = "#bcdfff" if is_dark else "#0969da"
        self.inline_edit.setStyleSheet(
            f"background-color: {bg}; color: {fg}; border: 1px solid {border}; "
            "font-family: Consolas; font-size: 11px; padding: 0px 2px; border-radius: 0px;"
        )

    def line_num_digits(self):
        return max(2, len(str(self.editor.blockCount())))

    def line_num_width(self):
        if not self.show_line_numbers:
            return 0
        return self.editor.fontMetrics().horizontalAdvance("9") * self.line_num_digits() + 12

    def label_col_width(self):
        return self.editor.fontMetrics().horizontalAdvance("W") * 4 + 14

    def total_width(self):
        return self.line_num_width() + self.label_col_width()

    def paintEvent(self, event):
        painter = QPainter(self)
        is_dark = (self.editor.theme == "dark")

        bg_color = QColor("#121718" if is_dark else "#f6f8fa")
        pen_line_num = QColor("#61717e" if is_dark else "#8c959f")
        pen_sep = QColor("#292f30" if is_dark else "#d0d7de")
        pen_empty = QColor("#454e4f" if is_dark else "#afb8c1")
        pen_filled = QColor("#bcdfff" if is_dark else "#0969da")

        painter.fillRect(event.rect(), bg_color)

        font = self.editor.font()
        painter.setFont(font)
        fm = self.editor.fontMetrics()

        line_w = self.line_num_width()
        lbl_w = self.label_col_width()
        total_w = line_w + lbl_w

        block = self.editor.firstVisibleBlock()
        block_num = block.blockNumber() + 1
        top = int(self.editor.blockBoundingGeometry(block).translated(self.editor.contentOffset()).top())
        bottom = top + int(self.editor.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                is_error = hasattr(self.editor, "error_lines") and (block_num in self.editor.error_lines)
                if self.show_line_numbers:
                    if is_error:
                        painter.setPen(QColor("#ff5555" if is_dark else "#cf222e"))
                    else:
                        painter.setPen(pen_line_num)
                    num_rect = QRect(0, top, line_w - 6, fm.height())
                    painter.drawText(num_rect, Qt.AlignRight | Qt.AlignVCenter, str(block_num))

                ud = block.userData()
                lbl = ud.label if (ud and hasattr(ud, "label")) else ""
                lbl_rect = QRect(line_w + 2, top, lbl_w - 4, fm.height())
                if lbl:
                    painter.setPen(pen_filled)
                    painter.drawText(lbl_rect, Qt.AlignCenter, lbl)
                else:
                    painter.setPen(pen_empty)
                    painter.drawText(lbl_rect, Qt.AlignCenter, "_ _")

                if is_error:
                    # Маркер ошибки в gutter
                    painter.setPen(QColor("#ff5555" if is_dark else "#cf222e"))
                    painter.drawText(QRect(total_w - 10, top, 8, fm.height()), Qt.AlignCenter, "●")

            block = block.next()
            top = bottom
            bottom = top + int(self.editor.blockBoundingRect(block).height())
            block_num += 1

        if self.show_line_numbers:
            painter.setPen(QPen(pen_sep, 1))
            painter.drawLine(line_w, event.rect().top(), line_w, event.rect().bottom())

        painter.setPen(QPen(QColor("#454e4f" if is_dark else "#d0d7de"), 1))
        painter.drawLine(total_w - 1, event.rect().top(), total_w - 1, event.rect().bottom())

    def mouseDoubleClickEvent(self, event):
        pos_y = event.position().y()
        block = self.editor.firstVisibleBlock()
        top = int(self.editor.blockBoundingGeometry(block).translated(self.editor.contentOffset()).top())
        bottom = top + int(self.editor.blockBoundingRect(block).height())

        while block.isValid():
            if block.isVisible() and top <= pos_y <= bottom:
                self._start_edit(block, top, bottom - top)
                break
            block = block.next()
            top = bottom
            bottom = top + int(self.editor.blockBoundingRect(block).height())

    def edit_block(self, block):
        if not block or not block.isValid():
            return
        top = int(self.editor.blockBoundingGeometry(block).translated(self.editor.contentOffset()).top())
        h = int(self.editor.blockBoundingRect(block).height())
        self._start_edit(block, top, h)

    def _start_edit(self, block, y, h):
        self.editing_block = block
        ud = block.userData()
        val = ud.label if (ud and hasattr(ud, "label")) else ""
        self.inline_edit.setText(val)
        line_w = self.line_num_width()
        lbl_w = self.label_col_width()
        self.inline_edit.setGeometry(line_w + 2, int(y) + 1, lbl_w - 4, int(h) - 2)
        self.update_inline_style()
        self.inline_edit.show()
        self.inline_edit.setFocus()
        self.inline_edit.selectAll()

    def _finish_edit(self):
        if self.editing_block and self.editing_block.isValid():
            val = self.inline_edit.text().strip()
            ud = self.editing_block.userData()
            if not ud:
                ud = BlockUserData(val)
                self.editing_block.setUserData(ud)

            else:
                ud.label = val
            if hasattr(self.editor, "highlighter") and self.editor.highlighter:
                self.editor.highlighter.rehighlightBlock(self.editing_block)
        self.editing_block = None
        self.inline_edit.hide()
        self.update()
        self.editor.setFocus()
