import os
import re
import sys
import json
import subprocess
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QPlainTextEdit, QLabel, QSplitter, QMessageBox,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QSizePolicy, QLineEdit, QInputDialog, QFileDialog,
    QDialog, QFormLayout, QComboBox, QTextEdit, QStatusBar,
    QCheckBox
)
from PySide6.QtGui import (
    QFont, QFontMetrics, QKeySequence, QShortcut, QColor, 
    QPainter, QPen, QTextCursor, QTextBlockUserData, QDesktopServices,
    QSyntaxHighlighter, QTextCharFormat, QTextDocument, QTextFormat
)
from PySide6.QtCore import Qt, QRect, QUrl, QRegularExpression, Signal, QPoint

DEFAULT_TEMPLATE = """"""

CODE_VAR_16 = DEFAULT_TEMPLATE
GITHUB_URL = "https://github.com/SL1dee36/gpss-studio"

GPSS_CORE_KEYWORDS = {
    "GENERATE", "TERMINATE", "SEIZE", "RELEASE", "ADVANCE",
    "QUEUE", "DEPART", "ENTER", "LEAVE", "STORAGE", "TRANSFER",
    "TEST", "ASSIGN", "MARK", "PRIORITY", "SPLIT", "ASSEMBLE",
    "GATHER", "MATCH", "PREEMPT", "RETURN", "SAVEVALUE",
    "MSAVEVALUE", "TABULATE", "GATE", "SELECT", "COUNT",
    "INDEX", "PRINT", "LOGIC", "BUFFER", "LINK", "UNLINK",
    "START", "END", "CLEAR", "RESET", "FUNCTION", "VARIABLE",
    "BVARIABLE", "FVARIABLE", "INITIAL", "TABLE", "QTABLE", "SIMULATE"
}

STYLE_SHEET_DARK = """
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

QPushButton#btn_menu {
    background-color: #1f2426;
    color: #8da4b5;
    border: 1px solid #454e4f;
    border-radius: 16px;
    font-size: 15px;
    font-weight: bold;
    padding: 0px;
}
QPushButton#btn_menu:hover {
    background-color: #292f30;
    color: #bcdfff;
    border-color: #bcdfff;
}
QPushButton#btn_menu:pressed {
    background-color: #1a2228;
}

QFrame#editor_header {
    background-color: #1b1f20;
    border: 1px solid #454e4f;
    border-bottom: 1px solid #454e4f;
}

QLabel#lbl_hdr_line {
    color: #7a8c9e;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.5px;
    border-right: 1px solid #454e4f;
}

QLabel#lbl_hdr_label {
    color: #7a8c9e;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.5px;
    border-right: 1px solid #454e4f;
}

QLabel#lbl_hdr_code {
    color: #b4c4d1;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.5px;
    padding-left: 8px;
}

QFrame#search_bar {
    background-color: #1b1f20;
    border: 1px solid #454e4f;
    border-top: none;
    border-bottom: 1px solid #454e4f;
}

QPlainTextEdit {
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
    padding: 6px 14px;
}
QPushButton#btn_reset:hover {
    background-color: #292f30;
    border-color: #bcdfff;
    color: #ffffff;
}
QPushButton#btn_reset:pressed {
    background-color: #1a2228;
}

QLineEdit, QComboBox {
    background-color: #1f2426;
    color: #e0e5e9;
    border: 1px solid #454e4f;
    border-radius: 2px;
    padding: 4px 8px;
}
QLineEdit:focus, QComboBox:focus {
    border-color: #bcdfff;
}
QComboBox QAbstractItemView {
    background-color: #1b1f20;
    color: #e0e5e9;
    selection-background-color: #292f30;
    selection-color: #bcdfff;
    border: 1px solid #454e4f;
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
QStatusBar {
    background-color: #1b1f20;
    color: #7a8c9e;
    border-top: 1px solid #292f30;
    min-height: 26px;
}
QStatusBar::item {
    border: none;
}
QLabel#status_msg {
    color: #7a8c9e;
    font-size: 11px;
    padding-left: 8px;
}
QLabel#status_item {
    color: #7a8c9e;
    font-size: 11px;
    border-left: 1px solid #454e4f;
    padding-left: 16px;
    padding-right: 16px;
}
QDialog {
    background-color: #121718;
}
QDialog QPushButton {
    background-color: #1f2426;
    color: #e0e5e9;
    border: 1px solid #454e4f;
    border-radius: 4px;
    padding: 6px 14px;
    font-weight: 500;
}
QDialog QPushButton:hover {
    background-color: #292f30;
    border-color: #bcdfff;
    color: #ffffff;
}
QDialog QPushButton:pressed {
    background-color: #1a2228;
    border-color: #9ecdfa;
}
QDialog QPushButton#btn_save {
    background-color: #bcdfff;
    color: #0a2f54;
    border: 1px solid #bcdfff;
    border-radius: 4px;
    padding: 6px 16px;
    font-weight: 600;
}
QDialog QPushButton#btn_save:hover {
    background-color: #d6ecff;
    border-color: #d6ecff;
}
QDialog QPushButton#btn_save:pressed {
    background-color: #9ecdfa;
    border-color: #9ecdfa;
}
QCheckBox {
    color: #e0e5e9;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 14px;
    height: 14px;
    border: 1px solid #454e4f;
    background-color: #1f2426;
    border-radius: 2px;
}
QCheckBox::indicator:checked {
    background-color: #bcdfff;
    border-color: #bcdfff;
}

QFrame#action_menu_popup {
    background-color: #1b1f20;
    border: 1px solid #454e4f;
    border-radius: 4px;
}
QFrame#popup_separator {
    background-color: #292f30;
    border: none;
}
QPushButton#btn_popup_action {
    background-color: #1f2426;
    color: #e0e5e9;
    border: 1px solid #454e4f;
    border-radius: 3px;
    padding: 7px 12px;
    text-align: left;
    font-size: 12px;
    font-weight: 500;
}
QPushButton#btn_popup_action:hover {
    background-color: #292f30;
    border-color: #bcdfff;
    color: #bcdfff;
}
QPushButton#btn_popup_action:pressed {
    background-color: #1a2228;
}
"""

STYLE_SHEET_LIGHT = """
QMainWindow {
    background-color: #f6f8fa;
}
QWidget {
    color: #1f2328;
    font-family: "Segoe UI", "Roboto", Arial, sans-serif;
    font-size: 13px;
}
QFrame#top_panel {
    background-color: transparent;
    border: 0px solid #d0d7de;
    border-radius: 0px;
}

QPushButton#btn_help {
    background-color: #f6f8fa;
    color: #57606a;
    border: 1px solid #d0d7de;
    border-radius: 16px;
    font-size: 14px;
    padding: 0px;
}
QPushButton#btn_help:hover {
    background-color: #eaeef2;
    color: #0969da;
    border-color: #0969da;
}
QPushButton#btn_help:pressed {
    background-color: #dadfe5;
}

QPushButton#btn_menu {
    background-color: #f6f8fa;
    color: #57606a;
    border: 1px solid #d0d7de;
    border-radius: 16px;
    font-size: 15px;
    font-weight: bold;
    padding: 0px;
}
QPushButton#btn_menu:hover {
    background-color: #eaeef2;
    color: #0969da;
    border-color: #0969da;
}
QPushButton#btn_menu:pressed {
    background-color: #dadfe5;
}

QFrame#editor_header {
    background-color: #f6f8fa;
    border: 1px solid #d0d7de;
    border-bottom: 1px solid #d0d7de;
}

QLabel#lbl_hdr_line {
    color: #57606a;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.5px;
    border-right: 1px solid #d0d7de;
}

QLabel#lbl_hdr_label {
    color: #57606a;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.5px;
    border-right: 1px solid #d0d7de;
}

QLabel#lbl_hdr_code {
    color: #24292f;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.5px;
    padding-left: 8px;
}

QFrame#search_bar {
    background-color: #f6f8fa;
    border: 1px solid #d0d7de;
    border-top: none;
    border-bottom: 1px solid #d0d7de;
}

QPlainTextEdit {
    background-color: #ffffff;
    color: #1f2328;
    border: 1px solid #d0d7de;
    border-radius: 0px;
    selection-background-color: #b6d7f2;
    selection-color: #051d38;
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
    background-color: #0969da;
    color: #ffffff;
    border-radius: 16px;
    border: 1px solid #0969da;
    padding: 6px 20px;
}
QPushButton#btn_run:hover {
    background-color: #0854ad;
    border-color: #0854ad;
}
QPushButton#btn_run:pressed {
    background-color: #063f82;
    border-color: #063f82;
}
QPushButton#btn_reset {
    background-color: #f6f8fa;
    color: #24292f;
    border: 1px solid #d0d7de;
    border-radius: 4px;
    padding: 6px 14px;
}
QPushButton#btn_reset:hover {
    background-color: #eaeef2;
    border-color: #0969da;
    color: #0969da;
}
QPushButton#btn_reset:pressed {
    background-color: #dadfe5;
}

QLineEdit, QComboBox {
    background-color: #ffffff;
    color: #1f2328;
    border: 1px solid #d0d7de;
    border-radius: 2px;
    padding: 4px 8px;
}
QLineEdit:focus, QComboBox:focus {
    border-color: #0969da;
}
QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #1f2328;
    selection-background-color: #eaeef2;
    selection-color: #0969da;
    border: 1px solid #d0d7de;
}

QTabWidget::pane {
    border: 1px solid #d0d7de;
    border-radius: 0px;
    background-color: #ffffff;
}
QTabBar::tab {
    background-color: #f6f8fa;
    color: #57606a;
    padding: 8px 18px;
    margin-right: 2px;
    border: 1px solid #d0d7de;
    border-bottom: none;
    border-radius: 0px;
}
QTabBar::tab:selected {
    background-color: #ffffff;
    color: #0969da;
    border-top: 2px solid #0969da;
}
QTabBar::tab:hover:!selected {
    background-color: #eaeef2;
    color: #1f2328;
}

QSplitter::handle:horizontal {
    background-color: #d0d7de;
    width: 6px;
    margin: 0px 2px;
    border-radius: 2px;
}
QSplitter::handle:horizontal:hover {
    background-color: #0969da;
}
QSplitter::handle:horizontal:pressed {
    background-color: #0854ad;
}

QTableWidget {
    background-color: #ffffff;
    gridline-color: #eaeef2;
    border: none;
    border-radius: 0px;
    selection-background-color: #b6d7f2;
    selection-color: #051d38;
}
QTableWidget::item:selected {
    background-color: #b6d7f2;
    color: #051d38;
    font-weight: normal;
}
QHeaderView {
    background-color: #ffffff;
}
QHeaderView::section {
    background-color: #f6f8fa;
    color: #0969da;
    border: 1px solid #d0d7de;
    border-radius: 0px;
    padding: 6px;
    font-weight: normal;
}
QHeaderView::section:checked {
    font-weight: normal;
}

QHeaderView::section:vertical {
    background-color: #ffffff;
    color: #8c959f;
    border: none;
    border-right: 1px solid #eaeef2;
    border-bottom: 1px solid #eaeef2;
    padding: 0px 8px;
    font-weight: normal;
}
QHeaderView::section:vertical:checked,
QHeaderView::section:vertical:selected {
    background-color: #ffffff;
    color: #0969da;
    font-weight: normal;
}
QTableCornerButton::section {
    background-color: #ffffff;
    border: 1px solid #eaeef2;
}

QScrollBar:vertical {
    border: none;
    background-color: #ffffff;
    width: 10px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background-color: #c1c8cf;
    min-height: 20px;
    border-radius: 0px;
}
QScrollBar::handle:vertical:hover {
    background-color: #8c959f;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
    border: none;
}
QScrollBar:horizontal {
    border: none;
    background-color: #ffffff;
    height: 10px;
    margin: 0px;
}
QScrollBar::handle:horizontal {
    background-color: #c1c8cf;
    min-width: 20px;
    border-radius: 0px;
}
QScrollBar::handle:horizontal:hover {
    background-color: #8c959f;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: none;
    border: none;
}
QStatusBar {
    background-color: #f6f8fa;
    color: #57606a;
    border-top: 1px solid #d0d7de;
    min-height: 26px;
}
QStatusBar::item {
    border: none;
}
QLabel#status_msg {
    color: #57606a;
    font-size: 11px;
    padding-left: 8px;
}
QLabel#status_item {
    color: #57606a;
    font-size: 11px;
    border-left: 1px solid #d0d7de;
    padding-left: 16px;
    padding-right: 16px;
}
QDialog {
    background-color: #ffffff;
}
QDialog QPushButton {
    background-color: #f6f8fa;
    color: #24292f;
    border: 1px solid #d0d7de;
    border-radius: 4px;
    padding: 6px 14px;
    font-weight: 500;
}
QDialog QPushButton:hover {
    background-color: #eaeef2;
    border-color: #0969da;
    color: #0969da;
}
QDialog QPushButton:pressed {
    background-color: #dadfe5;
}
QDialog QPushButton#btn_save {
    background-color: #0969da;
    color: #ffffff;
    border: 1px solid #0969da;
    border-radius: 4px;
    padding: 6px 16px;
    font-weight: 600;
}
QDialog QPushButton#btn_save:hover {
    background-color: #0854ad;
    border-color: #0854ad;
}
QDialog QPushButton#btn_save:pressed {
    background-color: #063f82;
    border-color: #063f82;
}
QCheckBox {
    color: #1f2328;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 14px;
    height: 14px;
    border: 1px solid #d0d7de;
    background-color: #ffffff;
    border-radius: 2px;
}
QCheckBox::indicator:checked {
    background-color: #0969da;
    border-color: #0969da;
}

QFrame#action_menu_popup {
    background-color: #ffffff;
    border: 1px solid #d0d7de;
    border-radius: 4px;
}
QFrame#popup_separator {
    background-color: #eaeef2;
    border: none;
}
QPushButton#btn_popup_action {
    background-color: #f6f8fa;
    color: #24292f;
    border: 1px solid #d0d7de;
    border-radius: 3px;
    padding: 7px 12px;
    text-align: left;
    font-size: 12px;
    font-weight: 500;
}
QPushButton#btn_popup_action:hover {
    background-color: #eaeef2;
    border-color: #0969da;
    color: #0969da;
}
QPushButton#btn_popup_action:pressed {
    background-color: #dadfe5;
}
"""


class ConfigManager:
    CONFIG_FILE = "settings.json"

    @classmethod
    def get_config_path(cls):
        app_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(app_dir, cls.CONFIG_FILE)

    @classmethod
    def load(cls):
        app_dir = os.path.dirname(os.path.abspath(__file__))
        is_win = sys.platform == "win32"
        default_exe = os.path.join(app_dir, "gpssh.exe" if is_win else "gpssh")

        defaults = {
            "target_os": "windows" if is_win else "linux",
            "executable_path": default_exe,
            "theme": "dark",
            "work_dir": app_dir,
            "show_line_numbers": False
        }

        path = cls.get_config_path()
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                defaults.update(data)
            except Exception:
                pass
        return defaults

    @classmethod
    def save(cls, config):
        path = cls.get_config_path()
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception:
            pass


class BlockUserData(QTextBlockUserData):
    def __init__(self, label=""):
        super().__init__()
        self.label = label


class GPSSHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None, theme="dark"):
        super().__init__(parent)
        self.theme = theme
        self.rules = []
        self._init_formats()
        self._build_rules()

    def set_theme(self, theme):
        self.theme = theme
        self._init_formats()
        self._build_rules()
        self.rehighlight()

    def _init_formats(self):
        if self.theme == "dark":
            color_kw = QColor("#bcdfff")
            color_dir = QColor("#d2a8ff")
            color_sna = QColor("#79c0ff")
            color_num = QColor("#ffa657")
            color_comment = QColor("#7a8c9e")
            color_str = QColor("#7ee787")
        else:
            color_kw = QColor("#0969da")
            color_dir = QColor("#8250df")
            color_sna = QColor("#0550ae")
            color_num = QColor("#b78103")
            color_comment = QColor("#6c757d")
            color_str = QColor("#1a7f37")

        self.fmt_keyword = QTextCharFormat()
        self.fmt_keyword.setForeground(color_kw)
        self.fmt_keyword.setFontWeight(QFont.Bold)

        self.fmt_directive = QTextCharFormat()
        self.fmt_directive.setForeground(color_dir)
        self.fmt_directive.setFontWeight(QFont.Bold)

        self.fmt_sna = QTextCharFormat()
        self.fmt_sna.setForeground(color_sna)

        self.fmt_number = QTextCharFormat()
        self.fmt_number.setForeground(color_num)

        self.fmt_comment = QTextCharFormat()
        self.fmt_comment.setForeground(color_comment)
        self.fmt_comment.setFontItalic(True)

        self.fmt_string = QTextCharFormat()
        self.fmt_string.setForeground(color_str)

    def _build_rules(self):
        self.rules = []

        keywords = [
            "GENERATE", "TERMINATE", "SEIZE", "RELEASE", "ADVANCE",
            "QUEUE", "DEPART", "ENTER", "LEAVE", "STORAGE", "TRANSFER",
            "TEST", "ASSIGN", "MARK", "PRIORITY", "SPLIT", "ASSEMBLE",
            "GATHER", "MATCH", "PREEMPT", "RETURN", "SAVEVALUE",
            "MSAVEVALUE", "TABULATE", "GATE", "SELECT", "COUNT",
            "INDEX", "PRINT", "LOGIC", "BUFFER", "LINK", "UNLINK"
        ]
        for kw in keywords:
            pattern = QRegularExpression(rf"\b{kw}\b", QRegularExpression.CaseInsensitiveOption)
            self.rules.append((pattern, self.fmt_keyword))

        directives = [
            "START", "END", "CLEAR", "RESET", "FUNCTION", "VARIABLE",
            "BVARIABLE", "FVARIABLE", "INITIAL", "TABLE", "QTABLE",
            "SIMULATE", "DO", "ENDDO", "IF", "ELSE", "ENDIF", "GOTO",
            "INCLUDE", "INTEGER", "REAL", "AMPER", "PUTPIC", "PUTSTRING",
            "GETLIST"
        ]
        for d in directives:
            pattern = QRegularExpression(rf"\b{d}\b", QRegularExpression.CaseInsensitiveOption)
            self.rules.append((pattern, self.fmt_directive))

        sna_patterns = [
            r"\b[QqFfSsVvXx](?:A|C|M|T|X|R)?\$[A-Za-z0-9_#]+",
            r"\bFN\$[A-Za-z0-9_#]+",
            r"\b(?:RN[1-7]|C1|AC1|PR|M1|CA|W)\b"
        ]
        for sna in sna_patterns:
            self.rules.append((QRegularExpression(sna, QRegularExpression.CaseInsensitiveOption), self.fmt_sna))

        self.rules.append((QRegularExpression(r"\b\d+(?:\.\d+)?\b"), self.fmt_number))
        self.rules.append((QRegularExpression(r'"[^"\\]*(?:\\.[^"\\]*)*"'), self.fmt_string))
        self.rules.append((QRegularExpression(r"'[^'\\]*(?:\\.[^'\\]*)*'"), self.fmt_string))
        self.rules.append((QRegularExpression(r";[^\n]*"), self.fmt_comment))

    def highlightBlock(self, text):
        user_data = self.currentBlockUserData()
        if user_data and hasattr(user_data, "label") and user_data.label.strip().startswith("*"):
            self.setFormat(0, len(text), self.fmt_comment)
            return

        if text.strip().startswith("*"):
            self.setFormat(0, len(text), self.fmt_comment)
            return

        for pattern, fmt in self.rules:
            match_iter = pattern.globalMatch(text)
            while match_iter.hasNext():
                match = match_iter.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)


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
                # Line number (if enabled)
                if self.show_line_numbers:
                    painter.setPen(pen_line_num)
                    num_rect = QRect(0, top, line_w - 6, fm.height())
                    painter.drawText(num_rect, Qt.AlignRight | Qt.AlignVCenter, str(block_num))

                # Label
                ud = block.userData()
                lbl = ud.label if (ud and hasattr(ud, "label")) else ""
                lbl_rect = QRect(line_w + 2, top, lbl_w - 4, fm.height())
                if lbl:
                    painter.setPen(pen_filled)
                    painter.drawText(lbl_rect, Qt.AlignCenter, lbl)
                else:
                    painter.setPen(pen_empty)
                    painter.drawText(lbl_rect, Qt.AlignCenter, "_ _")

            block = block.next()
            top = bottom
            bottom = top + int(self.editor.blockBoundingRect(block).height())
            block_num += 1

        # Vertical borders
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


class SearchBar(QFrame):
    def __init__(self, editor, parent=None):
        super().__init__(parent)
        self.editor = editor
        self.setObjectName("search_bar")
        self.setFixedHeight(34)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 2, 8, 2)
        layout.setSpacing(6)

        lbl = QLabel("Поиск:")
        lbl.setStyleSheet("font-weight: 600; font-size: 12px;")

        self.edit_find = QLineEdit()
        self.edit_find.setPlaceholderText("Введите текст для поиска...")
        self.edit_find.returnPressed.connect(self.find_next)

        self.btn_prev = QPushButton("Назад")
        self.btn_prev.setFixedHeight(24)
        self.btn_prev.clicked.connect(self.find_prev)

        self.btn_next = QPushButton("Далее")
        self.btn_next.setFixedHeight(24)
        self.btn_next.clicked.connect(self.find_next)

        self.lbl_count = QLabel("")
        self.lbl_count.setStyleSheet("color: #7a8c9e; font-size: 11px;")

        self.btn_close = QPushButton("Закрыть")
        self.btn_close.setFixedHeight(24)
        self.btn_close.clicked.connect(self.hide_bar)

        layout.addWidget(lbl)
        layout.addWidget(self.edit_find, 1)
        layout.addWidget(self.btn_prev)
        layout.addWidget(self.btn_next)
        layout.addWidget(self.lbl_count)
        layout.addWidget(self.btn_close)

        self.hide()

    def show_bar(self):
        self.show()
        selected = self.editor.textCursor().selectedText()
        if selected and "\n" not in selected:
            self.edit_find.setText(selected)
        self.edit_find.setFocus()
        self.edit_find.selectAll()

    def hide_bar(self):
        self.hide()
        self.editor.setFocus()

    def find_next(self):
        text = self.edit_find.text()
        if not text:
            self.lbl_count.setText("")
            return
        found = self.editor.find(text)
        if not found:
            cursor = self.editor.textCursor()
            cursor.movePosition(QTextCursor.Start)
            self.editor.setTextCursor(cursor)
            found = self.editor.find(text)
        self._update_count(text)

    def find_prev(self):
        text = self.edit_find.text()
        if not text:
            self.lbl_count.setText("")
            return
        found = self.editor.find(text, QTextDocument.FindBackward)
        if not found:
            cursor = self.editor.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.editor.setTextCursor(cursor)
            found = self.editor.find(text, QTextDocument.FindBackward)
        self._update_count(text)

    def _update_count(self, text):
        if not text:
            self.lbl_count.setText("")
            return
        content = self.editor.toPlainText()
        total = content.lower().count(text.lower())
        if total == 0:
            self.lbl_count.setText("Не найдено")
        else:
            self.lbl_count.setText(f"Найдено: {total}")


class ActionMenuPopup(QFrame):
    def __init__(self, main_window):
        super().__init__(main_window, Qt.Popup | Qt.FramelessWindowHint)
        self.main_window = main_window
        self.setObjectName("action_menu_popup")
        self.setFixedWidth(240)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(5)

        def add_item(text, callback, shortcut=""):
            btn = QPushButton(text)
            btn.setObjectName("btn_popup_action")
            btn.setCursor(Qt.PointingHandCursor)
            if shortcut:
                btn.setToolTip(shortcut)
            btn.clicked.connect(lambda: [self.hide(), callback()])
            layout.addWidget(btn)
            return btn

        add_item("Новый  (Ctrl+N)", self.main_window.new_file)
        add_item("Открыть...  (Ctrl+O)", self.main_window.open_file)
        add_item("Сохранить  (Ctrl+S)", self.main_window.save_file)
        add_item("Сохранить как...  (Ctrl+Shift+S)", self.main_window.save_file_as)

        sep = QFrame()
        sep.setObjectName("popup_separator")
        sep.setFixedHeight(1)
        layout.addWidget(sep)

        add_item("Рабочая папка (.gps / .lis)", self.main_window.open_work_directory)
        add_item("Настройки...", self.main_window.open_settings)

    def show_under(self, widget):
        pos = widget.mapToGlobal(widget.rect().bottomLeft())
        x = pos.x() - (self.width() - widget.width())
        y = pos.y() + 4
        self.move(x, y)
        self.show()


class GPSSCodeEditor(QPlainTextEdit):
    gutterWidthChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
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


class SettingsDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки")
        self.resize(540, 270)
        self.config = dict(config)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.combo_os = QComboBox()
        self.combo_os.addItems(["Windows", "Linux"])
        if self.config.get("target_os", "windows").lower() == "linux":
            self.combo_os.setCurrentIndex(1)
        else:
            self.combo_os.setCurrentIndex(0)
        self.combo_os.currentIndexChanged.connect(self._on_os_changed)
        form.addRow("Операционная система:", self.combo_os)

        box_exe = QHBoxLayout()
        box_exe.setSpacing(6)
        self.edit_exe = QLineEdit(self.config.get("executable_path", ""))
        btn_browse_exe = QPushButton("Обзор...")
        btn_browse_exe.clicked.connect(self._browse_exe)
        box_exe.addWidget(self.edit_exe, 1)
        box_exe.addWidget(btn_browse_exe)
        form.addRow("Исполняемый файл GPSS:", box_exe)

        box_dir = QHBoxLayout()
        box_dir.setSpacing(6)
        self.edit_work_dir = QLineEdit(self.config.get("work_dir", ""))
        btn_browse_dir = QPushButton("Обзор...")
        btn_browse_dir.clicked.connect(self._browse_work_dir)
        btn_open_dir = QPushButton("Открыть")
        btn_open_dir.clicked.connect(self._open_folder)
        box_dir.addWidget(self.edit_work_dir, 1)
        box_dir.addWidget(btn_browse_dir)
        box_dir.addWidget(btn_open_dir)
        form.addRow("Рабочая папка:", box_dir)

        self.combo_theme = QComboBox()
        self.combo_theme.addItems(["Тёмная", "Светлая"])
        if self.config.get("theme", "dark") == "light":
            self.combo_theme.setCurrentIndex(1)
        else:
            self.combo_theme.setCurrentIndex(0)
        form.addRow("Тема оформления:", self.combo_theme)

        self.chk_lines = QCheckBox("Показывать номера строк в редакторе")
        self.chk_lines.setChecked(self.config.get("show_line_numbers", False))
        form.addRow("Нумерация строк:", self.chk_lines)

        layout.addLayout(form)
        layout.addStretch()

        btns_layout = QHBoxLayout()
        btns_layout.addStretch()
        btn_cancel = QPushButton("Отмена")
        btn_cancel.clicked.connect(self.reject)
        btn_save = QPushButton("Сохранить")
        btn_save.setObjectName("btn_save")
        btn_save.clicked.connect(self._save)
        btns_layout.addWidget(btn_cancel)
        btns_layout.addWidget(btn_save)

        layout.addLayout(btns_layout)

    def _on_os_changed(self, _):
        chosen_os = self.combo_os.currentText().lower()
        cur_path = self.edit_exe.text().strip()
        dirname, basename = os.path.split(cur_path)
        if basename in ("gpssh.exe", "gpssh", ""):
            new_name = "gpssh.exe" if chosen_os == "windows" else "gpssh"
            self.edit_exe.setText(os.path.join(dirname or self.config.get("work_dir", ""), new_name))

    def _browse_exe(self):
        cur_os = self.combo_os.currentText().lower()
        start_dir = os.path.dirname(self.edit_exe.text().strip()) or self.config.get("work_dir", "")
        filter_str = "Исполняемые файлы (*.exe);;Все файлы (*.*)" if cur_os == "windows" else "Все файлы (*.*)"
        path, _ = QFileDialog.getOpenFileName(self, "Выбор исполняемого файла GPSS", start_dir, filter_str)
        if path:
            self.edit_exe.setText(os.path.normpath(path))

    def _browse_work_dir(self):
        start_dir = self.edit_work_dir.text().strip() or os.getcwd()
        path = QFileDialog.getExistingDirectory(self, "Выбор рабочей папки", start_dir)
        if path:
            self.edit_work_dir.setText(os.path.normpath(path))

    def _open_folder(self):
        folder = self.edit_work_dir.text().strip()
        if not os.path.isdir(folder):
            folder = os.path.dirname(os.path.abspath(__file__))
        QDesktopServices.openUrl(QUrl.fromLocalFile(folder))

    def _save(self):
        self.config["target_os"] = self.combo_os.currentText().lower()
        self.config["executable_path"] = self.edit_exe.text().strip()
        self.config["work_dir"] = self.edit_work_dir.text().strip()
        self.config["theme"] = "dark" if self.combo_theme.currentIndex() == 0 else "light"
        self.config["show_line_numbers"] = self.chk_lines.isChecked()
        self.accept()


class GPSSStudio(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1180, 720)
        self.current_file_path = None

        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.config = ConfigManager.load()
        self.theme = self.config.get("theme", "dark")
        self.target_os = self.config.get("target_os", "windows")
        self.work_dir = self.config.get("work_dir", self.current_dir)
        self.exe_path = self.config.get("executable_path", os.path.join(self.work_dir, "gpssh.exe"))
        self.show_line_numbers = self.config.get("show_line_numbers", False)

        self.gps_file = os.path.join(self.work_dir, "model.gps")
        self.lis_file = os.path.join(self.work_dir, "model.lis")

        self.action_popup = ActionMenuPopup(self)
        self.apply_theme(self.theme)
        self._build_ui()
        self._setup_shortcuts()
        self._update_window_title()

        self.editor.load_code(DEFAULT_TEMPLATE)

    def apply_theme(self, theme):
        self.theme = theme
        sheet = STYLE_SHEET_LIGHT if theme == "light" else STYLE_SHEET_DARK
        self.setStyleSheet(sheet)
        if hasattr(self, "action_popup"):
            self.action_popup.setStyleSheet(sheet)
        if hasattr(self, "editor"):
            self.editor.set_theme(theme)
        if hasattr(self, "lbl_status_theme"):
            self.lbl_status_theme.setText(f"Тема: {'Светлая' if theme == 'light' else 'Тёмная'}")

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(12, 12, 12, 12)
        root_layout.setSpacing(10)

        # Верхняя панель
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
        btn_reset.clicked.connect(self.reset_model)

        self.lbl_status = QLabel(f"Рабочая папка: {self.work_dir}")
        self.lbl_status.setStyleSheet("color: #7a8c9e; margin-left: 6px; font-size: 11px;")

        self.btn_menu = QPushButton("⁝")
        self.btn_menu.setObjectName("btn_menu")
        self.btn_menu.setFixedSize(32, 32)
        self.btn_menu.setToolTip("Файл, Папка, Настройки...")
        self.btn_menu.setCursor(Qt.PointingHandCursor)
        self.btn_menu.clicked.connect(self._toggle_action_menu)

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
        top_layout.addWidget(self.btn_menu)
        top_layout.addWidget(btn_help)

        root_layout.addWidget(top_panel)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(8)
        mono_font = QFont("Consolas", 11)
        mono_font.setStyleHint(QFont.Monospace)

        # Левая часть (Редактор кода)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        # Шапка редактора кода
        editor_header = QFrame()
        editor_header.setObjectName("editor_header")
        editor_header.setFixedHeight(30)
        header_layout = QHBoxLayout(editor_header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)

        self.lbl_hdr_line = QLabel("СТР")
        self.lbl_hdr_line.setObjectName("lbl_hdr_line")
        self.lbl_hdr_line.setAlignment(Qt.AlignCenter)

        self.lbl_hdr_label = QLabel("МЕТКА")
        self.lbl_hdr_label.setObjectName("lbl_hdr_label")
        self.lbl_hdr_label.setAlignment(Qt.AlignCenter)

        self.lbl_hdr_code = QLabel("КОД МОДЕЛИ GPSS")
        self.lbl_hdr_code.setObjectName("lbl_hdr_code")
        self.lbl_hdr_code.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        header_layout.addWidget(self.lbl_hdr_line)
        header_layout.addWidget(self.lbl_hdr_label)
        header_layout.addWidget(self.lbl_hdr_code, 1)

        left_layout.addWidget(editor_header)

        self.editor = GPSSCodeEditor()
        self.editor.setFont(mono_font)
        self.editor.setTabStopDistance(QFontMetrics(mono_font).horizontalAdvance(' ') * 8)
        self.editor.gutter.show_line_numbers = self.show_line_numbers
        self.editor.set_theme(self.theme)
        self.editor.gutterWidthChanged.connect(self._sync_header_widths)
        self.editor.cursorPositionChanged.connect(self._update_cursor_info)
        self.editor.document().modificationChanged.connect(lambda _: self._update_window_title())

        self.search_bar = SearchBar(self.editor, left_widget)
        left_layout.addWidget(self.search_bar)
        left_layout.addWidget(self.editor, 1)

        self._sync_header_widths()
        splitter.addWidget(left_widget)

        # Правая часть (Результаты и листинг)
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

        # Строка состояния
        status_bar = self.statusBar()
        status_bar.setSizeGripEnabled(False)
        self.lbl_status_msg = QLabel("Готов")
        self.lbl_status_msg.setObjectName("status_msg")

        self.lbl_status_lines = QLabel("Всего строк: 1")
        self.lbl_status_lines.setObjectName("status_item")

        self.lbl_status_pos = QLabel("Стр: 1, Кол: 1")
        self.lbl_status_pos.setObjectName("status_item")

        self.lbl_status_os = QLabel(f"ОС: {'Windows' if self.target_os == 'windows' else 'Linux'}")
        self.lbl_status_os.setObjectName("status_item")

        self.lbl_status_theme = QLabel(f"Тема: {'Светлая' if self.theme == 'light' else 'Тёмная'}")
        self.lbl_status_theme.setObjectName("status_item")

        status_bar.addWidget(self.lbl_status_msg, 1)
        status_bar.addPermanentWidget(self.lbl_status_lines)
        status_bar.addPermanentWidget(self.lbl_status_pos)
        status_bar.addPermanentWidget(self.lbl_status_os)
        status_bar.addPermanentWidget(self.lbl_status_theme)

    def _toggle_action_menu(self):
        if self.action_popup.isVisible():
            self.action_popup.hide()
        else:
            self.action_popup.show_under(self.btn_menu)

    def _sync_header_widths(self):
        line_w = self.editor.gutter.line_num_width()
        lbl_w = self.editor.gutter.label_col_width()
        if self.editor.gutter.show_line_numbers:
            self.lbl_hdr_line.show()
            self.lbl_hdr_line.setFixedWidth(line_w)
            self.lbl_hdr_label.setFixedWidth(lbl_w)
        else:
            self.lbl_hdr_line.hide()
            self.lbl_hdr_label.setFixedWidth(self.editor.gutter_width())

    def _setup_shortcuts(self):
        QShortcut(QKeySequence("F5"), self, self.run_simulation)
        QShortcut(QKeySequence("Ctrl+G"), self, self._go_to_line)
        QShortcut(QKeySequence("Ctrl+F"), self, self.search_bar.show_bar)
        QShortcut(QKeySequence("Ctrl+N"), self, self.new_file)
        QShortcut(QKeySequence("Ctrl+O"), self, self.open_file)
        QShortcut(QKeySequence("Ctrl+S"), self, self.save_file)
        QShortcut(QKeySequence("Ctrl+Shift+S"), self, self.save_file_as)
        QShortcut(QKeySequence("Ctrl+1"), self, lambda: self.tabs.setCurrentIndex(0))
        QShortcut(QKeySequence("Ctrl+2"), self, lambda: self.tabs.setCurrentIndex(1))
        QShortcut(QKeySequence("Ctrl+3"), self, lambda: self.tabs.setCurrentIndex(2))

    def _update_cursor_info(self):
        cursor = self.editor.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        total = self.editor.document().blockCount()
        self.lbl_status_pos.setText(f"Стр: {line}, Кол: {col}")
        self.lbl_status_lines.setText(f"Всего строк: {total}")

    def _update_window_title(self):
        filename = os.path.basename(self.current_file_path) if self.current_file_path else "Новая модель"
        modified = " *" if self.editor.document().isModified() else ""
        self.setWindowTitle(f"{filename}{modified} - GPSS/H Studio")

    def _go_to_line(self):
        total = self.editor.document().blockCount()
        line, ok = QInputDialog.getInt(self, "Переход к строке", f"Номер строки (1-{total}):", 1, 1, total)
        if ok:
            block = self.editor.document().findBlockByNumber(line - 1)
            cursor = QTextCursor(block)
            self.editor.setTextCursor(cursor)
            self.editor.setFocus()

    def new_file(self):
        if self.editor.document().isModified():
            res = QMessageBox.question(
                self, "Несохранённые изменения",
                "Сохранить текущую модель перед созданием новой?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save
            )
            if res == QMessageBox.Save:
                if not self.save_file():
                    return
            elif res == QMessageBox.Cancel:
                return

        self.current_file_path = None
        self.editor.load_code(DEFAULT_TEMPLATE)
        self.editor.document().setModified(False)
        self._update_window_title()
        self.lbl_status_msg.setText("Создана новая модель")

    def open_file(self):
        if self.editor.document().isModified():
            res = QMessageBox.question(
                self, "Несохранённые изменения",
                "Сохранить текущие изменения перед открытием другого файла?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save
            )
            if res == QMessageBox.Save:
                if not self.save_file():
                    return
            elif res == QMessageBox.Cancel:
                return

        path, _ = QFileDialog.getOpenFileName(
            self, "Открыть модель GPSS",
            self.work_dir,
            "Модели GPSS (*.gps *.txt *.dat);;Все файлы (*.*)"
        )
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка открытия", f"Не удалось прочитать файл:\n{e}")
            return

        self.current_file_path = path
        self.editor.load_code(content)
        self.editor.document().setModified(False)
        self._update_window_title()
        self.lbl_status_msg.setText(f"Открыт файл: {os.path.basename(path)}")

    def save_file(self):
        if not self.current_file_path:
            return self.save_file_as()
        return self._do_save(self.current_file_path)

    def save_file_as(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить модель как...",
            self.work_dir,
            "Модели GPSS (*.gps);;Все файлы (*.*)"
        )
        if not path:
            return False
        return self._do_save(path)

    def _do_save(self, path):
        code = self.editor.get_formatted_code(target_os=self.target_os)
        try:
            with open(path, "w", encoding="utf-8", errors="replace", newline="") as f:
                f.write(code)
            self.current_file_path = path
            self.editor.document().setModified(False)
            self._update_window_title()
            self.lbl_status_msg.setText(f"Файл сохранён: {os.path.basename(path)}")
            return True
        except Exception as e:
            QMessageBox.critical(self, "Ошибка сохранения", f"Не удалось сохранить файл:\n{e}")
            return False

    def reset_model(self):
        self.editor.load_code(DEFAULT_TEMPLATE)
        self.lbl_status_msg.setText("Код сброшен к базовому шаблону")

    def open_work_directory(self):
        if not os.path.exists(self.work_dir):
            try:
                os.makedirs(self.work_dir, exist_ok=True)
            except Exception:
                pass
        QDesktopServices.openUrl(QUrl.fromLocalFile(self.work_dir))

    def open_settings(self):
        dialog = SettingsDialog(self.config, self)
        if dialog.exec():
            self.config = dialog.config
            ConfigManager.save(self.config)
            self._apply_config()

    def _apply_config(self):
        self.target_os = self.config.get("target_os", "windows")
        self.exe_path = self.config.get("executable_path", "")
        self.work_dir = self.config.get("work_dir", self.current_dir)
        self.theme = self.config.get("theme", "dark")
        self.show_line_numbers = self.config.get("show_line_numbers", False)

        self.editor.gutter.show_line_numbers = self.show_line_numbers
        self.editor.update_gutter_width(0)
        self.editor.gutter.update()
        self._sync_header_widths()

        self.gps_file = os.path.join(self.work_dir, "model.gps")
        self.lis_file = os.path.join(self.work_dir, "model.lis")

        self.lbl_status.setText(f"Рабочая папка: {self.work_dir}")
        self.lbl_status_os.setText(f"ОС: {'Windows' if self.target_os == 'windows' else 'Linux'}")
        self.apply_theme(self.theme)

    def closeEvent(self, event):
        if self.editor.document().isModified():
            res = QMessageBox.question(
                self, "Несохранённые изменения",
                "В модели есть несохранённые изменения. Сохранить перед выходом?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save
            )
            if res == QMessageBox.Save:
                if not self.save_file():
                    event.ignore()
                    return
            elif res == QMessageBox.Cancel:
                event.ignore()
                return
        event.accept()

    def run_simulation(self):
        if not os.path.exists(self.exe_path):
            QMessageBox.critical(
                self, "Ошибка",
                f"Исполняемый файл GPSS не найден!\n\nПуть: {self.exe_path}\n"
                f"Целевая ОС: {'Windows' if self.target_os == 'windows' else 'Linux'}\n\n"
                "Укажите правильный путь в настройках."
            )
            return

        if not os.path.exists(self.work_dir):
            try:
                os.makedirs(self.work_dir, exist_ok=True)
            except Exception:
                pass

        code = self.editor.get_formatted_code(target_os=self.target_os)

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

        try:
            if sys.platform != "win32" and os.path.exists(self.exe_path):
                try:
                    os.chmod(self.exe_path, 0o755)
                except Exception:
                    pass

            process = subprocess.run(
                [self.exe_path, "model.gps"],
                input="model.gps\n",
                cwd=self.work_dir,
                capture_output=True,
                text=True,
                timeout=5
            )
        except subprocess.TimeoutExpired:
            QMessageBox.warning(self, "Таймаут", "Процесс GPSS завис. Проверьте условия завершения модели.")
            return
        except Exception as e:
            QMessageBox.critical(self, "Ошибка запуска", f"Сбой при запуске GPSS:\n{e}")
            return

        self.console_viewer.setPlainText(f"STDOUT:\n{process.stdout}\n\nSTDERR:\n{process.stderr}")

        if not os.path.exists(self.lis_file):
            self.tabs.setCurrentIndex(2)
            self.lis_viewer.setPlainText("Файл model.lis не был создан. Проверьте вкладку консоли.")
            self.lbl_status_msg.setText("Ошибка запуска (файл листинга не создан)")
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
        self.lbl_status_msg.setText("Симуляция успешно завершена")

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
            it_val.setForeground(QColor("#bcdfff" if self.theme == "dark" else "#0969da"))
            it_desc = QTableWidgetItem(desc)

            self.summary_table.setItem(row, 0, it_param)
            self.summary_table.setItem(row, 1, it_val)
            self.summary_table.setItem(row, 2, it_desc)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GPSSStudio()
    window.show()
    sys.exit(app.exec())