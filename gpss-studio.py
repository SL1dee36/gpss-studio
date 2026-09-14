# Description: Lightweight desktop IDE and simulation runner for Wolverine Software GPSS/H
# Author: Nazaryan Artem @Sl1dee36
# Date: 15.09.2026
# Current version: v1.5.0-indev
# License: MIT

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
    QCheckBox, QStyledItemDelegate, QStyleOptionViewItem, QStyle
)
from PySide6.QtGui import (
    QFont, QFontMetrics, QKeySequence, QShortcut, QColor, 
    QPainter, QPen, QTextCursor, QTextBlockUserData, QDesktopServices,
    QSyntaxHighlighter, QTextCharFormat, QTextDocument, QTextFormat,
    QIcon
)
from PySide6.QtCore import Qt, QRect, QSize, QUrl, QRegularExpression, Signal, QPoint, QTimer

DEFAULT_TEMPLATE = """"""

CODE_VAR_16 = DEFAULT_TEMPLATE
GITHUB_URL = "https://github.com/SL1dee36/gpss-studio"

def get_app_dir():
    if "NUITKA_ONEFILE_BINARY" in os.environ:
        return os.path.dirname(os.path.abspath(os.environ["NUITKA_ONEFILE_BINARY"]))
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))

def get_resource_path(relative_path):
    candidates = []
    if hasattr(sys, "_MEIPASS"):
        candidates.append(sys._MEIPASS)
    try:
        candidates.append(os.path.dirname(os.path.abspath(__file__)))
    except Exception:
        pass
    candidates.append(get_app_dir())
    candidates.append(os.getcwd())

    for c_dir in candidates:
        if c_dir:
            full_path = os.path.join(c_dir, relative_path)
            if os.path.exists(full_path):
                return full_path

    return os.path.join(get_app_dir(), relative_path)


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
    font-size: 14px;
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
QFrame#search_bar QLabel {
    color: #b4c4d1;
    font-size: 12px;
    font-weight: 600;
}
QFrame#search_bar QLabel#search_lbl_count {
    color: #7a8c9e;
    font-size: 11px;
    font-weight: normal;
    border: none;
    background: transparent;
    padding: 0 4px;
}
QFrame#search_bar QLineEdit {
    background-color: #121718;
    color: #e0e5e9;
    border: 1px solid #454e4f;
    border-radius: 3px;
    padding: 2px 8px;
    font-size: 12px;
}
QFrame#search_bar QLineEdit:focus {
    border-color: #bcdfff;
}
QFrame#search_bar QPushButton {
    outline: none;
    background-color: #1f2426;
    color: #e0e5e9;
    border: 1px solid #454e4f;
    border-radius: 3px;
    padding: 2px 12px;
    font-size: 12px;
    font-weight: 500;
}
QFrame#search_bar QPushButton:focus {
    outline: none;
}
QFrame#search_bar QPushButton:hover {
    background-color: #292f30;
    border-color: #bcdfff;
    color: #ffffff;
}
QFrame#search_bar QPushButton:pressed {
    background-color: #1a2228;
}
QPushButton#btn_lis_find {
    outline: none;
    background-color: #1f2426;
    color: #e0e5e9;
    border: 1px solid #454e4f;
    border-radius: 3px;
    padding: 2px 12px;
    font-size: 12px;
    font-weight: 500;
}
QPushButton#btn_lis_find:focus {
    outline: none;
}
QPushButton#btn_lis_find:hover {
    background-color: #292f30;
    border-color: #bcdfff;
    color: #ffffff;
}
QPushButton#btn_lis_find:pressed {
    background-color: #1a2228;
}
QLabel#lbl_lis_file {
    color: #7a8c9e;
    font-size: 11px;
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
    outline: none;
    font-weight: 600;
    border-radius: 0px;
    padding: 6px 16px;
    border: 1px solid transparent;
}
QPushButton:focus {
    outline: none;
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
QPushButton#btn_copy_table {
    outline: none;
    background-color: #1f2426;
    color: #e0e5e9;
    border: 1px solid #454e4f;
    border-radius: 14px;
    padding: 2px 14px;
    font-size: 12px;
    font-weight: 600;
}
QPushButton#btn_copy_table:focus {
    outline: none;
}
QPushButton#btn_copy_table:hover {
    background-color: #292f30;
    border-color: #bcdfff;
    color: #ffffff;
}
QPushButton#btn_copy_table:pressed {
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
    outline: none;
    background-color: #121718;
    gridline-color: #292f30;
    border: none;
    border-radius: 0px;
    selection-background-color: #1f2e3d;
    selection-color: #e0e5e9;
}
QTableWidget::item {
    outline: none;
}
QTableWidget::item:focus {
    outline: none;
}
QTableWidget::item:selected {
    outline: none;
    background-color: #1f2e3d;
    color: #ffffff;
    font-weight: normal;
}
QHeaderView {
    background-color: #121718;
    border: none;
}
QHeaderView::section {
    background-color: #1b1f20;
    color: #bcdfff;
    border: none;
    border-right: 1px solid #292f30;
    border-bottom: 1px solid #292f30;
    border-radius: 0px;
    padding: 5px 8px;
    font-weight: 600;
}
QHeaderView::section:checked {
    font-weight: 600;
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
    border: none;
    border-right: 1px solid #292f30;
    border-bottom: 1px solid #292f30;
}

QTabWidget#summary_subtabs::pane {
    border: none;
    border-top: 1px solid #292f30;
    background-color: #121718;
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
    font-size: 14px;
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
QFrame#search_bar QLabel {
    color: #57606a;
    font-size: 12px;
    font-weight: 600;
}
QFrame#search_bar QLabel#search_lbl_count {
    color: #656d76;
    font-size: 11px;
    font-weight: normal;
    border: none;
    background: transparent;
    padding: 0 4px;
}
QFrame#search_bar QLineEdit {
    background-color: #ffffff;
    color: #1f2328;
    border: 1px solid #d0d7de;
    border-radius: 3px;
    padding: 2px 8px;
    font-size: 12px;
}
QFrame#search_bar QLineEdit:focus {
    border-color: #0969da;
}
QFrame#search_bar QPushButton {
    outline: none;
    background-color: #ffffff;
    color: #24292f;
    border: 1px solid #d0d7de;
    border-radius: 3px;
    padding: 2px 12px;
    font-size: 12px;
    font-weight: 500;
}
QFrame#search_bar QPushButton:focus {
    outline: none;
}
QFrame#search_bar QPushButton:hover {
    background-color: #f3f4f6;
    border-color: #0969da;
    color: #0969da;
}
QFrame#search_bar QPushButton:pressed {
    background-color: #ebecf0;
}
QPushButton#btn_lis_find {
    outline: none;
    background-color: #ffffff;
    color: #24292f;
    border: 1px solid #d0d7de;
    border-radius: 3px;
    padding: 2px 12px;
    font-size: 12px;
    font-weight: 500;
}
QPushButton#btn_lis_find:focus {
    outline: none;
}
QPushButton#btn_lis_find:hover {
    background-color: #f3f4f6;
    border-color: #0969da;
    color: #0969da;
}
QPushButton#btn_lis_find:pressed {
    background-color: #ebecf0;
}
QLabel#lbl_lis_file {
    color: #7a8c9e;
    font-size: 11px;
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
    outline: none;
    font-weight: 600;
    border-radius: 0px;
    padding: 6px 16px;
    border: 1px solid transparent;
}
QPushButton:focus {
    outline: none;
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
QPushButton#btn_copy_table {
    outline: none;
    background-color: #f6f8fa;
    color: #24292f;
    border: 1px solid #d0d7de;
    border-radius: 14px;
    padding: 2px 14px;
    font-size: 12px;
    font-weight: 600;
}
QPushButton#btn_copy_table:focus {
    outline: none;
}
QPushButton#btn_copy_table:hover {
    background-color: #f3f4f6;
    border-color: #0969da;
    color: #0969da;
}
QPushButton#btn_copy_table:pressed {
    background-color: #ebecf0;
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
    outline: none;
    background-color: #ffffff;
    gridline-color: #eaeef2;
    border: none;
    border-radius: 0px;
    selection-background-color: #b6d7f2;
    selection-color: #051d38;
}
QTableWidget::item {
    outline: none;
}
QTableWidget::item:focus {
    outline: none;
}
QTableWidget::item:selected {
    outline: none;
    background-color: #b6d7f2;
    color: #051d38;
    font-weight: normal;
}
QHeaderView {
    background-color: #ffffff;
    border: none;
}
QHeaderView::section {
    background-color: #f6f8fa;
    color: #0969da;
    border: none;
    border-right: 1px solid #eaeef2;
    border-bottom: 1px solid #d0d7de;
    border-radius: 0px;
    padding: 5px 8px;
    font-weight: 600;
}
QHeaderView::section:checked {
    font-weight: 600;
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
    background-color: #f6f8fa;
    border: none;
    border-right: 1px solid #eaeef2;
    border-bottom: 1px solid #d0d7de;
}

QTabWidget#summary_subtabs::pane {
    border: none;
    border-top: 1px solid #d0d7de;
    background-color: #ffffff;
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
        app_dir = get_app_dir()
        return os.path.join(app_dir, cls.CONFIG_FILE)

    @classmethod
    def load(cls):
        app_dir = get_app_dir()
        is_win = sys.platform == "win32"
        exe_name = "gpssh.exe" if is_win else "gpssh"
        default_exe = get_resource_path(exe_name)

        defaults = {
            "target_os": "windows" if is_win else "linux",
            "executable_path": default_exe,
            "theme": "dark",
            "work_dir": app_dir,
            "show_line_numbers": False,
            "zoom": 100
        }

        path = cls.get_config_path()
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                defaults.update(data)
            except Exception:
                pass

        # Если путь к исполняемому файлу из настроек не существует, пробуем fallback
        if not os.path.exists(defaults.get("executable_path", "")):
            candidate = get_resource_path(exe_name)
            if os.path.exists(candidate):
                defaults["executable_path"] = candidate

        # Если рабочая папка не существует, сбрасываем на папку приложения
        if not os.path.exists(defaults.get("work_dir", "")):
            defaults["work_dir"] = app_dir

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
                if self.show_line_numbers:
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

class SearchBar(QFrame):
    def __init__(self, editor, parent=None, title="Поиск:", placeholder="Введите текст для поиска..."):
        super().__init__(parent)
        self.editor = editor
        self.setObjectName("search_bar")
        self.setFixedHeight(36)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(6)

        lbl = QLabel(title)
        lbl.setObjectName("search_lbl_title")

        self.edit_find = QLineEdit()
        self.edit_find.setObjectName("search_edit")
        self.edit_find.setPlaceholderText(placeholder)
        self.edit_find.setFixedHeight(28)
        self.edit_find.returnPressed.connect(self.find_next)
        self.edit_find.textChanged.connect(self._on_text_changed)

        self.btn_prev = QPushButton("Назад")
        self.btn_prev.setObjectName("search_btn_prev")
        self.btn_prev.setFixedHeight(28)
        self.btn_prev.setCursor(Qt.PointingHandCursor)
        self.btn_prev.setFocusPolicy(Qt.NoFocus)
        self.btn_prev.clicked.connect(self.find_prev)

        self.btn_next = QPushButton("Далее")
        self.btn_next.setObjectName("search_btn_next")
        self.btn_next.setFixedHeight(28)
        self.btn_next.setCursor(Qt.PointingHandCursor)
        self.btn_next.setFocusPolicy(Qt.NoFocus)
        self.btn_next.clicked.connect(self.find_next)

        self.lbl_count = QLabel("")
        self.lbl_count.setObjectName("search_lbl_count")
        self.lbl_count.setAlignment(Qt.AlignCenter)

        self.btn_close = QPushButton("Закрыть")
        self.btn_close.setObjectName("search_btn_close")
        self.btn_close.setFixedHeight(28)
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.setFocusPolicy(Qt.NoFocus)
        self.btn_close.clicked.connect(self.hide_bar)

        layout.addWidget(lbl)
        layout.addWidget(self.edit_find, 1)
        layout.addWidget(self.btn_prev)
        layout.addWidget(self.btn_next)
        layout.addWidget(self.lbl_count)
        layout.addWidget(self.btn_close)

        self.hide()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.hide_bar()
            return
        super().keyPressEvent(event)

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

    def _on_text_changed(self, text):
        self._update_count(text)

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

class SettingsDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки")
        self.resize(540, 310)
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

        self.combo_zoom = QComboBox()
        self.combo_zoom.addItems(["75%", "80%", "90%", "100%", "110%", "125%", "150%", "175%", "200%"])
        cur_zoom = f"{self.config.get('zoom', 100)}%"
        idx = self.combo_zoom.findText(cur_zoom)
        if idx >= 0:
            self.combo_zoom.setCurrentIndex(idx)
        else:
            self.combo_zoom.setEditText(cur_zoom)
        form.addRow("Масштаб интерфейса (UI):", self.combo_zoom)

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
            folder = get_app_dir()
        QDesktopServices.openUrl(QUrl.fromLocalFile(folder))

    def _save(self):
        self.config["target_os"] = self.combo_os.currentText().lower()
        self.config["executable_path"] = self.edit_exe.text().strip()
        self.config["work_dir"] = self.edit_work_dir.text().strip()
        self.config["theme"] = "dark" if self.combo_theme.currentIndex() == 0 else "light"
        self.config["show_line_numbers"] = self.chk_lines.isChecked()
        try:
            zoom_str = self.combo_zoom.currentText().replace("%", "").strip()
            self.config["zoom"] = int(zoom_str)
        except Exception:
            self.config["zoom"] = 100
        self.accept()

class GPSSListingParser:
    def __init__(self, text):
        self.text = text
        self.lines = text.replace("\r\n", "\n").split("\n")
        self.header_info = {}
        self.clocks = {}
        self.model_size = {}
        self.storage_requirements = {}
        self.common_storage = {}
        self.execution_stats = {}
        self.elapsed_time = {}
        self.facilities = []
        self.queues = []
        self.storages = []
        self.blocks = []
        self.random_streams = []
        self.parse()

    def parse(self):
        state = None
        block_col_pos = []

        for idx, line in enumerate(self.lines):
            line_no = idx + 1
            s = line.strip()

            if "GPSS/H Release" in line and not self.header_info:
                m_ver = re.search(r"GPSS/H\s+Release\s+([^\s]+(?:\s*\([^\)]+\))?)", line)
                ver = m_ver.group(1) if m_ver else "GPSS/H"
                m_file = re.search(r"File:\s*([^\s]+)", line)
                f_name = m_file.group(1) if m_file else ""
                self.header_info = {"version": ver, "file": f_name, "line_no": line_no}

            if "Relative Clock:" in line:
                m_rel = re.search(r"Relative Clock:\s*([\d\.]+)", line)
                m_abs = re.search(r"Absolute Clock:\s*([\d\.]+)", line)
                self.clocks["relative"] = m_rel.group(1) if m_rel else "0.0"
                self.clocks["absolute"] = m_abs.group(1) if m_abs else "0.0"
                self.clocks["line_no"] = line_no

            if "Simulation complete." in line:
                m_abs = re.search(r"Absolute Clock:\s*([\d\.]+)", line)
                if m_abs:
                    self.clocks["absolute"] = m_abs.group(1)
                    if "line_no" not in self.clocks:
                        self.clocks["line_no"] = line_no

            if "Total Block Executions:" in line:
                m = re.search(r"Total Block Executions:\s*(\d+)", line)
                if m:
                    self.execution_stats["total_blocks"] = m.group(1)
                    self.execution_stats["line_no"] = line_no
            if "Blocks / second:" in line:
                m = re.search(r"Blocks\s*/\s*second:\s*([\d\.]+)", line)
                if m:
                    self.execution_stats["blocks_per_sec"] = m.group(1)
            if "Microseconds / Block:" in line:
                m = re.search(r"Microseconds\s*/\s*Block:\s*([\d\.]+)", line)
                if m:
                    self.execution_stats["us_per_block"] = m.group(1)

            if "Control Statements" in line and "Blocks" not in line:
                m = re.search(r"Control Statements\s+(\d+)", line)
                if m:
                    self.model_size["control_statements"] = m.group(1)
                    self.model_size["line_no"] = line_no
            if re.match(r"^\s*Blocks\s+\d+", line):
                m = re.search(r"Blocks\s+(\d+)", line)
                if m:
                    self.model_size["blocks"] = m.group(1)
                    if "line_no" not in self.model_size:
                        self.model_size["line_no"] = line_no

            if "Compiled Code:" in line:
                m = re.search(r"Compiled Code:\s*(\d+)", line)
                if m:
                    self.storage_requirements["compiled_code"] = m.group(1)
                    self.storage_requirements["line_no"] = line_no
            if "Compiled Data:" in line:
                m = re.search(r"Compiled Data:\s*(\d+)", line)
                if m:
                    self.storage_requirements["compiled_data"] = m.group(1)
            if "Entities:" in line and "Dictionary" not in line:
                m = re.search(r"Entities:\s*(\d+)", line)
                if m:
                    self.storage_requirements["entities"] = m.group(1)
            if "Common:" in line:
                m = re.search(r"Common:\s*(\d+)", line)
                if m:
                    self.storage_requirements["common"] = m.group(1)
            if re.match(r"^\s*Total:\s*\d+", line):
                m = re.search(r"Total:\s*(\d+)", line)
                if m:
                    self.storage_requirements["total"] = m.group(1)

            if "bytes available" in line:
                m = re.search(r"(\d+)\s+bytes available", line)
                if m:
                    self.common_storage["available"] = m.group(1)
                    self.common_storage["line_no"] = line_no
            if "in use" in line:
                m = re.search(r"(\d+)\s+in use", line)
                if m:
                    self.common_storage["in_use"] = m.group(1)
            if "used (max)" in line:
                m = re.search(r"(\d+)\s+used \(max\)", line)
                if m:
                    self.common_storage["max_used"] = m.group(1)

            if "Facility" in line and ("Total" in line or "Avail" in line):
                state = "facility_hdr"
                continue
            if state == "facility_hdr":
                if "Time" in line or "Status" in line:
                    state = "facilities"
                    continue
                state = None

            if state == "facilities":
                if not s or s.startswith("\x0c") or any(k in line for k in ["Queue", "Storage", "Random", "Status of", "Relative Clock", "Simulation"]):
                    state = None
                else:
                    name = line[0:10].strip()
                    if name and not name.startswith("-"):
                        self.facilities.append({
                            "line_no": line_no,
                            "name": name,
                            "util": line[10:17].strip() if len(line) > 10 else "",
                            "avail_util": line[17:24].strip() if len(line) > 17 else "",
                            "unavl_util": line[24:31].strip() if len(line) > 24 else "",
                            "entries": line[31:43].strip() if len(line) > 31 else "",
                            "avg_time": line[43:56].strip() if len(line) > 43 else "",
                            "status": line[56:66].strip() if len(line) > 56 else "",
                            "pct_avail": line[66:75].strip() if len(line) > 66 else "",
                            "seizing": line[75:85].strip() if len(line) > 75 else "",
                            "preempting": line[85:95].strip() if len(line) > 85 else ""
                        })

            if "Queue" in line and ("Maximum" in line or "Average" in line):
                state = "queue_hdr"
                continue
            if state == "queue_hdr":
                if "Contents" in line or "Entries" in line:
                    state = "queues"
                    continue
                state = None

            if state == "queues":
                if not s or s.startswith("\x0c") or any(k in line for k in ["Facility", "Storage", "Random", "Status of", "Relative Clock", "Simulation"]):
                    state = None
                else:
                    name = line[0:10].strip()
                    if name and not name.startswith("-"):
                        self.queues.append({
                            "line_no": line_no,
                            "name": name,
                            "max_c": line[10:21].strip() if len(line) > 10 else "",
                            "avg_c": line[21:34].strip() if len(line) > 21 else "",
                            "total_e": line[34:47].strip() if len(line) > 34 else "",
                            "zero_e": line[47:58].strip() if len(line) > 47 else "",
                            "pct_z": line[58:69].strip() if len(line) > 58 else "",
                            "avg_t": line[69:83].strip() if len(line) > 69 else "",
                            "dollar_avg_t": line[83:97].strip() if len(line) > 83 else "",
                            "qtable": line[97:107].strip() if len(line) > 97 else "",
                            "cur_c": line[107:].strip() if len(line) > 107 else ""
                        })

            if "Storage" in line and ("Capacity" in line or "Average" in line or "Avg-Util" in line):
                state = "storage_hdr"
                continue
            if state == "storage_hdr":
                if "Contents" in line or "Time" in line or "Status" in line:
                    state = "storages"
                    continue
                state = None

            if state == "storages":
                if not s or s.startswith("\x0c") or any(k in line for k in ["Facility", "Queue", "Random", "Status of", "Relative Clock", "Simulation"]):
                    state = None
                else:
                    name = line[0:10].strip()
                    if name and not name.startswith("-"):
                        self.storages.append({
                            "line_no": line_no,
                            "name": name,
                            "util": line[10:17].strip() if len(line) > 10 else "",
                            "avail_util": line[17:24].strip() if len(line) > 17 else "",
                            "unavl_util": line[24:31].strip() if len(line) > 24 else "",
                            "entries": line[31:43].strip() if len(line) > 31 else "",
                            "avg_time": line[43:56].strip() if len(line) > 43 else "",
                            "status": line[56:66].strip() if len(line) > 56 else "",
                            "pct_avail": line[66:76].strip() if len(line) > 66 else "",
                            "capacity": line[76:88].strip() if len(line) > 76 else "",
                            "avg_contents": line[88:100].strip() if len(line) > 88 else "",
                            "cur_contents": line[100:112].strip() if len(line) > 100 else "",
                            "max_contents": line[112:].strip() if len(line) > 112 else ""
                        })

            if "Block Current     Total" in line:
                state = "blocks"
                block_col_pos = [m.start() for m in re.finditer(r"Block", line)]
                continue
            if state == "blocks":
                if not s or s.startswith("\x0c") or any(k in line for k in ["Facility", "Storage", "Queue", "Random", "Status of", "Relative Clock", "Simulation"]):
                    state = None
                else:
                    for p in block_col_pos:
                        chunk = line[p:p+25]
                        if not chunk.strip():
                            continue
                        blk = chunk[:12].strip()
                        if not blk or blk == "Block":
                            continue
                        cur = chunk[12:18].strip() or "0"
                        tot = chunk[18:].strip()
                        self.blocks.append({
                            "line_no": line_no,
                            "block": blk,
                            "current": cur,
                            "total": tot
                        })

            if "Random    Antithetic" in line:
                state = "random_hdr"
                continue
            if state == "random_hdr":
                if "Stream" in line or "Variates" in line:
                    state = "random"
                    continue
                state = None
            if state == "random":
                if not s or s.startswith("\x0c") or any(k in line for k in ["Status of", "Simulation", "Facility", "Queue", "Storage"]):
                    state = None
                else:
                    parts = line.split()
                    if len(parts) >= 5:
                        self.random_streams.append({
                            "line_no": line_no,
                            "stream": parts[0],
                            "antithetic": parts[1],
                            "initial_pos": parts[2],
                            "current_pos": parts[3],
                            "sample_count": parts[4],
                            "chi_square": parts[5] if len(parts) > 5 else "N/A"
                        })

def filter_table(table, text):
    text = text.lower().strip()
    for r in range(table.rowCount()):
        if not text:
            table.setRowHidden(r, False)
            continue
        match = False
        for c in range(table.columnCount()):
            it = table.item(r, c)
            if it and text in it.text().lower():
                match = True
                break
        table.setRowHidden(r, not match)

class GPSSStudio(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1440, 780)
        self.current_file_path = None

        self.current_dir = get_app_dir()
        self.config = ConfigManager.load()
        self.theme = self.config.get("theme", "dark")
        self.target_os = self.config.get("target_os", "windows")
        self.work_dir = self.config.get("work_dir", self.current_dir)
        self.exe_path = self.config.get("executable_path", "")
        if not os.path.exists(self.exe_path):
            exe_name = "gpssh.exe" if sys.platform == "win32" else "gpssh"
            self.exe_path = get_resource_path(exe_name)
        self.show_line_numbers = self.config.get("show_line_numbers", False)
        self.zoom_level = self.config.get("zoom", 100)

        icon_path = get_resource_path("gpss-studio.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.gps_file = os.path.join(self.work_dir, "model.gps")
        self.lis_file = os.path.join(self.work_dir, "model.lis")

        self.action_popup = ActionMenuPopup(self)
        self._build_ui()
        self.apply_theme(self.theme)
        self._setup_shortcuts()
        self._update_window_title()

        if os.path.exists(self.gps_file):
            try:
                with open(self.gps_file, "r", encoding="utf-8", errors="replace") as f:
                    c = f.read()
                if c.strip():
                    self.editor.load_code(c)
                    self.current_file_path = self.gps_file
                else:
                    self.editor.load_code(DEFAULT_TEMPLATE)
            except Exception:
                self.editor.load_code(DEFAULT_TEMPLATE)
        else:
            self.editor.load_code(DEFAULT_TEMPLATE)

        if os.path.exists(self.lis_file):
            try:
                for enc in ("cp866", "latin-1", "utf-8"):
                    try:
                        with open(self.lis_file, "r", encoding=enc) as f:
                            lis_text = f.read()
                        break
                    except UnicodeDecodeError:
                        continue
                self.lis_viewer.setPlainText(lis_text)
                self._parse_and_fill_summary(lis_text)
            except Exception:
                pass

    def apply_theme(self, theme):
        self.theme = theme
        raw_sheet = STYLE_SHEET_LIGHT if theme == "light" else STYLE_SHEET_DARK
        scale = max(0.5, min(2.5, self.zoom_level / 100.0))

        if self.zoom_level == 100:
            sheet = raw_sheet
        else:
            sheet = re.sub(
                r"font-size:\s*(\d+)px",
                lambda m: f"font-size: {max(8, round(int(m.group(1)) * scale))}px",
                raw_sheet
            )

        self.setStyleSheet(sheet)
        if hasattr(self, "action_popup"):
            self.action_popup.setStyleSheet(sheet)

        mono_size = max(8, round(11 * scale))
        mono_font = QFont("Consolas", mono_size)
        mono_font.setStyleHint(QFont.Monospace)
        mono_font.setFixedPitch(True)

        if hasattr(self, "editor"):
            self.editor.setFont(mono_font)
            self.editor.set_theme(theme)
            self.editor.setTabStopDistance(QFontMetrics(mono_font).horizontalAdvance(' ') * 8)
            self.editor.update_gutter_width(0)
            self.editor.gutter.update()
            self._sync_header_widths()

        if hasattr(self, "lis_viewer"):
            self.lis_viewer.theme = theme
            self.lis_viewer.setFont(mono_font)
            self.lis_viewer.setTabStopDistance(QFontMetrics(mono_font).horizontalAdvance(' ') * 8)
            self.lis_viewer.update_line_number_area_width(0)
            self.lis_viewer.line_number_area.update()

        if hasattr(self, "console_viewer"):
            self.console_viewer.setFont(mono_font)
            self.console_viewer.setTabStopDistance(QFontMetrics(mono_font).horizontalAdvance(' ') * 8)

        table_font = QFont("Segoe UI", max(9, round(12 * scale)))
        row_height = max(20, round(26 * scale))
        if hasattr(self, "all_summary_tables"):
            for tbl in self.all_summary_tables:
                tbl.setFont(table_font)
                tbl.horizontalHeader().setFont(table_font)
                tbl.verticalHeader().setDefaultSectionSize(row_height)

        if hasattr(self, "lbl_status_theme"):
            self.lbl_status_theme.setText(f"Тема: {'Светлая' if theme == 'light' else 'Тёмная'}")
        if hasattr(self, "lbl_status_zoom"):
            self.lbl_status_zoom.setText(f"Масштаб: {self.zoom_level}%")

    def zoom_in(self):
        self.set_zoom(self.zoom_level + 10)

    def zoom_out(self):
        self.set_zoom(self.zoom_level - 10)

    def zoom_reset(self):
        self.set_zoom(100)

    def set_zoom(self, zoom_val):
        zoom_val = max(70, min(250, zoom_val))
        if zoom_val == self.zoom_level and hasattr(self, "_zoom_applied"):
            return
        self._zoom_applied = True
        self.zoom_level = zoom_val
        self.config["zoom"] = zoom_val
        ConfigManager.save(self.config)
        self.apply_theme(self.theme)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(12, 12, 12, 12)
        root_layout.setSpacing(10)

        self.top_panel = QFrame()
        self.top_panel.setObjectName("top_panel")
        self.top_panel.setFixedHeight(46)
        top_layout = QHBoxLayout(self.top_panel)
        top_layout.setContentsMargins(8, 4, 8, 4)
        top_layout.setSpacing(8)

        self.btn_run = QPushButton("Запустить (F5)")
        self.btn_run.setObjectName("btn_run")
        self.btn_run.setFixedHeight(32)
        self.btn_run.setFocusPolicy(Qt.NoFocus)
        self.btn_run.clicked.connect(self.run_simulation)

        self.btn_reset = QPushButton("Сбросить")
        self.btn_reset.setObjectName("btn_reset")
        self.btn_reset.setFixedHeight(32)
        self.btn_reset.setFocusPolicy(Qt.NoFocus)
        self.btn_reset.clicked.connect(self.reset_model)

        self.lbl_status = QLabel(f"Рабочая папка: {self.work_dir}")
        self.lbl_status.setStyleSheet("color: #7a8c9e; margin-left: 6px; font-size: 11px;")

        self.btn_menu = QPushButton("menu")
        self.btn_menu.setObjectName("btn_menu")
        self.btn_menu.setFixedSize(64, 32)
        self.btn_menu.setToolTip("Файл, Папка, Настройки...")
        self.btn_menu.setCursor(Qt.PointingHandCursor)
        self.btn_menu.setFocusPolicy(Qt.NoFocus)
        self.btn_menu.clicked.connect(self._toggle_action_menu)

        self.btn_help = QPushButton("help?")
        self.btn_help.setObjectName("btn_help")
        self.btn_help.setFixedSize(64, 32)
        self.btn_help.setToolTip(f"Открыть GitHub репозиторий:\n{GITHUB_URL}")
        self.btn_help.setCursor(Qt.PointingHandCursor)
        self.btn_help.setFocusPolicy(Qt.NoFocus)
        self.btn_help.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(GITHUB_URL)))

        top_layout.addWidget(self.btn_run)
        top_layout.addWidget(self.btn_reset)
        top_layout.addWidget(self.lbl_status)
        top_layout.addStretch()
        top_layout.addWidget(self.btn_menu)
        top_layout.addWidget(self.btn_help)

        root_layout.addWidget(self.top_panel)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(8)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        self.editor_header = QFrame()
        self.editor_header.setObjectName("editor_header")
        self.editor_header.setFixedHeight(36)
        header_layout = QHBoxLayout(self.editor_header)
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

        left_layout.addWidget(self.editor_header)

        self.editor = GPSSCodeEditor(main_window=self)
        self.editor.gutter.show_line_numbers = self.show_line_numbers
        self.editor.gutterWidthChanged.connect(self._sync_header_widths)
        self.editor.cursorPositionChanged.connect(self._update_cursor_info)
        self.editor.document().modificationChanged.connect(lambda _: self._update_window_title())

        self.search_bar = SearchBar(self.editor, left_widget, title="Поиск:", placeholder="Введите текст для поиска...")
        left_layout.addWidget(self.search_bar)
        left_layout.addWidget(self.editor, 1)

        self._sync_header_widths()
        splitter.addWidget(left_widget)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(6)

        self.tabs = QTabWidget()

        self.summary_widget = QWidget()
        sum_layout = QVBoxLayout(self.summary_widget)
        sum_layout.setContentsMargins(0, 0, 0, 0)
        sum_layout.setSpacing(4)

        sum_toolbar = QHBoxLayout()
        sum_toolbar.setContentsMargins(4, 4, 4, 4)
        sum_toolbar.setSpacing(8)

        self.summary_filter_edit = QLineEdit()
        self.summary_filter_edit.setObjectName("summary_filter_edit")
        self.summary_filter_edit.setFixedHeight(28)
        self.summary_filter_edit.setPlaceholderText("Поиск по таблице...")
        self.summary_filter_edit.textChanged.connect(self._on_summary_filter_changed)

        self.btn_copy_table = QPushButton("Скопировать таблицу")
        self.btn_copy_table.setObjectName("btn_copy_table")
        self.btn_copy_table.setFixedHeight(28)
        self.btn_copy_table.setToolTip("Скопировать содержимое текущей таблицы в буфер обмена")
        self.btn_copy_table.setCursor(Qt.PointingHandCursor)
        self.btn_copy_table.setFocusPolicy(Qt.NoFocus)
        self.btn_copy_table.clicked.connect(self.copy_current_table_to_clipboard)

        sum_toolbar.addWidget(self.summary_filter_edit, 1)
        sum_toolbar.addWidget(self.btn_copy_table)
        sum_layout.addLayout(sum_toolbar)

        self.summary_subtabs = QTabWidget()
        self.summary_subtabs.setObjectName("summary_subtabs")
        self.summary_subtabs.currentChanged.connect(self._on_summary_subtab_changed)

        self.overview_table = ClickableTableWidget()
        self.overview_table.setColumnCount(3)
        self.overview_table.setHorizontalHeaderLabels(["Параметр", "Значение", "Пояснение"])
        self.overview_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.overview_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.overview_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.summary_table = self.overview_table
        self.summary_subtabs.addTab(self.overview_table, "Сводка")

        self.fac_table = ClickableTableWidget()
        self.fac_table.setColumnCount(8)
        self.fac_table.setHorizontalHeaderLabels([
            "Устройство", "Загрузка (Util)", "Входов (Entries)", "Среднее время/заявку",
            "Статус", "% готовности", "Захвативший Xact", "Вытеснивший Xact"
        ])
        for c in range(8):
            self.fac_table.horizontalHeader().setSectionResizeMode(c, QHeaderView.ResizeToContents)
        self.summary_subtabs.addTab(self.fac_table, "Устройства")

        self.q_table = ClickableTableWidget()
        self.q_table.setColumnCount(10)
        self.q_table.setHorizontalHeaderLabels([
            "Очередь", "Макс. длина", "Средняя длина", "Всего заявок",
            "Нулевых входов", "% нулевых", "Среднее время",
            "$Среднее время", "Таблица", "Текущая длина"
        ])
        for c in range(10):
            self.q_table.horizontalHeader().setSectionResizeMode(c, QHeaderView.ResizeToContents)
        self.summary_subtabs.addTab(self.q_table, "Очереди")

        self.storage_table = ClickableTableWidget()
        self.storage_table.setColumnCount(9)
        self.storage_table.setHorizontalHeaderLabels([
            "Память", "Ёмкость", "Среднее содерж.", "Коэффициент загрузки",
            "Число входов", "Среднее время", "Статус", "Текущая занятость", "Пик (Max)"
        ])
        for c in range(9):
            self.storage_table.horizontalHeader().setSectionResizeMode(c, QHeaderView.ResizeToContents)
        self.summary_subtabs.addTab(self.storage_table, "Памяти")

        self.block_table = ClickableTableWidget()
        self.block_table.setColumnCount(3)
        self.block_table.setHorizontalHeaderLabels(["Блок / Метка", "Транзактов сейчас (Current)", "Всего транзактов (Total)"])
        self.block_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.block_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.block_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.summary_subtabs.addTab(self.block_table, "Блоки")

        self.sys_table = ClickableTableWidget()
        self.sys_table.setColumnCount(3)
        self.sys_table.setHorizontalHeaderLabels(["Параметр", "Значение", "Пояснение"])
        self.sys_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.sys_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.sys_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.summary_subtabs.addTab(self.sys_table, "Система")

        self.all_summary_tables = [
            self.overview_table, self.fac_table, self.q_table,
            self.storage_table, self.block_table, self.sys_table
        ]

        for tbl in self.all_summary_tables:
            tbl.ctrlClickedRow.connect(lambda row, t=tbl: self._jump_to_summary_row(t, row))
            tbl.cellClicked.connect(lambda r, c, t=tbl: self._on_table_cell_clicked(t, r, c))
            tbl.cellDoubleClicked.connect(lambda r, c, t=tbl: self._jump_to_summary_row(t, r))

        sum_layout.addWidget(self.summary_subtabs, 1)
        self.tabs.addTab(self.summary_widget, "Сводка для отчёта")

        self.lis_widget = QWidget()
        lis_layout = QVBoxLayout(self.lis_widget)
        lis_layout.setContentsMargins(0, 0, 0, 0)
        lis_layout.setSpacing(0)

        lis_header = QFrame()
        lis_header.setFixedHeight(36)
        lis_header.setObjectName("editor_header")
        lis_hdr_layout = QHBoxLayout(lis_header)
        lis_hdr_layout.setContentsMargins(8, 4, 8, 4)
        lis_hdr_layout.setSpacing(8)

        self.btn_lis_find = QPushButton("Найти")
        self.btn_lis_find.setObjectName("btn_lis_find")
        self.btn_lis_find.setFixedHeight(28)
        self.btn_lis_find.setCursor(Qt.PointingHandCursor)
        self.btn_lis_find.setFocusPolicy(Qt.NoFocus)
        self.btn_lis_find.clicked.connect(self._show_listing_search)

        self.lbl_lis_file = QLabel("model.lis")
        self.lbl_lis_file.setObjectName("lbl_lis_file")

        lis_hdr_layout.addWidget(self.btn_lis_find)
        lis_hdr_layout.addWidget(self.lbl_lis_file)
        lis_hdr_layout.addStretch()

        self.lis_viewer = ListingViewer(main_window=self)
        self.lis_viewer.setStyleSheet("font-family: Consolas, 'Courier New', monospace;")
        self.lis_search_bar = SearchBar(self.lis_viewer, self.lis_widget, title="Поиск:", placeholder="Введите текст для поиска по листингу...")

        lis_layout.addWidget(lis_header)
        lis_layout.addWidget(self.lis_search_bar)
        lis_layout.addWidget(self.lis_viewer, 1)

        self.tabs.addTab(self.lis_widget, "Полный листинг (.lis)")

        self.console_viewer = QPlainTextEdit()
        self.console_viewer.setReadOnly(True)
        self.console_viewer.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.console_viewer.setStyleSheet("font-family: Consolas, 'Courier New', monospace;")
        self.tabs.addTab(self.console_viewer, "Вывод консоли")

        right_layout.addWidget(self.tabs)
        splitter.addWidget(right_widget)

        splitter.setSizes([320, 1120])
        root_layout.addWidget(splitter, 1)

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

        self.lbl_status_zoom = QLabel(f"Масштаб: {self.zoom_level}%")
        self.lbl_status_zoom.setObjectName("status_item")
        self.lbl_status_zoom.setToolTip("Масштаб: Ctrl + / Ctrl - / Ctrl+0 (сброс)")
        self.lbl_status_zoom.setCursor(Qt.PointingHandCursor)

        def zoom_click(ev):
            if ev.button() == Qt.LeftButton:
                self.zoom_reset()
        self.lbl_status_zoom.mousePressEvent = zoom_click

        status_bar.addWidget(self.lbl_status_msg, 1)
        status_bar.addPermanentWidget(self.lbl_status_lines)
        status_bar.addPermanentWidget(self.lbl_status_pos)
        status_bar.addPermanentWidget(self.lbl_status_os)
        status_bar.addPermanentWidget(self.lbl_status_theme)
        status_bar.addPermanentWidget(self.lbl_status_zoom)

    def _show_listing_search(self):
        self.tabs.setCurrentIndex(1)
        self.lis_search_bar.show_bar()

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
        QShortcut(QKeySequence("Ctrl+F"), self, self._handle_find_shortcut)
        QShortcut(QKeySequence("Ctrl+N"), self, self.new_file)
        QShortcut(QKeySequence("Ctrl+O"), self, self.open_file)
        QShortcut(QKeySequence("Ctrl+S"), self, self.save_file)
        QShortcut(QKeySequence("Ctrl+Shift+S"), self, self.save_file_as)
        QShortcut(QKeySequence("Ctrl+1"), self, lambda: self.tabs.setCurrentIndex(0))
        QShortcut(QKeySequence("Ctrl+2"), self, lambda: self.tabs.setCurrentIndex(1))
        QShortcut(QKeySequence("Ctrl+3"), self, lambda: self.tabs.setCurrentIndex(2))

        QShortcut(QKeySequence.ZoomIn, self, self.zoom_in)
        QShortcut(QKeySequence.ZoomOut, self, self.zoom_out)
        QShortcut(QKeySequence("Ctrl++"), self, self.zoom_in)
        QShortcut(QKeySequence("Ctrl+="), self, self.zoom_in)
        QShortcut(QKeySequence("Ctrl+-"), self, self.zoom_out)
        QShortcut(QKeySequence("Ctrl+0"), self, self.zoom_reset)

    def _handle_find_shortcut(self):
        if self.tabs.currentIndex() == 1 or self.lis_viewer.hasFocus():
            self.lis_search_bar.show_bar()
        else:
            self.search_bar.show_bar()

    def _on_table_cell_clicked(self, table, row, col):
        if QApplication.keyboardModifiers() & Qt.ControlModifier:
            self._jump_to_summary_row(table, row)

    def _jump_to_summary_row(self, table, row):
        item = table.item(row, 0)
        if not item:
            return
        line_no = item.data(Qt.UserRole)
        if not line_no or line_no <= 0:
            return
        self.tabs.setCurrentIndex(1)
        self.jump_to_listing_line(line_no)

    def jump_to_listing_line(self, line_no):
        doc = self.lis_viewer.document()
        block = doc.findBlockByNumber(line_no - 1)
        if not block.isValid():
            return

        cursor = QTextCursor(block)
        self.lis_viewer.setTextCursor(cursor)
        self.lis_viewer.centerCursor()
        self.lis_viewer.setFocus()

        sel = QTextEdit.ExtraSelection()
        is_dark = (self.theme == "dark")
        sel.format.setBackground(QColor("#1e4976" if is_dark else "#ffe58f"))
        sel.format.setProperty(QTextFormat.FullWidthSelection, True)
        sel.cursor = cursor
        self.lis_viewer.setExtraSelections([sel])

        self.lbl_status_msg.setText(f"Переход к строке {line_no} в листинге")

        if hasattr(self, "_highlight_timer") and self._highlight_timer:
            self._highlight_timer.stop()
        else:
            self._highlight_timer = QTimer(self)
            self._highlight_timer.setSingleShot(True)
            self._highlight_timer.timeout.connect(lambda: self.lis_viewer.setExtraSelections([]))

        self._highlight_timer.start(3000)

    def copy_current_table_to_clipboard(self):
        cur_subtab = self.summary_subtabs.currentWidget()
        if not cur_subtab or not isinstance(cur_subtab, QTableWidget):
            return
        table = cur_subtab
        lines = []
        headers = []
        for c in range(table.columnCount()):
            it = table.horizontalHeaderItem(c)
            headers.append(it.text() if it else f"Колонка {c+1}")
        lines.append("\t".join(headers))

        for r in range(table.rowCount()):
            if table.isRowHidden(r):
                continue
            row_data = []
            for c in range(table.columnCount()):
                it = table.item(r, c)
                row_data.append(it.text() if it else "")
            lines.append("\t".join(row_data))

        tsv_text = "\n".join(lines)
        QApplication.clipboard().setText(tsv_text)
        tab_name = self.summary_subtabs.tabText(self.summary_subtabs.currentIndex())
        self.lbl_status_msg.setText(f"Таблица '{tab_name}' скопирована в буфер обмена")

    def _on_summary_filter_changed(self, text):
        cur_subtab = self.summary_subtabs.currentWidget()
        if cur_subtab and isinstance(cur_subtab, QTableWidget):
            filter_table(cur_subtab, text)

    def _on_summary_subtab_changed(self, _):
        text = self.summary_filter_edit.text()
        cur_subtab = self.summary_subtabs.currentWidget()
        if cur_subtab and isinstance(cur_subtab, QTableWidget):
            filter_table(cur_subtab, text)

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
        if hasattr(self, "search_bar"):
            self.search_bar.hide_bar()
            self.search_bar.edit_find.clear()
        self.reset_right_frame()
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

    def reset_right_frame(self):
        if hasattr(self, "summary_filter_edit"):
            self.summary_filter_edit.clear()
        if hasattr(self, "all_summary_tables"):
            for tbl in self.all_summary_tables:
                tbl.setRowCount(0)
        if hasattr(self, "summary_subtabs"):
            self.summary_subtabs.setTabVisible(3, True)
            self.summary_subtabs.setCurrentIndex(0)

        if hasattr(self, "lis_viewer"):
            self.lis_viewer.clear()
            self.lis_viewer.setExtraSelections([])
        if hasattr(self, "_highlight_timer") and self._highlight_timer:
            self._highlight_timer.stop()
        if hasattr(self, "lis_search_bar"):
            self.lis_search_bar.hide_bar()
            self.lis_search_bar.edit_find.clear()
        if hasattr(self, "lbl_lis_file"):
            self.lbl_lis_file.setText("model.lis")

        if hasattr(self, "console_viewer"):
            self.console_viewer.clear()

        if hasattr(self, "tabs"):
            self.tabs.setCurrentIndex(0)

    def reset_model(self):
        self.editor.load_code(DEFAULT_TEMPLATE)
        self.current_file_path = None
        self.editor.document().setModified(False)
        self._update_window_title()
        if hasattr(self, "search_bar"):
            self.search_bar.hide_bar()
            self.search_bar.edit_find.clear()
        self.reset_right_frame()
        self.lbl_status_msg.setText("Модель и результаты сброшены")

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
        self.zoom_level = self.config.get("zoom", 100)

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

    def _populate_key_value_table(self, table, data):
        table.setRowCount(len(data))
        for row, item_info in enumerate(data):
            param = item_info[0]
            val = item_info[1]
            desc = item_info[2]
            line_no = item_info[3] if len(item_info) > 3 else 1

            it_param = QTableWidgetItem(param)
            it_val = QTableWidgetItem(val)
            it_desc = QTableWidgetItem(desc)

            for it in (it_param, it_val, it_desc):
                it.setData(Qt.UserRole, line_no)
                it.setToolTip(f"Ctrl + Клик для перехода к строке {line_no} в листинге")
                it.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

            it_val.setTextAlignment(Qt.AlignCenter)
            it_val.setForeground(QColor("#bcdfff" if self.theme == "dark" else "#0969da"))

            table.setItem(row, 0, it_param)
            table.setItem(row, 1, it_val)
            table.setItem(row, 2, it_desc)

    def _parse_and_fill_summary(self, text):
        p = GPSSListingParser(text)

        overview_data = []

        abs_c = p.clocks.get("absolute", "Н/Д")
        rel_c = p.clocks.get("relative", abs_c)
        clock_line = p.clocks.get("line_no", 1)
        overview_data.append(("Время моделирования (Absolute Clock)", abs_c, "Общая длительность работы системы в тактах", clock_line))
        if rel_c != abs_c and rel_c != "Н/Д":
            overview_data.append(("Относительное время (Relative Clock)", rel_c, "Время с момента последнего сброса статистики", clock_line))

        if p.model_size:
            ctrl = p.model_size.get("control_statements", "")
            blocks_cnt = p.model_size.get("blocks", "")
            msz_line = p.model_size.get("line_no", 1)
            overview_data.append(("Размер модели", f"{blocks_cnt} блоков, {ctrl} упр. опер.", "Число блоков и управляющих операторов в модели", msz_line))

        if p.execution_stats:
            tot_b = p.execution_stats.get("total_blocks", "")
            b_sec = p.execution_stats.get("blocks_per_sec", "")
            us_blk = p.execution_stats.get("us_per_block", "")
            ex_line = p.execution_stats.get("line_no", 1)
            if tot_b:
                overview_data.append(("Всего выполнено блоков (Total Executions)", tot_b, "Суммарное число входов транзактов во все блоки модели", ex_line))
            if b_sec:
                overview_data.append(("Скорость симуляции (Blocks / second)", b_sec, "Производительность интерпретатора GPSS", ex_line))
            if us_blk:
                overview_data.append(("Время на один блок (Microseconds / Block)", us_blk, "Среднее процессорное время на обработку одного блока", ex_line))

        if p.common_storage:
            in_use = p.common_storage.get("in_use", "")
            avail = p.common_storage.get("available", "")
            max_u = p.common_storage.get("max_used", "")
            cs_line = p.common_storage.get("line_no", 1)
            overview_data.append(("Память системы (Common Storage)", f"{in_use} байт занято (макс. {max_u})", f"Доступно: {avail} байт", cs_line))

        for f in p.facilities:
            fn = f["name"]
            lno = f["line_no"]
            overview_data.append((f"Устройство {fn}: Загрузка (Avg-Util)", f["util"], f"Коэффициент занятости прибора {fn} [0..1]", lno))
            overview_data.append((f"Устройство {fn}: Заявок (Entries)", f["entries"], f"Количество заявок, обслуженных прибором {fn}", lno))
            overview_data.append((f"Устройство {fn}: Среднее время (Avg Time)", f["avg_time"], f"Среднее время занятия прибора {fn} (такты)", lno))
            st_text = f["status"] + (f" (Xact: {f['seizing']})" if f['seizing'] else "")
            overview_data.append((f"Устройство {fn}: Статус", st_text, f"Текущее состояние прибора {fn}", lno))

        for q in p.queues:
            qn = q["name"]
            lno = q["line_no"]
            overview_data.append((f"Очередь {qn}: Всего заявок (Total Entries)", q["total_e"], f"Общее число заявок, поступивших в очередь {qn}", lno))
            overview_data.append((f"Очередь {qn}: Макс. длина (Max Contents)", q["max_c"], f"Пиковая длина очереди {qn}", lno))
            overview_data.append((f"Очередь {qn}: Средняя длина (Avg Contents)", q["avg_c"], f"Среднее число ожидающих заявок в очереди {qn}", lno))
            overview_data.append((f"Очередь {qn}: Среднее время ожидания", q["avg_t"], f"Среднее время нахождения в очереди {qn} (такты)", lno))
            overview_data.append((f"Очередь {qn}: Доля без ожидания (%)", f"{q['pct_z']}%", f"Процент заявок с нулевым временем ожидания (нулевые входы: {q['zero_e']})", lno))

        for s in p.storages:
            sn = s["name"]
            lno = s["line_no"]
            overview_data.append((f"Память {sn}: Загрузка (Avg-Util)", s["util"], f"Коэффициент загрузки многоканального устройства {sn}", lno))
            overview_data.append((f"Память {sn}: Ёмкость (Capacity)", s["capacity"], f"Максимальная вместимость памяти {sn}", lno))
            overview_data.append((f"Память {sn}: Среднее число занятых", s["avg_contents"], f"Среднее количество одновременно занятых каналов {sn}", lno))
            overview_data.append((f"Память {sn}: Всего заявок (Entries)", s["entries"], f"Число заявок, вошедших в память {sn}", lno))

        for r in p.random_streams:
            st = r["stream"]
            lno = r["line_no"]
            overview_data.append((f"ГСЧ поток {st}: Число выборок", r["sample_count"], f"Текущая позиция: {r['current_pos']}, исходная: {r['initial_pos']}", lno))

        self._populate_key_value_table(self.overview_table, overview_data)

        self.fac_table.setRowCount(len(p.facilities))
        for row, f in enumerate(p.facilities):
            lno = f["line_no"]
            items = [
                f["name"],
                f["util"],
                f["entries"],
                f["avg_time"],
                f["status"],
                f["pct_avail"] or "100.0",
                f["seizing"] or "-",
                f["preempting"] or "-"
            ]
            for col, val in enumerate(items):
                it = QTableWidgetItem(val)
                it.setData(Qt.UserRole, lno)
                it.setToolTip(f"Ctrl + Клик для перехода к строке {lno} в листинге")
                it.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                if col in (1, 2, 3, 5, 6, 7):
                    it.setTextAlignment(Qt.AlignCenter)
                if col == 1:
                    it.setForeground(QColor("#bcdfff" if self.theme == "dark" else "#0969da"))
                elif col == 4:
                    it.setForeground(QColor("#7ee787" if f['status'] == 'AVAIL' else "#ffa657"))
                self.fac_table.setItem(row, col, it)

        self.q_table.setRowCount(len(p.queues))
        for row, q in enumerate(p.queues):
            lno = q["line_no"]
            items = [
                q["name"],
                q["max_c"],
                q["avg_c"],
                q["total_e"],
                q["zero_e"],
                f"{q['pct_z']}%",
                q["avg_t"],
                q["dollar_avg_t"],
                q["qtable"] or "-",
                q["cur_c"]
            ]
            for col, val in enumerate(items):
                it = QTableWidgetItem(val)
                it.setData(Qt.UserRole, lno)
                it.setToolTip(f"Ctrl + Клик для перехода к строке {lno} в листинге")
                it.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                if col >= 1:
                    it.setTextAlignment(Qt.AlignCenter)
                if col in (1, 2, 3, 6):
                    it.setForeground(QColor("#bcdfff" if self.theme == "dark" else "#0969da"))
                self.q_table.setItem(row, col, it)

        if p.storages:
            self.summary_subtabs.setTabVisible(3, True)
            self.storage_table.setRowCount(len(p.storages))
            for row, s in enumerate(p.storages):
                lno = s["line_no"]
                items = [
                    s["name"],
                    s["capacity"],
                    s["avg_contents"],
                    s["util"],
                    s["entries"],
                    s["avg_time"],
                    s["status"],
                    s["cur_contents"],
                    s["max_contents"]
                ]
                for col, val in enumerate(items):
                    it = QTableWidgetItem(val)
                    it.setData(Qt.UserRole, lno)
                    it.setToolTip(f"Ctrl + Клик для перехода к строке {lno} в листинге")
                    it.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                    if col >= 1:
                        it.setTextAlignment(Qt.AlignCenter)
                    if col in (1, 2, 3, 4, 5):
                        it.setForeground(QColor("#bcdfff" if self.theme == "dark" else "#0969da"))
                    self.storage_table.setItem(row, col, it)
        else:
            self.storage_table.setRowCount(0)
            self.summary_subtabs.setTabVisible(3, False)

        self.block_table.setRowCount(len(p.blocks))
        for row, b in enumerate(p.blocks):
            lno = b["line_no"]
            it_blk = QTableWidgetItem(b["block"])
            it_cur = QTableWidgetItem(b["current"])
            it_tot = QTableWidgetItem(b["total"])

            for it in (it_blk, it_cur, it_tot):
                it.setData(Qt.UserRole, lno)
                it.setToolTip(f"Ctrl + Клик для перехода к строке {lno} в листинге")
                it.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

            it_cur.setTextAlignment(Qt.AlignCenter)
            it_tot.setTextAlignment(Qt.AlignCenter)
            if b["current"] != "0":
                it_cur.setForeground(QColor("#ffa657" if self.theme == "dark" else "#b78103"))
            it_tot.setForeground(QColor("#bcdfff" if self.theme == "dark" else "#0969da"))

            self.block_table.setItem(row, 0, it_blk)
            self.block_table.setItem(row, 1, it_cur)
            self.block_table.setItem(row, 2, it_tot)

        sys_data = []
        if p.clocks:
            sys_data.append(("Время Relative Clock", p.clocks.get("relative", ""), "Относительные часы модели", p.clocks.get("line_no", 1)))
            sys_data.append(("Время Absolute Clock", p.clocks.get("absolute", ""), "Абсолютные часы модели", p.clocks.get("line_no", 1)))
        if p.execution_stats:
            sys_data.append(("Всего выполнено блоков", p.execution_stats.get("total_blocks", ""), "Суммарное число входов транзактов", p.execution_stats.get("line_no", 1)))
            sys_data.append(("Скорость симуляции", f"{p.execution_stats.get('blocks_per_sec', '')} блоков/сек", "Скорость выполнения интерпретатора", p.execution_stats.get("line_no", 1)))
            sys_data.append(("Время на один блок", f"{p.execution_stats.get('us_per_block', '')} мкс", "Микросекунд на обработку блока", p.execution_stats.get("line_no", 1)))
        if p.storage_requirements:
            sr = p.storage_requirements
            s_line = sr.get("line_no", 1)
            sys_data.append(("Память: Скомпилированный код", f"{sr.get('compiled_code', '')} байт", "Размер исполняемого кода модели", s_line))
            sys_data.append(("Память: Скомпилированные данные", f"{sr.get('compiled_data', '')} байт", "Статические данные модели", s_line))
            sys_data.append(("Память: Сущности (Entities)", f"{sr.get('entities', '')} байт", "Память под структуры очередей, приборов и т.д.", s_line))
            sys_data.append(("Память: Common Storage", f"{sr.get('common', '')} байт", "Размер общей памяти GPSS", s_line))
            sys_data.append(("Память: ИТОГО", f"{sr.get('total', '')} байт", "Общие требования к памяти", s_line))
        if p.common_storage:
            cs = p.common_storage
            cs_line = cs.get("line_no", 1)
            sys_data.append(("Common Storage: Доступно", f"{cs.get('available', '')} байт", "Свободная динамическая память", cs_line))
            sys_data.append(("Common Storage: Занято", f"{cs.get('in_use', '')} байт", "Текущее использование", cs_line))
            sys_data.append(("Common Storage: Пик занятости", f"{cs.get('max_used', '')} байт", "Максимальное использование памяти за прогон", cs_line))
        for r in p.random_streams:
            sys_data.append((f"ГСЧ поток #{r['stream']}", f"Выборок: {r['sample_count']} (поз: {r['current_pos']})", f"Антитетичность: {r['antithetic']}, Начало: {r['initial_pos']}, Хи-квадрат: {r['chi_square']}", r["line_no"]))

        self._populate_key_value_table(self.sys_table, sys_data)

        for tbl in self.all_summary_tables:
            tbl.resizeColumnsToContents()
            if tbl.columnCount() >= 3 and tbl in (self.overview_table, self.sys_table):
                tbl.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)

if __name__ == "__main__":
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("sl1dee36.gpssstudio.ide.1.5")
        except Exception:
            pass

    app = QApplication(sys.argv)

    icon_path = get_resource_path("gpss-studio.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    window = GPSSStudio()
    window.show()
    sys.exit(app.exec())
