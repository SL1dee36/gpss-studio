from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFrame, QHBoxLayout, QPushButton, QComboBox, QCheckBox, QMessageBox

from app.flowchart.view import GPSSFlowchartView


class GPSSFlowchartWidget(QWidget):
    blockClicked = Signal(int)
    refreshRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = "dark"
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.toolbar = QFrame()
        self.toolbar.setObjectName("flowchart_toolbar")
        self.toolbar.setFixedHeight(36)
        tb_layout = QHBoxLayout(self.toolbar)
        tb_layout.setContentsMargins(8, 4, 8, 4)
        tb_layout.setSpacing(8)

        self.btn_zoom_in = QPushButton("+")
        self.btn_zoom_in.setObjectName("btn_flowchart_tool")
        self.btn_zoom_in.setFixedSize(28, 28)
        self.btn_zoom_in.setToolTip("Увеличить (Ctrl + колесо мыши)")
        self.btn_zoom_in.setFocusPolicy(Qt.NoFocus)

        self.btn_zoom_out = QPushButton("-")
        self.btn_zoom_out.setObjectName("btn_flowchart_tool")
        self.btn_zoom_out.setFixedSize(28, 28)
        self.btn_zoom_out.setToolTip("Уменьшить (Ctrl + колесо мыши)")
        self.btn_zoom_out.setFocusPolicy(Qt.NoFocus)

        self.btn_zoom_reset = QPushButton("100%")
        self.btn_zoom_reset.setObjectName("btn_flowchart_tool")
        self.btn_zoom_reset.setFixedHeight(28)
        self.btn_zoom_reset.setToolTip("Сбросить масштаб")
        self.btn_zoom_reset.setFocusPolicy(Qt.NoFocus)

        self.btn_zoom_fit = QPushButton("Вписать")
        self.btn_zoom_fit.setObjectName("btn_flowchart_tool")
        self.btn_zoom_fit.setFixedHeight(28)
        self.btn_zoom_fit.setToolTip("Вписать схему в окно")
        self.btn_zoom_fit.setFocusPolicy(Qt.NoFocus)

        self.combo_mode = QComboBox()
        self.combo_mode.setObjectName("flowchart_mode_combo")
        self.combo_mode.setFixedHeight(28)
        self.combo_mode.addItems(["Колонки (подсистемы)", "Вертикальный поток"])
        self.combo_mode.setFocusPolicy(Qt.NoFocus)

        self.chk_stats = QCheckBox("Счётчики симуляции")
        self.chk_stats.setChecked(True)
        self.chk_stats.setFocusPolicy(Qt.NoFocus)

        self.btn_refresh = QPushButton("Обновить схему")
        self.btn_refresh.setObjectName("btn_flowchart_tool")
        self.btn_refresh.setFixedHeight(28)
        self.btn_refresh.setFocusPolicy(Qt.NoFocus)

        self.btn_copy = QPushButton("Копировать")
        self.btn_copy.setObjectName("btn_flowchart_tool")
        self.btn_copy.setFixedHeight(28)
        self.btn_copy.setToolTip("Скопировать изображение блок-схемы в буфер обмена")
        self.btn_copy.setFocusPolicy(Qt.NoFocus)

        self.btn_save = QPushButton("Экспорт PNG...")
        self.btn_save.setObjectName("btn_flowchart_tool")
        self.btn_save.setFixedHeight(28)
        self.btn_save.setFocusPolicy(Qt.NoFocus)

        tb_layout.addWidget(self.btn_zoom_in)
        tb_layout.addWidget(self.btn_zoom_out)
        tb_layout.addWidget(self.btn_zoom_reset)
        tb_layout.addWidget(self.btn_zoom_fit)
        tb_layout.addWidget(self.combo_mode)
        tb_layout.addWidget(self.chk_stats)
        tb_layout.addStretch()
        tb_layout.addWidget(self.btn_refresh)
        tb_layout.addWidget(self.btn_copy)
        tb_layout.addWidget(self.btn_save)

        layout.addWidget(self.toolbar)

        self.view = GPSSFlowchartView(self)
        self.view.blockClicked.connect(self.blockClicked.emit)
        layout.addWidget(self.view, 1)

        self.btn_zoom_in.clicked.connect(self.view.zoom_in)
        self.btn_zoom_out.clicked.connect(self.view.zoom_out)
        self.btn_zoom_reset.clicked.connect(self.view.zoom_reset)
        self.btn_zoom_fit.clicked.connect(self.view.zoom_fit)
        self.combo_mode.currentIndexChanged.connect(self._on_mode_changed)
        self.chk_stats.toggled.connect(self._on_stats_toggled)
        self.btn_refresh.clicked.connect(self.refreshRequested.emit)
        self.btn_copy.clicked.connect(self._copy_diagram)
        self.btn_save.clicked.connect(lambda: self.view.export_png(self))

    def _on_mode_changed(self, idx):
        self.view.layout_mode = "lanes" if idx == 0 else "vertical"
        self.view.rebuild_flowchart()

    def _on_stats_toggled(self, checked):
        self.view.show_stats = checked
        self.view.rebuild_flowchart()

    def _copy_diagram(self):
        if self.view.copy_to_clipboard():
            QMessageBox.information(self, "Копирование", "Изображение блок-схемы успешно скопировано в буфер обмена.")
        else:
            QMessageBox.warning(self, "Копирование", "Схема пуста или не может быть скопирована.")

    def set_theme(self, theme):
        self.theme = theme
        self.view.set_theme(theme)

    def update_model(self, code_text, listing_stats=None):
        self.view.update_model(code_text, listing_stats)

    def update_stats(self, parser):
        if not parser or not parser.blocks:
            return
        stats = {}
        for b in parser.blocks:
            blk = b['block']
            cur = b['current']
            tot = b['total']
            if blk.isdigit():
                stats[int(blk)] = {'current': cur, 'total': tot}
            else:
                stats[blk.upper()] = {'current': cur, 'total': tot}
        self.view.listing_stats = stats
        self.view.rebuild_flowchart()
