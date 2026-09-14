# /// script
# requires-python = ">=3.9"
# dependencies = ["PySide6>=6.5"]
# ///
import os
import re
import sys
import subprocess
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QPlainTextEdit, QLabel, QSplitter, QMessageBox,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QSizePolicy, QLineEdit, QInputDialog, QProgressDialog
)
from PySide6.QtGui import (
    QFont, QFontMetrics, QKeySequence, QShortcut, QColor, QFontDatabase,
    QPainter, QPen, QTextCursor, QTextBlockUserData, QDesktopServices
)
from PySide6.QtCore import Qt, QRect, QUrl, QThread, Signal

from gpss_runner import GpssRunner

CODE_VAR_16 = """"""
GITHUB_URL = "https://github.com/SL1dee36/gpss-studio"

STYLE_SHEET = """
QMainWindow {
    background-color: #121718;
}
QWidget {
    color: #e0e5e9;
    font-family: "Segoe UI", "Roboto", Arial, sans-serif;
    font-size: 13px;
}
QFrame#top_panel {
    background-color: transparent;
    border: 0px solid #454e4f;
    border-radius: 0px;
}

QPushButton#btn_help {
    background-color: #1f2426;
    color: #8da4b5;
    border: 1px solid #454e4f;
    border-radius: 16px;
    font-size: 14px;
    padding: 0px;
}
QPushButton#btn_help:hover {
    background-color: #292f30;
    color: #bcdfff;
    border-color: #bcdfff;
}
QPushButton#btn_help:pressed {
    background-color: #1a2228;
}

QFrame#editor_header {
    background-color: #1b1f20;
    border: 1px solid #454e4f;
    border-bottom: 1px solid #292f30;
}

QPlainTextEdit {
    font-family: Consolas, "DejaVu Sans Mono", "Liberation Mono", Menlo, monospace;
    font-size: 11pt;
    background-color: #121718;
    color: #e0e5e9;
    border: 1px solid #454e4f;
    border-radius: 0px;
    selection-background-color: #275782;
    selection-color: #ffffff;
}
QPlainTextEdit#code_editor {
    border-top: none;
}

QPushButton {
    font-weight: 600;
    border-radius: 0px;
    padding: 6px 16px;
    border: 1px solid transparent;
}
QPushButton#btn_run {
    background-color: #bcdfff;
    color: #0a2f54;
    border-radius: 16px;
    border: 1px solid #bcdfff;
    padding: 6px 20px;
}
QPushButton#btn_run:hover {
    background-color: #d6ecff;
    border: 1px solid #d6ecff;
}
QPushButton#btn_run:pressed {
    background-color: #9ecdfa;
    border: 1px solid #9ecdfa;
}
QPushButton#btn_reset {
    background-color: #1f2426;
    color: #e0e5e9;
    border: 1px solid #454e4f;
    border-radius: 4px;
}
QPushButton#btn_reset:hover {
    background-color: #292f30;
    border-color: #bcdfff;
    color: #ffffff;
}
QPushButton#btn_reset:pressed {
    background-color: #1a2228;
}
QTabWidget::pane {
    border: 1px solid #454e4f;
    border-radius: 0px;
    background-color: #121718;
}
QTabBar::tab {
    background-color: #1b1f20;
    color: #b4c4d1;
    padding: 8px 18px;
    margin-right: 2px;
    border: 1px solid #454e4f;
    border-bottom: none;
    border-radius: 0px;
}
QTabBar::tab:selected {
    background-color: #292f30;
    color: #bcdfff;
    border-top: 2px solid #bcdfff;
}
QTabBar::tab:hover:!selected {
    background-color: #22282a;
    color: #e0e5e9;
}

QSplitter::handle:horizontal {
    background-color: #313a3d;
    width: 6px;
    margin: 0px 2px;
    border-radius: 2px;
}
QSplitter::handle:horizontal:hover {
    background-color: #bcdfff;
}
QSplitter::handle:horizontal:pressed {
    background-color: #9ecdfa;
}

QTableWidget {
    background-color: #121718;
    gridline-color: #292f30;
    border: none;
    border-radius: 0px;
    selection-background-color: #1f2e3d;
    selection-color: #e0e5e9;
}
QTableWidget::item:selected {
    background-color: #1f2e3d;
    color: #ffffff;
    font-weight: normal;
}
QHeaderView {
    background-color: #121718;
}
QHeaderView::section {
    background-color: #1b1f20;
    color: #bcdfff;
    border: 1px solid #454e4f;
    border-radius: 0px;
    padding: 6px;
    font-weight: normal;
}
QHeaderView::section:checked {
    font-weight: normal;
}

QHeaderView::section:vertical {
    background-color: #121718;
    color: #61717e;
    border: none;
    border-right: 1px solid #292f30;
    border-bottom: 1px solid #292f30;
    padding: 0px 8px;
    font-weight: normal;
}
QHeaderView::section:vertical:checked,
QHeaderView::section:vertical:selected {
    background-color: #121718;
    color: #bcdfff;
    font-weight: normal;
}
QTableCornerButton::section {
    background-color: #121718;
    border: 1px solid #292f30;
}

QScrollBar:vertical {
    border: none;
    background-color: #121718;
    width: 10px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background-color: #454e4f;
    min-height: 20px;
    border-radius: 0px;
}
QScrollBar::handle:vertical:hover {
    background-color: #5d6e7a;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
    border: none;
}
QScrollBar:horizontal {
    border: none;
    background-color: #121718;
    height: 10px;
    margin: 0px;
}
QScrollBar::handle:horizontal {
    background-color: #454e4f;
    min-width: 20px;
    border-radius: 0px;
}
QScrollBar::handle:horizontal:hover {
    background-color: #5d6e7a;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: none;
    border: none;
}
"""


class BlockUserData(QTextBlockUserData):
    def __init__(self, label=""):
        super().__init__()
        self.label = label


class LabelGutter(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
        self.inline_edit = QLineEdit(self)
        self.inline_edit.setMaxLength(4)
        self.inline_edit.hide()
        self.inline_edit.setStyleSheet(
            "background-color: #1f2426; color: #bcdfff; border: 1px solid #bcdfff; "
            "font-family: Consolas, 'DejaVu Sans Mono', Menlo, monospace; font-size: 11px; padding: 0px 2px; border-radius: 0px;"
        )
        self.inline_edit.returnPressed.connect(self._finish_edit)
        self.inline_edit.editingFinished.connect(self._finish_edit)
        self.editing_block = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(event.rect(), QColor("#121718"))

        font = self.editor.font()
        painter.setFont(font)
        fm = QFontMetrics(font)

        block = self.editor.firstVisibleBlock()
        block_num = block.blockNumber()
        top = int(self.editor.blockBoundingGeometry(block).translated(self.editor.contentOffset()).top())
        bottom = top + int(self.editor.blockBoundingRect(block).height())

        pen_empty = QColor("#454e4f")
        pen_filled = QColor("#bcdfff")

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                ud = block.userData()
                lbl = ud.label if (ud and hasattr(ud, "label")) else ""

                if lbl:
                    painter.setPen(pen_filled)
                    painter.drawText(4, top, self.width() - 8, fm.height(), Qt.AlignCenter, lbl)
                else:
                    painter.setPen(pen_empty)
                    painter.drawText(4, top, self.width() - 8, fm.height(), Qt.AlignCenter, "_ _")

            block = block.next()
            top = bottom
            bottom = top + int(self.editor.blockBoundingRect(block).height())
            block_num += 1

        painter.setPen(QPen(QColor("#454e4f"), 1))
        painter.drawLine(self.width() - 1, event.rect().top(), self.width() - 1, event.rect().bottom())

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
        self.inline_edit.setGeometry(2, int(y) + 1, self.width() - 4, int(h) - 2)
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
        self.inline_edit.hide()
        self.editing_block = None
        self.update()


class GPSSCodeEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("code_editor")
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.gutter = LabelGutter(self)

        self.blockCountChanged.connect(self.update_gutter_width)
        self.updateRequest.connect(self.update_gutter)
        self.update_gutter_width(0)

    def gutter_width(self):
        return self.fontMetrics().horizontalAdvance("W") * 3 + 14

    def update_gutter_width(self, _):
        self.setViewportMargins(self.gutter_width(), 0, 0, 0)

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


def make_mono_font():
    if "Consolas" in QFontDatabase.families():
        font = QFont("Consolas", 11)
    else:
        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        font.setPointSize(11)
    font.setStyleHint(QFont.Monospace)
    return font


class SetupWorker(QThread):
    progress = Signal(str, int)
    failed = Signal(str)

    def __init__(self, runner):
        super().__init__()
        self.runner = runner

    def run(self):
        try:
            self.runner.setup(lambda text, pct: self.progress.emit(text, -1 if pct is None else pct))
        except Exception as e:
            self.failed.emit(str(e))


def ensure_runner_ready(runner, parent=None):
    if not runner.needs_setup():
        return True

    dlg = QProgressDialog("Подготовка окружения для gpssh.exe...", None, 0, 0, parent)
    dlg.setWindowTitle("GPSS/H Studio: первый запуск")
    dlg.setWindowModality(Qt.ApplicationModal)
    dlg.setMinimumWidth(480)
    dlg.setMinimumDuration(0)
    dlg.setAutoClose(False)
    dlg.setAutoReset(False)

    def on_progress(text, pct):
        dlg.setLabelText(text)
        if pct < 0:
            dlg.setRange(0, 0)
        else:
            dlg.setRange(0, 100)
            dlg.setValue(pct)

    errors = []
    worker = SetupWorker(runner)
    worker.progress.connect(on_progress)
    worker.failed.connect(errors.append)
    worker.finished.connect(dlg.close)
    worker.start()
    dlg.exec()
    worker.wait()

    if errors:
        QMessageBox.critical(parent, "Ошибка настройки", errors[0])
        return False
    return True


class GPSSStudio(QMainWindow):
    def __init__(self, runner):
        super().__init__()
        self.setWindowTitle("GPSS/H Studio")
        self.resize(1180, 720)
        self.setStyleSheet(STYLE_SHEET)

        self.runner = runner
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.gps_file = os.path.join(self.current_dir, "model.gps")
        self.lis_file = os.path.join(self.current_dir, "model.lis")

        self._build_ui()

        QShortcut(QKeySequence("F5"), self, self.run_simulation)
        QShortcut(QKeySequence("Ctrl+G"), self, self._go_to_line)
        QShortcut(QKeySequence("Ctrl+1"), self, lambda: self.tabs.setCurrentIndex(0))
        QShortcut(QKeySequence("Ctrl+2"), self, lambda: self.tabs.setCurrentIndex(1))
        QShortcut(QKeySequence("Ctrl+3"), self, lambda: self.tabs.setCurrentIndex(2))

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(12, 12, 12, 12)
        root_layout.setSpacing(10)

        top_panel = QFrame()
        top_panel.setObjectName("top_panel")
        top_panel.setFixedHeight(46)
        top_layout = QHBoxLayout(top_panel)
        top_layout.setContentsMargins(8, 4, 8, 4)
        top_layout.setSpacing(8)

        self.btn_run = QPushButton("Запустить (F5)")
        self.btn_run.setObjectName("btn_run")
        self.btn_run.setFixedHeight(32)
        self.btn_run.clicked.connect(self.run_simulation)

        btn_reset = QPushButton("Сбросить")
        btn_reset.setObjectName("btn_reset")
        btn_reset.setFixedHeight(32)
        btn_reset.clicked.connect(lambda: self.editor.setPlainText(CODE_VAR_16))

        self.lbl_status = QLabel(f"Рабочая папка: {self.current_dir}")
        self.lbl_status.setStyleSheet("color: #7a8c9e; margin-left: 6px; font-size: 11px;")

        btn_help = QPushButton("help?")
        btn_help.setObjectName("btn_help")
        btn_help.setFixedSize(64, 32)
        btn_help.setToolTip(f"Открыть GitHub репозиторий:\n{GITHUB_URL}")
        btn_help.setCursor(Qt.PointingHandCursor)
        btn_help.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(GITHUB_URL)))

        top_layout.addWidget(self.btn_run)
        top_layout.addWidget(btn_reset)
        top_layout.addWidget(self.lbl_status)
        top_layout.addStretch()
        top_layout.addWidget(btn_help)

        root_layout.addWidget(top_panel)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(8)
        mono_font = make_mono_font()

        # Левая часть
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        # Интегрированная шапка над редактором кода
        editor_header = QFrame()
        editor_header.setObjectName("editor_header")
        editor_header.setFixedHeight(35)
        header_layout = QHBoxLayout(editor_header)
        header_layout.setContentsMargins(12, 0, 12, 0)
        header_layout.setSpacing(8)

        lbl_col1 = QLabel("МЕТКА")
        lbl_col1.setStyleSheet("color: #7a8c9e; font-size: 11px; font-weight: 600; letter-spacing: 0.5px;")

        lbl_sep = QLabel("│")
        lbl_sep.setStyleSheet("color: #454e4f; font-weight: bold;")

        lbl_col2 = QLabel("КОД МОДЕЛИ GPSS")
        lbl_col2.setStyleSheet("color: #b4c4d1; font-size: 11px; font-weight: 600; letter-spacing: 0.5px;")

        header_layout.addWidget(lbl_col1)
        header_layout.addWidget(lbl_sep)
        header_layout.addWidget(lbl_col2)
        header_layout.addStretch()

        left_layout.addWidget(editor_header)

        self.editor = GPSSCodeEditor()
        self.editor.setFont(mono_font)
        self.editor.setTabStopDistance(QFontMetrics(mono_font).horizontalAdvance(' ') * 8)
        self.editor.setPlainText(CODE_VAR_16)
        left_layout.addWidget(self.editor)
        splitter.addWidget(left_widget)

        # Правая часть
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(6)

        self.tabs = QTabWidget()

        self.summary_table = QTableWidget()
        self.summary_table.setColumnCount(3)
        self.summary_table.setHorizontalHeaderLabels(["Параметр", "Значение", "Пояснение"])
        
        self.summary_table.horizontalHeader().setHighlightSections(False)
        self.summary_table.verticalHeader().setHighlightSections(False)
        
        self.summary_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.summary_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.summary_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tabs.addTab(self.summary_table, "Сводка для отчёта")

        self.lis_viewer = QPlainTextEdit()
        self.lis_viewer.setFont(mono_font)
        self.lis_viewer.setReadOnly(True)
        self.lis_viewer.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.tabs.addTab(self.lis_viewer, "Полный листинг (.lis)")

        self.console_viewer = QPlainTextEdit()
        self.console_viewer.setFont(mono_font)
        self.console_viewer.setReadOnly(True)
        self.tabs.addTab(self.console_viewer, "Вывод консоли")

        right_layout.addWidget(self.tabs)
        splitter.addWidget(right_widget)

        splitter.setSizes([500, 660])
        root_layout.addWidget(splitter, 1)

    def _go_to_line(self):
        total = self.editor.document().blockCount()
        line, ok = QInputDialog.getInt(self, "Переход к строке", f"Номер строки (1-{total}):", 1, 1, total)
        if ok:
            block = self.editor.document().findBlockByNumber(line - 1)
            cursor = QTextCursor(block)
            self.editor.setTextCursor(cursor)
            self.editor.setFocus()

    def _find_exe(self):
        for name in os.listdir(self.current_dir):
            if name.lower() == "gpssh.exe":
                return os.path.join(self.current_dir, name)
        return None

    def run_simulation(self):
        exe_path = self._find_exe()
        if not exe_path:
            QMessageBox.critical(
                self, "Ошибка",
                f"Файл gpssh.exe не найден!\n\nПоложите gpssh.exe в папку программы:\n{self.current_dir}"
            )
            return
        if not ensure_runner_ready(self.runner, self):
            return

        full_code_lines = []
        block = self.editor.document().firstBlock()
        while block.isValid():
            line_text = block.text().replace("\xa0", " ").lstrip(" \t")
            ud = block.userData()
            label = ud.label.strip() if (ud and hasattr(ud, "label")) else ""

            if not line_text and not label:
                block = block.next()
                continue

            if label:
                if label.startswith("*"):
                    full_code_lines.append(f"{label} {line_text}")
                else:
                    full_code_lines.append(f"{label:<2} {line_text}")
            else:
                full_code_lines.append(f"  {line_text}")

            block = block.next()

        code = "\n".join(full_code_lines).rstrip() + "\r\n"

        try:
            with open(self.gps_file, "w", encoding="ascii", errors="replace", newline="") as f:
                f.write(code)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка сохранения", f"Не удалось записать model.gps:\n{e}")
            return

        if os.path.exists(self.lis_file):
            try:
                os.remove(self.lis_file)
            except OSError:
                pass

        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            process = self.runner.run(exe_path, self.current_dir, "model.gps", timeout=15)
        except subprocess.TimeoutExpired:
            QMessageBox.warning(self, "Таймаут", "Процесс GPSS завис. Проверьте условия завершения модели.")
            return
        except Exception as e:
            QMessageBox.critical(self, "Ошибка запуска", f"Сбой при запуске gpssh.exe:\n{e}")
            return
        finally:
            QApplication.restoreOverrideCursor()

        self.console_viewer.setPlainText(f"STDOUT:\n{process.stdout}\n\nSTDERR:\n{process.stderr}")

        if not os.path.exists(self.lis_file):
            self.tabs.setCurrentIndex(2)
            self.lis_viewer.setPlainText("Файл model.lis не был создан. Проверьте вкладку консоли.")
            return

        lis_text = ""
        for enc in ("cp866", "latin-1", "utf-8"):
            try:
                with open(self.lis_file, "r", encoding=enc) as f:
                    lis_text = f.read()
                break
            except UnicodeDecodeError:
                continue

        self.lis_viewer.setPlainText(lis_text)
        self._parse_and_fill_summary(lis_text)
        self.tabs.setCurrentIndex(0)

    def _parse_and_fill_summary(self, text):
        data = []

        clock_match = re.search(r"Absolute Clock:\s*([\d\.]+)", text, re.IGNORECASE)
        clock = clock_match.group(1) if clock_match else "Н/Д"
        data.append(("Время моделирования (Absolute Clock)", clock, "Общая длительность работы системы в тактах"))

        fac_match = re.search(
            r"Facility\s+Total\s+Avail.*?\n(?:[^\n]*\n)?\s*(\w+)\s+([\d\.]+)\s+(?:[\d\.]+\s+)*(\d+)\s+([\d\.]+)",
            text,
            re.IGNORECASE
        )
        if not fac_match:
            fac_match = re.search(
                r"^[ \t]*(?:MEM|\w+)[ \t]+([\d\.]+)[ \t]+(?:[\d\.]+[ \t]+)*(\d+)[ \t]+([\d\.]+)",
                text,
                re.MULTILINE
            )

        if fac_match:
            _, util, entries, avg_time = fac_match.groups()
            data.append(("Обработано заявок ОП (Entries)", entries, "Количество заявок, обслуженных памятью"))
            data.append(("Коэффициент загрузки ОП (Avg-Util)", util, "Доля времени занятости памяти (от 0 до 1)"))
            data.append(("Среднее время обработки (Avg Time/Xact)", avg_time, "Время обработки одного запроса памятью (такты)"))

        q_match = re.search(
            r"Queue\s+Maximum\s+Average.*?\n(?:[^\n]*\n)?\s*(\w+)\s+(\d+)\s+([\d\.]+)\s+(\d+)\s+\d+\s+[\d\.]+\s+([\d\.]+)",
            text,
            re.IGNORECASE
        )
        if not q_match:
            q_match = re.search(
                r"^[ \t]*(?:AAA|\w+)[ \t]+(\d+)[ \t]+([\d\.]+)[ \t]+(\d+)[ \t]+\d+[ \t]+[\d\.]+[ \t]+([\d\.]+)",
                text,
                re.MULTILINE
            )

        if q_match:
            _, q_max, q_avg, q_total, q_time = q_match.groups()
            data.append(("Всего заявок в очереди (Total Entries)", q_total, "Сколько всего заявок поступило от процессора"))
            data.append(("Макс. длина очереди (Maximum Contents)", q_max, "Пиковое число заявок, ожидавших в очереди"))
            data.append(("Средняя длина очереди (Average Contents)", q_avg, "Среднее количество ожидающих запросов"))
            data.append(("Среднее время ожидания (Average Time/Unit)", q_time, "Среднее время нахождения запроса в очереди (такты)"))

        self.summary_table.setRowCount(len(data))
        for row, (param, val, desc) in enumerate(data):
            it_param = QTableWidgetItem(param)
            it_val = QTableWidgetItem(val)
            it_val.setTextAlignment(Qt.AlignCenter)
            it_val.setForeground(QColor("#bcdfff"))
            it_desc = QTableWidgetItem(desc)

            self.summary_table.setItem(row, 0, it_param)
            self.summary_table.setItem(row, 1, it_val)
            self.summary_table.setItem(row, 2, it_desc)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    runner = GpssRunner()
    ensure_runner_ready(runner)
    window = GPSSStudio(runner)
    window.show()
    sys.exit(app.exec())