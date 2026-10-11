from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QColor, QTextFormat, QTextCursor
from PySide6.QtWidgets import QPlainTextEdit, QTextEdit

from app.consts import GPSS_CORE_KEYWORDS
from app.editor.highlighter import GPSSHighlighter
from app.editor.lable_gutter import LabelGutter
from app.widgets.text import BlockUserData


class GPSSCodeEditor(QPlainTextEdit):
    gutterWidthChanged = Signal()

    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self.main_window = main_window
        self.setObjectName("code_editor")
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.theme = "dark"
        self.gutter = LabelGutter(self)
        self.highlighter = GPSSHighlighter(self.document(), theme=self.theme)

        self.blockCountChanged.connect(self.update_gutter_width)
        self.updateRequest.connect(self.update_gutter)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.update_gutter_width(0)

    def set_theme(self, theme):
        self.theme = theme
        self.highlighter.set_theme(theme)
        self.gutter.update_inline_style()
        self.gutter.update()
        self.highlight_current_line()

    def gutter_width(self):
        return self.gutter.total_width()

    def update_gutter_width(self, _=0):
        self.setViewportMargins(self.gutter_width(), 0, 0, 0)
        self.gutterWidthChanged.emit()

    def update_gutter(self, rect, dy):
        if dy:
            self.gutter.scroll(0, dy)
        else:
            self.gutter.update(0, rect.y(), self.gutter.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_gutter_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.gutter.setGeometry(cr.left(), cr.top(), self.gutter_width(), cr.height())

    def highlight_current_line(self):
        extra_selections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor("#161d21" if self.theme == "dark" else "#eef3f8")
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        self.setExtraSelections(extra_selections)

    def load_code(self, text):
        lines = text.splitlines()
        if not lines:
            lines = [""]

        cursor = self.textCursor()
        cursor.beginEditBlock()
        self.clear()

        first = True
        for line in lines:
            line_clean = line.replace("\xa0", " ").rstrip("\r\n")
            label = ""
            code_text = ""

            if line_clean.startswith("*"):
                label = "*"
                code_text = line_clean[1:].lstrip()
            elif line_clean.startswith(" ") or line_clean.startswith("\t") or not line_clean.strip():
                label = ""
                code_text = line_clean.lstrip(" \t")
            else:
                tokens = line_clean.split(None, 1)
                first_token = tokens[0].rstrip(":").upper()
                if first_token in GPSS_CORE_KEYWORDS:
                    label = ""
                    code_text = line_clean.strip()
                else:
                    label = tokens[0].rstrip(":")
                    code_text = tokens[1].strip() if len(tokens) > 1 else ""

            if not first:
                cursor.insertBlock()
            else:
                first = False

            cursor.insertText(code_text)
            cursor.block().setUserData(BlockUserData(label))

        cursor.endEditBlock()
        self.document().setModified(False)
        self.update_gutter_width(0)
        self.gutter.update()

    def get_formatted_code(self, target_os="windows"):
        full_code_lines = []
        block = self.document().firstBlock()
        while block.isValid():
            line_text = block.text().replace("\xa0", " ").strip()
            ud = block.userData()
            label = ud.label.strip() if (ud and hasattr(ud, "label")) else ""

            if not line_text and not label:
                full_code_lines.append("")
                block = block.next()
                continue

            if label:
                if label.startswith("*"):
                    full_code_lines.append(f"{label} {line_text}".rstrip())
                else:
                    full_code_lines.append(f"{label:<8} {line_text}".rstrip())
            else:
                full_code_lines.append(f"  {line_text}".rstrip())

            block = block.next()

        newline_seq = "\r\n" if target_os == "windows" else "\n"
        return newline_seq.join(full_code_lines).rstrip() + newline_seq

    def _indent_selection(self, unindent=False):
        cursor = self.textCursor()
        if not cursor.hasSelection() and not unindent:
            self.insertPlainText("  ")
            return

        cursor.beginEditBlock()
        start_block = self.document().findBlock(cursor.selectionStart())
        end_block = self.document().findBlock(cursor.selectionEnd())
        b = start_block
        while True:
            c = QTextCursor(b)
            if unindent:
                text = b.text()
                if text.startswith("  "):
                    c.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor, 2)
                    c.removeSelectedText()
                elif text.startswith(" ") or text.startswith("\t"):
                    c.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor, 1)
                    c.removeSelectedText()
            else:
                c.insertText("  ")
            if b == end_block:
                break
            b = b.next()
        cursor.endEditBlock()

    def _move_line(self, direction):
        cursor = self.textCursor()
        block = cursor.block()
        target_block = block.previous() if direction < 0 else block.next()
        if not target_block.isValid():
            return

        b1, b2 = (target_block, block) if direction < 0 else (block, target_block)
        t1, t2 = b1.text(), b2.text()
        lbl1 = b1.userData().label if (b1.userData() and hasattr(b1.userData(), "label")) else ""
        lbl2 = b2.userData().label if (b2.userData() and hasattr(b2.userData(), "label")) else ""

        cursor.beginEditBlock()
        c1 = QTextCursor(b1)
        c1.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
        c1.insertText(t2)
        b1.setUserData(BlockUserData(lbl2))

        c2 = QTextCursor(b2)
        c2.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
        c2.insertText(t1)
        b2.setUserData(BlockUserData(lbl1))
        cursor.endEditBlock()

        if hasattr(self, "highlighter") and self.highlighter:
            self.highlighter.rehighlightBlock(b1)
            self.highlighter.rehighlightBlock(b2)

        self.gutter.update()
        new_cursor = QTextCursor(target_block)
        new_cursor.movePosition(QTextCursor.StartOfLine)
        self.setTextCursor(new_cursor)

    def _duplicate_line(self):
        cursor = self.textCursor()
        cursor.beginEditBlock()
        line_text = cursor.block().text()
        ud = cursor.block().userData()
        lbl = ud.label if (ud and hasattr(ud, "label")) else ""
        cursor.movePosition(QTextCursor.EndOfBlock)
        cursor.insertText("\n" + line_text)
        cursor.block().setUserData(BlockUserData(lbl))
        cursor.endEditBlock()
        if hasattr(self, "highlighter") and self.highlighter:
            self.highlighter.rehighlightBlock(cursor.block())
        self.gutter.update()

    def _toggle_comment(self):
        cursor = self.textCursor()
        cursor.beginEditBlock()
        start_block = self.document().findBlock(cursor.selectionStart())
        end_block = self.document().findBlock(cursor.selectionEnd())
        b = start_block
        while True:
            ud = b.userData()
            lbl = ud.label if (ud and hasattr(ud, "label")) else ""
            if lbl.strip() == "*":
                b.setUserData(BlockUserData(""))
            elif not lbl.strip():
                b.setUserData(BlockUserData("*"))
            else:
                text = b.text()
                c = QTextCursor(b)
                if text.startswith("*"):
                    c.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor)
                    c.removeSelectedText()
                else:
                    c.insertText("* ")
            if hasattr(self, "highlighter") and self.highlighter:
                self.highlighter.rehighlightBlock(b)
            if b == end_block:
                break
            b = b.next()
        cursor.endEditBlock()
        self.gutter.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Home:
            cursor = self.textCursor()
            pos = cursor.position()
            start_of_line = cursor.block().position()
            line_text = cursor.block().text()
            first_non_space = len(line_text) - len(line_text.lstrip(" \t"))
            indent_pos = start_of_line + first_non_space
            mode = QTextCursor.KeepAnchor if (event.modifiers() & Qt.ShiftModifier) else QTextCursor.MoveAnchor
            if pos == indent_pos:
                cursor.setPosition(start_of_line, mode)
            else:
                cursor.setPosition(indent_pos, mode)
            self.setTextCursor(cursor)
            return

        if event.key() in (Qt.Key_Backtab, Qt.Key_Tab) and (event.modifiers() & Qt.ShiftModifier):
            self._indent_selection(unindent=True)
            return

        if event.key() == Qt.Key_Tab:
            self._indent_selection(unindent=False)
            return

        if event.modifiers() == Qt.AltModifier and event.key() == Qt.Key_Up:
            self._move_line(-1)
            return

        if event.modifiers() == Qt.AltModifier and event.key() == Qt.Key_Down:
            self._move_line(1)
            return

        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_D:
            self._duplicate_line()
            return

        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_Slash:
            self._toggle_comment()
            return

        if event.key() == Qt.Key_F2:
            self.gutter.edit_block(self.textCursor().block())
            return

        super().keyPressEvent(event)

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
