import os
import re
import shutil
import sys

from PySide6.QtCore import Qt, QUrl, QTimer
from PySide6.QtGui import (
    QIcon, QFontMetrics, QDesktopServices, QTextCursor,
    QShortcut, QKeySequence, QColor, QTextFormat
)

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QFrame,
    QHBoxLayout, QPushButton, QLabel, QSplitter,
    QTabWidget, QLineEdit, QHeaderView, QPlainTextEdit,
    QApplication, QTextEdit, QTableWidget, QInputDialog,
    QMessageBox, QFileDialog, QTableWidgetItem
)

from app.charts.dashboard import PerformanceDashboardWidget
from app.config import ConfigManager
from app.consts import DEFAULT_TEMPLATE, GITHUB_URL
from app.editor.code_editor import GPSSCodeEditor
from app.editor.listing_viewer import ListingViewer
from app.editor.search_bar import SearchBar
from app.flowchart.widget import GPSSFlowchartWidget
from app.parsing.analysis import analyze_device_grouping
from app.parsing.listing import GPSSListingParser
from app.runner.dos_runner import DosRunner
from app.runner.windows_runner import WindowsRunner
from app.style.dark import STYLE_SHEET_DARK
from app.style.light import STYLE_SHEET_LIGHT
from app.util import get_monospace_font, get_ui_font, filter_table
from app.widgets.action_menu import ActionMenuPopup
from app.widgets.settings_dialog import SettingsDialog
from app.widgets.tables import ClickableTableWidget
from root import get_app_dir, get_resource_path


class GPSSStudio(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1440, 780)
        self.current_file_path = None
        self.sim_thread = None

        self.current_dir = get_app_dir()
        self.config = ConfigManager.load()
        self.theme = self.config.get("theme", "dark")
        self.target_os = self.config.get("target_os", "windows" if sys.platform == "win32" else "linux")
        self.work_dir = self.config.get("work_dir", self.current_dir)
        self.runner = self.get_runner()
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

        self.load_startup_file()
        self._update_window_title()
        self._refresh_flowchart_from_editor()

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

    def load_startup_file(self):
        last_opened = self.config.get("last_opened_file")
        if last_opened and os.path.exists(last_opened):
            try:
                with open(last_opened, "r", encoding="utf-8", errors="replace") as f:
                    c = f.read()
                if c.strip():
                    self.editor.load_code(c)
                    self.current_file_path = last_opened
                    return
            except Exception:
                pass

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

    def get_runner(self):
        dos_mode = self.config.get("use_dos_emulation", False)
        if not dos_mode:
            return WindowsRunner(self.config, self.target_os)
        else:
            return DosRunner(self.config, self.target_os)

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
        mono_font = get_monospace_font(mono_size)

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

        table_font = get_ui_font(max(9, round(12 * scale)))
        row_height = max(20, round(26 * scale))
        if hasattr(self, "all_summary_tables"):
            for tbl in self.all_summary_tables:
                tbl.setFont(table_font)
                tbl.horizontalHeader().setFont(table_font)
                tbl.verticalHeader().setDefaultSectionSize(row_height)

        if hasattr(self, "flowchart_widget"):
            self.flowchart_widget.set_theme(theme)
        if hasattr(self, "charts_widget"):
            self.charts_widget.set_theme(theme)

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
        self.btn_run.clicked.connect(self.run_stop_simulation_button)

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

        self.device_group_table = ClickableTableWidget()
        self.device_group_table.setColumnCount(12)
        self.device_group_table.setHorizontalHeaderLabels([
            "Устройство", "Тип", "Загрузка (Util)", "Входов", "Ср. время обслуж.",
            "Очередь", "Ср. длина очер.", "Макс. длина", "Ср. время очер.", "% без ожид.",
            "Ср. время в узле", "Статус"
        ])
        for c in range(12):
            self.device_group_table.horizontalHeader().setSectionResizeMode(c, QHeaderView.ResizeToContents)
        self.summary_subtabs.addTab(self.device_group_table, "По устройствам")

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
            self.overview_table, self.device_group_table, self.fac_table, self.q_table,
            self.storage_table, self.block_table, self.sys_table
        ]

        for tbl in self.all_summary_tables:
            tbl.ctrlClickedRow.connect(lambda row, t=tbl: self._jump_to_summary_row(t, row))
            tbl.cellClicked.connect(lambda r, c, t=tbl: self._on_table_cell_clicked(t, r, c))
            tbl.cellDoubleClicked.connect(lambda r, c, t=tbl: self._jump_to_summary_row(t, r))

        sum_layout.addWidget(self.summary_subtabs, 1)
        self.tabs.addTab(self.summary_widget, "Сводка для отчёта")

        self.flowchart_widget = GPSSFlowchartWidget()
        self.flowchart_widget.blockClicked.connect(self.jump_to_editor_line)
        self.flowchart_widget.refreshRequested.connect(self._refresh_flowchart_from_editor)
        self.flowchart_widget.set_theme(self.theme)
        self.tabs.addTab(self.flowchart_widget, "Блок-схема")

        self.charts_widget = PerformanceDashboardWidget()
        self.charts_widget.itemClicked.connect(self._on_chart_item_clicked)
        self.charts_widget.set_theme(self.theme)
        self.tabs.addTab(self.charts_widget, "Графики")

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

        self.tabs.currentChanged.connect(self._on_main_tab_changed)

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
        self.tabs.setCurrentIndex(3)
        self.lis_search_bar.show_bar()

    def _on_main_tab_changed(self, idx):
        if idx == 1:
            self._refresh_flowchart_from_editor()

    def _refresh_flowchart_from_editor(self):
        if hasattr(self, "flowchart_widget") and hasattr(self, "editor"):
            code = self.editor.get_formatted_code(target_os=self.target_os)
            stats = getattr(self, "_last_parser", None)
            self.flowchart_widget.update_model(code, stats)

    def jump_to_editor_line(self, line_no):
        if not line_no or line_no <= 0:
            return
        doc = self.editor.document()
        block = doc.findBlockByNumber(line_no - 1)
        if not block.isValid():
            return
        cursor = QTextCursor(block)
        self.editor.setTextCursor(cursor)
        self.editor.centerCursor()
        self.editor.setFocus()
        self.lbl_status_msg.setText(f"Переход к строке {line_no} в редакторе")

    def _on_chart_item_clicked(self, line_no):
        if line_no and line_no > 0:
            self.tabs.setCurrentIndex(3)
            self.jump_to_listing_line(line_no)

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
        QShortcut(QKeySequence("F5"), self, self.run_stop_simulation_button)
        QShortcut(QKeySequence("Ctrl+G"), self, self._go_to_line)
        QShortcut(QKeySequence("Ctrl+F"), self, self._handle_find_shortcut)
        QShortcut(QKeySequence("Ctrl+N"), self, self.new_file)
        QShortcut(QKeySequence("Ctrl+O"), self, self.open_file)
        QShortcut(QKeySequence("Ctrl+S"), self, self.save_file)
        QShortcut(QKeySequence("Ctrl+Shift+S"), self, self.save_file_as)
        QShortcut(QKeySequence("Ctrl+1"), self, lambda: self.tabs.setCurrentIndex(0))
        QShortcut(QKeySequence("Ctrl+2"), self, lambda: self.tabs.setCurrentIndex(1))
        QShortcut(QKeySequence("Ctrl+3"), self, lambda: self.tabs.setCurrentIndex(2))
        QShortcut(QKeySequence("Ctrl+4"), self, lambda: self.tabs.setCurrentIndex(3))
        QShortcut(QKeySequence("Ctrl+5"), self, lambda: self.tabs.setCurrentIndex(4))

        QShortcut(QKeySequence.ZoomIn, self, self.zoom_in)
        QShortcut(QKeySequence.ZoomOut, self, self.zoom_out)
        QShortcut(QKeySequence("Ctrl++"), self, self.zoom_in)
        QShortcut(QKeySequence("Ctrl+="), self, self.zoom_in)
        QShortcut(QKeySequence("Ctrl+-"), self, self.zoom_out)
        QShortcut(QKeySequence("Ctrl+0"), self, self.zoom_reset)

    def _handle_find_shortcut(self):
        if self.tabs.currentIndex() == 3 or self.lis_viewer.hasFocus():
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
        self.tabs.setCurrentIndex(3)
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
            os.path.dirname(self.current_file_path) if self.current_file_path else get_app_dir(),
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
        self.config["last_opened_file"] = self.current_file_path
        ConfigManager.save(self.config)
        self.lbl_status_msg.setText(f"Открыт файл: {os.path.basename(path)}")

    def save_file(self):
        if not self.current_file_path:
            return self.save_file_as()
        return self._do_save(self.current_file_path)

    def save_file_as(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить модель как...",
            os.path.dirname(self.current_file_path) if self.current_file_path else get_app_dir(),
            "Модели GPSS (*.gps);;Все файлы (*.*)"
        )
        if not path:
            return False
        is_saved = self._do_save(path)

        if is_saved:
            self.config["last_opened_file"] = self.current_file_path
            ConfigManager.save(self.config)

        return is_saved

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
            self.summary_subtabs.setTabVisible(4, True)
            self.summary_subtabs.setCurrentIndex(0)

        if hasattr(self, "flowchart_widget"):
            self.flowchart_widget.view.listing_stats = {}
            self.flowchart_widget.view.rebuild_flowchart()

        if hasattr(self, "charts_widget"):
            self.charts_widget.clear()

        self._last_parser = None

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
        self.runner.enshure_stop()

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
        self.target_os = self.config.get("target_os", "windows" if sys.platform == "win32" else "linux")
        self.runner = self.get_runner()

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

    # Кнопка "Закрыть"
    def closeEvent(self, event):

        self.runner.enshure_stop()

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

    def run_stop_simulation_button(self):
        if self.runner.is_running():
            self.stop_simulation()
        else:
            self.start_simulation()

    def stop_simulation(self):
        if self.runner.is_running():
            self.lbl_status_msg.setText("Остановка симуляции...")
            self.btn_run.setEnabled(False)
            self.runner.enshure_stop()

    def verify_exe_path(self):
        is_valid = self.runner.validate_runner_path()
        if not is_valid:
            QMessageBox.critical(self, "Ошибка", self.runner.get_failed_path_msg())
            return False
        return True

    def start_simulation(self):
        # Validate executable path with fallbacks
        if not self.verify_exe_path():
            return

        if not os.path.exists(self.work_dir):
            try:
                os.makedirs(self.work_dir, exist_ok=True)
            except Exception:
                pass

        code = self.editor.get_formatted_code(target_os=self.target_os)

        # Write model.gps with robust encoding handling
        written = False
        enc_list = ["cp866", "windows-1251", "utf-8"] if self.target_os == "windows" else ["utf-8", "latin-1", "cp866"]
        for enc in enc_list:
            try:
                with open(self.gps_file, "w", encoding=enc, newline="") as f:
                    f.write(code)
                written = True
                break
            except (UnicodeEncodeError, OSError):
                continue

        if not written:
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

        # Update UI to running state
        self.btn_run.setText("Остановить (F5)")
        self.btn_run.setProperty("running", "true")
        self.btn_run.style().unpolish(self.btn_run)
        self.btn_run.style().polish(self.btn_run)
        self.btn_reset.setEnabled(False)
        self.lbl_status_msg.setText("Запуск симуляции GPSS/H...")

        self.runner.run_gps(
            self.work_dir, self.gps_file, self.lis_file, self,
            self._on_simulation_status, self._on_simulation_finished
        )

    def _on_simulation_status(self, msg):
        self.lbl_status_msg.setText(msg)

    def _on_simulation_finished(self, success, retcode, stdout, stderr, lis_text, err_msg):
        # Restore run and reset button states
        self.btn_run.setEnabled(True)
        self.btn_run.setText("Запустить (F5)")
        self.btn_run.setProperty("running", "false")
        self.btn_run.style().unpolish(self.btn_run)
        self.btn_run.style().polish(self.btn_run)
        self.btn_reset.setEnabled(True)

        # Update console output
        console_out = f"STDOUT:\n{stdout}\n\nSTDERR:\n{stderr}"
        if self.config.get("use_dos_emulation"):
            dos_warn_msg = f'!!! ВНИМАНИЕ !!!\n\n' \
                           f'Вы запущены в режиме DOS-эмулятора\n' \
                           f'По широкому спектру причин(всё очень старое) получить ' \
                           f'вывод с консоли DOS-эмулятора НЕ ПОЛУЧИТСЯ\n' \
                           f'Чтобы проверить вывод эмулятора - переключите в настройках ' \
                           f'"Закрывать эмулятор DOS после выполнения"\n\n' \
                           f'!!! ВНИМАНИЕ !!!\n\n'
            console_out = dos_warn_msg + console_out
        if err_msg:
            console_out += f"\n\nСИСТЕМНОЕ СООБЩЕНИЕ:\n{err_msg}"
        self.console_viewer.setPlainText(console_out)

        if success:
            self.lis_viewer.setPlainText(lis_text)
            self._parse_and_fill_summary(lis_text)
            self._refresh_flowchart_from_editor()
            if self.config.get("switch_to_first_tab_after_simulating", False):
                self.tabs.setCurrentIndex(0)
            self.lbl_status_msg.setText("Симуляция успешно завершена")
        else:
            if lis_text:
                self.lis_viewer.setPlainText(lis_text)
                self._parse_and_fill_summary(lis_text)
            else:
                self.lis_viewer.setPlainText(f"Листинг недоступен.\n{err_msg}")
            self.tabs.setCurrentIndex(4)
            short_err = err_msg.split("\n")[0] if err_msg else "Ошибка запуска"
            self.lbl_status_msg.setText(f"Ошибка: {short_err}")
            QMessageBox.warning(self, "Результат симуляции", err_msg or "Произошла ошибка при выполнении модели.")

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
        self._last_parser = p

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

        code_str = self.editor.get_formatted_code(target_os=self.target_os)
        dev_groups, group_summary = analyze_device_grouping(p, code_str)

        self.device_group_table.setRowCount(len(dev_groups))
        for row, g in enumerate(dev_groups):
            items = [
                g['device'],
                g['type'],
                g['util'],
                g['entries'],
                g['avg_serv'],
                g['queue'],
                g['q_avg_len'],
                g['q_max_len'],
                g['q_avg_wait'],
                g['q_zero_pct'],
                g['total_node_time'],
                g['status']
            ]
            lno = g['line_no']
            for col, val in enumerate(items):
                it = QTableWidgetItem(str(val))
                it.setData(Qt.UserRole, lno)
                it.setToolTip(f"Ctrl + Клик для перехода к строке {lno} в листинге")
                it.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                if col in (1, 2, 3, 4, 6, 7, 8, 9, 10, 11):
                    it.setTextAlignment(Qt.AlignCenter)
                if col == 2:
                    u_val = g.get('util_val', 0.0)
                    if u_val >= 0.90:
                        it.setForeground(QColor("#f85149" if self.theme == "dark" else "#cf222e"))
                    elif u_val >= 0.70:
                        it.setForeground(QColor("#ffa657" if self.theme == "dark" else "#b78103"))
                    else:
                        it.setForeground(QColor("#7ee787" if self.theme == "dark" else "#1a7f37"))
                elif col in (4, 8, 10):
                    it.setForeground(QColor("#bcdfff" if self.theme == "dark" else "#0969da"))
                elif col == 11:
                    st = g['status']
                    if 'AVAIL' in st or 'BUSY' in st:
                        it.setForeground(QColor("#7ee787" if self.theme == "dark" else "#1a7f37"))
                    else:
                        it.setForeground(QColor("#ffa657" if self.theme == "dark" else "#b78103"))
                self.device_group_table.setItem(row, col, it)

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
            self.summary_subtabs.setTabVisible(4, True)
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
            self.summary_subtabs.setTabVisible(4, False)

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

        if hasattr(self, "charts_widget"):
            self.charts_widget.set_data(p, dev_groups, theme=self.theme)

        if hasattr(self, "flowchart_widget"):
            self.flowchart_widget.update_model(code_str, p)
