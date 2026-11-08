from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFrame, QHBoxLayout, QLabel, QComboBox, QPushButton, QMessageBox

from app.charts.chart_view import PerformanceChartView


class PerformanceDashboardWidget(QWidget):
    itemClicked = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = "dark"
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(6)

        self.kpi_banner = QFrame()
        self.kpi_banner.setObjectName("flowchart_toolbar")
        kpi_layout = QHBoxLayout(self.kpi_banner)
        kpi_layout.setContentsMargins(8, 6, 8, 6)
        kpi_layout.setSpacing(10)

        self.kpi_cards = []
        titles = [
            "Время Clock", "Скорость", "Ср. загрузка",
            "Узкое место", "Худшая очередь", "Всего блоков"
        ]
        subtitles = [
            "Абсолютное время", "Блоков / секунду", "Всех приборов",
            "Макс. занятость", "Макс. задержка", "Входов в блоки"
        ]
        for t, s in zip(titles, subtitles):
            card = QFrame()
            card.setObjectName("kpi_card")
            c_lay = QVBoxLayout(card)
            c_lay.setContentsMargins(8, 4, 8, 4)
            c_lay.setSpacing(2)

            lbl_t = QLabel(t)
            lbl_t.setObjectName("kpi_card_title")
            lbl_v = QLabel("-")
            lbl_v.setObjectName("kpi_card_value")
            lbl_s = QLabel(s)
            lbl_s.setObjectName("kpi_card_sub")

            c_lay.addWidget(lbl_t)
            c_lay.addWidget(lbl_v)
            c_lay.addWidget(lbl_s)
            kpi_layout.addWidget(card)
            self.kpi_cards.append((lbl_t, lbl_v, lbl_s))

        root.addWidget(self.kpi_banner)

        self.toolbar = QFrame()
        self.toolbar.setObjectName("chart_toolbar")
        self.toolbar.setFixedHeight(36)
        tb_lay = QHBoxLayout(self.toolbar)
        tb_lay.setContentsMargins(8, 4, 8, 4)
        tb_lay.setSpacing(8)

        lbl_chart = QLabel("График:")
        lbl_chart.setStyleSheet("font-weight: 600; font-size: 12px;")

        self.combo_chart_type = QComboBox()
        self.combo_chart_type.setObjectName("chart_type_combo")
        self.combo_chart_type.setFixedHeight(28)
        self.combo_chart_type.addItems([
            "Загрузка устройств (Facility Utilization)",
            "Очереди: средняя и макс. длина (Contents)",
            "Очереди: среднее время ожидания (Wait Time)",
            "Очереди: доля без ожидания (% Zeros)",
            "Узлы: Время в очереди vs Время обслуживания",
            "Нагрузка на блоки модели (Total Executions)",
            "Многоканальные устройства (Storages)"
        ])
        self.combo_chart_type.setFocusPolicy(Qt.NoFocus)
        self.combo_chart_type.currentIndexChanged.connect(self._on_type_changed)

        self.btn_copy_chart = QPushButton("Копировать график")
        self.btn_copy_chart.setObjectName("btn_chart_tool")
        self.btn_copy_chart.setFixedHeight(28)
        self.btn_copy_chart.setFocusPolicy(Qt.NoFocus)
        self.btn_copy_chart.clicked.connect(self._copy_chart)

        self.btn_save_chart = QPushButton("Экспорт PNG...")
        self.btn_save_chart.setObjectName("btn_chart_tool")
        self.btn_save_chart.setFixedHeight(28)
        self.btn_save_chart.setFocusPolicy(Qt.NoFocus)
        self.btn_save_chart.clicked.connect(lambda: self.chart_view.export_png(self))

        tb_lay.addWidget(lbl_chart)
        tb_lay.addWidget(self.combo_chart_type, 1)
        tb_lay.addStretch()
        tb_lay.addWidget(self.btn_copy_chart)
        tb_lay.addWidget(self.btn_save_chart)

        root.addWidget(self.toolbar)

        self.chart_view = PerformanceChartView(self)
        self.chart_view.itemClicked.connect(self.itemClicked.emit)
        root.addWidget(self.chart_view, 1)

    def _on_type_changed(self, idx):
        self.chart_view.set_chart_type(idx)

    def _copy_chart(self):
        if self.chart_view.copy_to_clipboard():
            QMessageBox.information(self, "Копирование", "График успешно скопирован в буфер обмена.")
        else:
            QMessageBox.warning(self, "Копирование", "Нет данных для копирования.")

    def set_theme(self, theme):
        self.theme = theme
        self.chart_view.set_theme(theme)

    def set_data(self, parser, device_groups, theme=None):
        if theme:
            self.theme = theme
        self.chart_view.set_data(parser, device_groups, self.theme)

        if parser:
            abs_clock = parser.clocks.get("absolute", "-")
            b_sec = parser.execution_stats.get("blocks_per_sec", "")
            if b_sec:
                try:
                    f_bsec = float(b_sec)
                    if f_bsec >= 1e6:
                        b_sec_str = f"{f_bsec/1e6:.1f}M бл/с"
                    elif f_bsec >= 1e3:
                        b_sec_str = f"{f_bsec/1e3:.1f}K бл/с"
                    else:
                        b_sec_str = f"{round(f_bsec)} бл/с"
                except Exception:
                    b_sec_str = f"{b_sec} бл/с"
            else:
                b_sec_str = "-"

            tot_blocks = parser.execution_stats.get("total_blocks", "-")

            if parser.facilities:
                utils = []
                for f in parser.facilities:
                    try:
                        utils.append(float(f['util']))
                    except Exception:
                        pass
                mean_u = (sum(utils) / len(utils)) if utils else 0.0
                mean_u_str = f"{round(mean_u * 100, 1)}%"

                b_fac = max(parser.facilities, key=lambda x: float(x.get('util', 0) or 0))
                b_str = f"{b_fac['name']} ({round(float(b_fac.get('util', 0) or 0)*100)}%)"
            else:
                mean_u_str = "-"
                b_str = "-"

            if parser.queues:
                worst_q = max(parser.queues, key=lambda x: float(x.get('avg_t', 0) or 0))
                w_val = float(worst_q.get('avg_t', 0) or 0)
                wq_str = f"{worst_q['name']} ({w_val:.1f}с)"
            else:
                wq_str = "-"

            self.kpi_cards[0][1].setText(abs_clock)
            self.kpi_cards[1][1].setText(b_sec_str)
            self.kpi_cards[2][1].setText(mean_u_str)
            self.kpi_cards[3][1].setText(b_str)
            self.kpi_cards[4][1].setText(wq_str)
            self.kpi_cards[5][1].setText(tot_blocks)

    def clear(self):
        self.chart_view.clear()
        for _, val_lbl, _ in self.kpi_cards:
            val_lbl.setText("-")
