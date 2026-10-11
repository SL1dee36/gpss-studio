STYLE_SHEET_LIGHT = """
QMainWindow {
    background-color: #f6f8fa;
}
QWidget {
    color: #1f2328;
    font-family: "Segoe UI", "Ubuntu", "Cantarell", "DejaVu Sans", "Liberation Sans", Arial, sans-serif;
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
QPushButton#btn_run[running="true"] {
    background-color: #cf222e;
    color: #ffffff;
    border: 1px solid #a40e26;
}
QPushButton#btn_run[running="true"]:hover {
    background-color: #e5534b;
    border-color: #cf222e;
}
QPushButton#btn_run[running="true"]:pressed {
    background-color: #82071e;
    border-color: #82071e;
}
QPushButton#btn_reset {
    background-color: #f6f8fa;
    color: #24292f;
    border: 1px solid #d0d7de;
    border-radius: 4px;
    padding: 6px 14px;
}
QPushButton#btn_reset:disabled {
    color: #8c959f;
    background-color: #f3f4f6;
    border-color: #e1e4e8;
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

QFrame#flowchart_toolbar, QFrame#chart_toolbar {
    background-color: #f6f8fa;
    border: 1px solid #d0d7de;
    border-radius: 0px;
}
QPushButton#btn_flowchart_tool, QPushButton#btn_chart_tool {
    outline: none;
    background-color: #ffffff;
    color: #24292f;
    border: 1px solid #d0d7de;
    border-radius: 3px;
    padding: 2px 10px;
    font-size: 12px;
    font-weight: 500;
}
QPushButton#btn_flowchart_tool:hover, QPushButton#btn_chart_tool:hover {
    background-color: #f3f4f6;
    border-color: #0969da;
    color: #0969da;
}
QPushButton#btn_flowchart_tool:pressed, QPushButton#btn_chart_tool:pressed {
    background-color: #ebecf0;
}
QFrame#kpi_card {
    background-color: #ffffff;
    border: 1px solid #d0d7de;
    border-radius: 4px;
}
QLabel#kpi_card_title {
    color: #57606a;
    font-size: 11px;
    font-weight: 500;
}
QLabel#kpi_card_value {
    color: #0969da;
    font-size: 15px;
    font-weight: bold;
}
QLabel#kpi_card_sub {
    color: #656d76;
    font-size: 10px;
}
QFrame#grouping_banner {
    background-color: #ffffff;
    border: 1px solid #d0d7de;
    border-radius: 4px;
}
QLabel#grouping_banner_text {
    color: #0969da;
    font-size: 12px;
    font-weight: 600;
}
"""
