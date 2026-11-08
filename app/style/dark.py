STYLE_SHEET_DARK = """
QMainWindow {
    background-color: #121718;
}
QWidget {
    color: #e0e5e9;
    font-family: "Segoe UI", "Ubuntu", "Cantarell", "DejaVu Sans", "Liberation Sans", Arial, sans-serif;
    font-size: 13px;
}
QFrame#top_panel {
    background-color: transparent;
    border: 0px solid #454e4f;
    border-radius: 0px;
}
QLabel#lbl_top_status {
    color: #8da4b5;
    margin-left: 6px;
    font-size: 11px;
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

QPlainTextEdit, QTextEdit {
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

QListWidget, QListView {
    background-color: #1b1f20;
    color: #e0e5e9;
    border: 1px solid #454e4f;
    border-radius: 3px;
    selection-background-color: #292f30;
    selection-color: #bcdfff;
    outline: none;
}
QListWidget::item, QListView::item {
    padding: 6px 10px;
    border-radius: 3px;
    color: #e0e5e9;
}
QListWidget::item:hover, QListView::item:hover {
    background-color: #292f30;
    color: #bcdfff;
}
QListWidget::item:selected, QListView::item:selected {
    background-color: #275782;
    color: #ffffff;
    font-weight: 600;
}

QToolTip {
    background-color: #292f30;
    color: #e0e5e9;
    border: 1px solid #454e4f;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 11px;
}

QMenu {
    background-color: #1f2426;
    color: #e0e5e9;
    border: 1px solid #454e4f;
    border-radius: 4px;
    padding: 4px 0px;
}
QMenu::item {
    background-color: transparent;
    padding: 5px 24px 5px 20px;
    color: #e0e5e9;
}
QMenu::item:selected {
    background-color: #275782;
    color: #ffffff;
}
QMenu::separator {
    height: 1px;
    background-color: #454e4f;
    margin: 4px 0px;
}

QGroupBox {
    background-color: #121718;
    color: #e0e5e9;
    border: 1px solid #454e4f;
    border-radius: 4px;
    margin-top: 14px;
    padding-top: 14px;
    font-weight: 600;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 0 4px;
    background-color: #121718;
    color: #bcdfff;
}

QPushButton {
    outline: none;
    font-weight: 600;
    border-radius: 0px;
    padding: 6px 16px;
    border: 1px solid transparent;
    color: #e0e5e9;
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
QPushButton#btn_run[running="true"] {
    background-color: #f85149;
    color: #ffffff;
    border: 1px solid #da3633;
}
QPushButton#btn_run[running="true"]:hover {
    background-color: #ff7b72;
    border: 1px solid #f85149;
}
QPushButton#btn_run[running="true"]:pressed {
    background-color: #b62324;
    border: 1px solid #b62324;
}
QPushButton#btn_reset, QPushButton#btn_templates, QPushButton#btn_report {
    background-color: #1f2426;
    color: #e0e5e9;
    border: 1px solid #454e4f;
    border-radius: 4px;
    padding: 6px 14px;
}
QPushButton#btn_reset:disabled, QPushButton#btn_templates:disabled, QPushButton#btn_report:disabled {
    color: #555e61;
    background-color: #16191a;
    border-color: #2b3133;
}
QPushButton#btn_reset:hover, QPushButton#btn_templates:hover, QPushButton#btn_report:hover {
    background-color: #292f30;
    border-color: #bcdfff;
    color: #ffffff;
}
QPushButton#btn_reset:pressed, QPushButton#btn_templates:pressed, QPushButton#btn_report:pressed {
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
    color: #e0e5e9;
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

QFrame#flowchart_toolbar, QFrame#chart_toolbar {
    background-color: #1b1f20;
    border: 1px solid #454e4f;
    border-radius: 0px;
}
QPushButton#btn_flowchart_tool, QPushButton#btn_chart_tool {
    outline: none;
    background-color: #1f2426;
    color: #e0e5e9;
    border: 1px solid #454e4f;
    border-radius: 3px;
    padding: 2px 10px;
    font-size: 12px;
    font-weight: 500;
}
QPushButton#btn_flowchart_tool:hover, QPushButton#btn_chart_tool:hover {
    background-color: #292f30;
    border-color: #bcdfff;
    color: #ffffff;
}
QPushButton#btn_flowchart_tool:pressed, QPushButton#btn_chart_tool:pressed {
    background-color: #1a2228;
}
QFrame#kpi_card {
    background-color: #1b1f20;
    border: 1px solid #454e4f;
    border-radius: 4px;
}
QLabel#kpi_card_title {
    color: #7a8c9e;
    font-size: 11px;
    font-weight: 500;
}
QLabel#kpi_card_value {
    color: #bcdfff;
    font-size: 15px;
    font-weight: bold;
}
QLabel#kpi_card_sub {
    color: #7a8c9e;
    font-size: 10px;
}
QFrame#grouping_banner {
    background-color: #1b1f20;
    border: 1px solid #454e4f;
    border-radius: 4px;
}
QLabel#grouping_banner_text {
    color: #bcdfff;
    font-size: 12px;
    font-weight: 600;
}
"""
