import math

from PySide6.QtCore import Signal, QPointF, Qt, QRectF
from PySide6.QtGui import QPixmap, QColor, QPainter, QFont, QPen, QBrush
from PySide6.QtWidgets import QWidget, QSizePolicy, QApplication, QFileDialog


class PerformanceChartView(QWidget):
    itemClicked = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = "dark"
        self.chart_type = 0
        self.parser = None
        self.device_groups = []
        self.hovered_item = None
        self.hover_pos = QPointF(0, 0)
        self.hit_boxes = []
        self.setMouseTracking(True)
        self.setMinimumHeight(340)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def set_theme(self, theme):
        self.theme = theme
        self.update()

    def set_chart_type(self, idx):
        self.chart_type = idx
        self.hovered_item = None
        self.update()

    def set_data(self, parser, device_groups, theme=None):
        self.parser = parser
        self.device_groups = device_groups
        if theme:
            self.theme = theme
        self.hovered_item = None
        self.update()

    def clear(self):
        self.parser = None
        self.device_groups = []
        self.hovered_item = None
        self.update()

    def mouseMoveEvent(self, event):
        pos = event.position()
        found = False
        for rect, item in self.hit_boxes:
            if rect.contains(pos):
                self.hovered_item = item
                self.hover_pos = pos
                self.setCursor(Qt.PointingHandCursor if item.get('line_no') else Qt.ArrowCursor)
                self.update()
                found = True
                break
        if not found and self.hovered_item is not None:
            self.hovered_item = None
            self.setCursor(Qt.ArrowCursor)
            self.update()
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.hovered_item and self.hovered_item.get('line_no'):
            self.itemClicked.emit(self.hovered_item['line_no'])
        super().mousePressEvent(event)

    def render_to_pixmap(self):
        pixmap = QPixmap(self.size())
        pixmap.fill(QColor("#121718" if self.theme == "dark" else "#ffffff"))
        p = QPainter(pixmap)
        p.setRenderHint(QPainter.Antialiasing)
        self._paint_content(p, self.width(), self.height(), is_export=True)
        p.end()
        return pixmap

    def copy_to_clipboard(self):
        pixmap = self.render_to_pixmap()
        if pixmap:
            QApplication.clipboard().setPixmap(pixmap)
            return True
        return False

    def export_png(self, parent):
        path, _ = QFileDialog.getSaveFileName(
            parent, "Экспорт графика в PNG", "", "Изображение PNG (*.png)"
        )
        if not path:
            return False
        pixmap = self.render_to_pixmap()
        if pixmap:
            return pixmap.save(path, "PNG")
        return False

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        self._paint_content(p, self.width(), self.height(), is_export=False)
        p.end()

    def _paint_content(self, p, w, h, is_export=False):
        is_dark = (self.theme == "dark")
        bg_color = QColor("#121718" if is_dark else "#ffffff")
        p.fillRect(0, 0, w, h, bg_color)

        text_primary = QColor("#e0e5e9" if is_dark else "#1f2328")
        text_muted = QColor("#7a8c9e" if is_dark else "#57606a")
        grid_color = QColor("#292f30" if is_dark else "#eaeef2")
        border_color = QColor("#454e4f" if is_dark else "#d0d7de")
        accent_color = QColor("#bcdfff" if is_dark else "#0969da")

        if not is_export:
            self.hit_boxes = []

        if not self.parser or not (self.parser.facilities or self.parser.queues or self.parser.blocks):
            p.setPen(text_muted)
            p.setFont(QFont("Segoe UI", 13))
            p.drawText(QRectF(0, 0, w, h), Qt.AlignCenter, "Нет данных моделирования.\nЗапустите модель (F5), чтобы построить графики.")
            return

        titles = [
            "Коэффициенты загрузки устройств (Facility Utilization)",
            "Характеристики очередей: средняя и максимальная длина",
            "Среднее время ожидания в очередях (Avg Wait Time)",
            "Доля заявок с нулевым временем ожидания (% Zeros)",
            "Структура задержки в узлах: время в очереди vs время обслуживания",
            "Интенсивность блоков модели: общее число транзактов",
            "Многоканальные устройства (Storage Utilization & Capacity)"
        ]
        title_text = titles[min(self.chart_type, len(titles)-1)]

        p.setFont(QFont("Segoe UI", 12, QFont.Bold))
        p.setPen(accent_color)
        p.drawText(QRectF(30, 15, w - 60, 26), Qt.AlignLeft | Qt.AlignVCenter, title_text)

        m_l, m_r, m_t, m_b = 65, 40, 60, 60
        pw = w - m_l - m_r
        ph = h - m_t - m_b
        if pw <= 40 or ph <= 40:
            return

        p.setPen(QPen(border_color, 1))
        p.drawLine(m_l, m_t + ph, m_l + pw, m_t + ph)
        p.drawLine(m_l, m_t, m_l, m_t + ph)

        if self.chart_type == 0:
            self._draw_facility_util(p, m_l, m_t, pw, ph, is_dark, text_primary, text_muted, grid_color)
        elif self.chart_type == 1:
            self._draw_queue_lengths(p, m_l, m_t, pw, ph, is_dark, text_primary, text_muted, grid_color)
        elif self.chart_type == 2:
            self._draw_queue_wait_times(p, m_l, m_t, pw, ph, is_dark, text_primary, text_muted, grid_color)
        elif self.chart_type == 3:
            self._draw_queue_zeros(p, m_l, m_t, pw, ph, is_dark, text_primary, text_muted, grid_color)
        elif self.chart_type == 4:
            self._draw_node_composition(p, m_l, m_t, pw, ph, is_dark, text_primary, text_muted, grid_color)
        elif self.chart_type == 5:
            self._draw_block_executions(p, m_l, m_t, pw, ph, is_dark, text_primary, text_muted, grid_color)
        elif self.chart_type == 6:
            self._draw_storage_stats(p, m_l, m_t, pw, ph, is_dark, text_primary, text_muted, grid_color)

        if not is_export and self.hovered_item:
            self._draw_tooltip(p, w, h, is_dark)

    def _draw_facility_util(self, p, ml, mt, pw, ph, is_dark, text_primary, text_muted, grid_color):
        facs = self.parser.facilities
        if not facs:
            p.drawText(QRectF(ml, mt, pw, ph), Qt.AlignCenter, "Нет данных об одноканальных устройствах")
            return

        for step in (0.0, 0.25, 0.5, 0.75, 1.0):
            y = mt + ph - step * ph
            p.setPen(QPen(grid_color, 1, Qt.DashLine))
            p.drawLine(ml, y, ml + pw, y)
            p.setPen(text_muted)
            p.setFont(QFont("Segoe UI", 8))
            p.drawText(QRectF(ml - 55, y - 9, 48, 18), Qt.AlignRight | Qt.AlignVCenter, f"{round(step*100)}%")

        y_80 = mt + ph - 0.8 * ph
        p.setPen(QPen(QColor("#ff7b72" if is_dark else "#cf222e"), 1, Qt.DotLine))
        p.drawLine(ml, y_80, ml + pw, y_80)
        p.setFont(QFont("Segoe UI", 8, QFont.Bold))
        p.drawText(QRectF(ml + pw - 150, y_80 - 18, 145, 16), Qt.AlignRight, "80% (Порог перегрузки)")

        n = len(facs)
        slot_w = pw / n
        bar_w = min(48.0, max(18.0, slot_w * 0.65))

        for i, f in enumerate(facs):
            try:
                val = float(f['util'])
            except Exception:
                val = 0.0

            bx = ml + i * slot_w + (slot_w - bar_w) / 2
            bh = min(val, 1.0) * ph
            by = mt + ph - bh

            if val >= 0.90:
                color = QColor("#f85149" if is_dark else "#cf222e")
            elif val >= 0.70:
                color = QColor("#d29922" if is_dark else "#b78103")
            else:
                color = QColor("#388bfd" if is_dark else "#0969da")

            bar_rect = QRectF(bx, by, bar_w, bh)
            p.setBrush(QBrush(color))
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(bar_rect, 4, 4)

            p.setPen(text_primary)
            p.setFont(QFont("Segoe UI", 9, QFont.Bold))
            p.drawText(QRectF(bx - 15, by - 20, bar_w + 30, 18), Qt.AlignCenter, f"{round(val*100, 1)}%")

            p.drawText(QRectF(bx - 15, mt + ph + 6, bar_w + 30, 18), Qt.AlignCenter, f['name'])

            p.setFont(QFont("Segoe UI", 8))
            p.setPen(text_muted)
            p.drawText(QRectF(bx - 20, mt + ph + 24, bar_w + 40, 16), Qt.AlignCenter, f"{f['entries']} вх.")

            self.hit_boxes.append((
                QRectF(bx, mt, bar_w, ph + 45),
                {
                    'title': f"Прибор: {f['name']}",
                    'lines': [
                        f"Загрузка (Util): {round(val*100, 2)}%",
                        f"Входов (Entries): {f['entries']}",
                        f"Ср. время обслуж.: {f['avg_time']}",
                        f"Статус: {f['status']}"
                    ],
                    'line_no': f['line_no']
                }
            ))

    def _draw_queue_lengths(self, p, ml, mt, pw, ph, is_dark, text_primary, text_muted, grid_color):
        qs = self.parser.queues
        if not qs:
            p.drawText(QRectF(ml, mt, pw, ph), Qt.AlignCenter, "Нет данных об очередях")
            return

        max_val = max(1.0, max(float(q['max_c'] or 0) for q in qs))
        y_max = math.ceil(max_val * 1.25)

        for step_i in range(5):
            val = (y_max / 4) * step_i
            y = mt + ph - (val / y_max) * ph
            p.setPen(QPen(grid_color, 1, Qt.DashLine))
            p.drawLine(ml, y, ml + pw, y)
            p.setPen(text_muted)
            p.setFont(QFont("Segoe UI", 8))
            p.drawText(QRectF(ml - 55, y - 9, 48, 18), Qt.AlignRight | Qt.AlignVCenter, f"{val:.1f}")

        leg_x = ml + pw - 280
        p.fillRect(QRectF(leg_x, mt - 30, 12, 12), QColor("#388bfd" if is_dark else "#0969da"))
        p.setPen(text_primary)
        p.setFont(QFont("Segoe UI", 9))
        p.drawText(QRectF(leg_x + 18, mt - 32, 110, 16), Qt.AlignLeft | Qt.AlignVCenter, "Ср. длина")

        p.fillRect(QRectF(leg_x + 140, mt - 30, 12, 12), QColor("#f0883e" if is_dark else "#d47616"))
        p.drawText(QRectF(leg_x + 158, mt - 32, 120, 16), Qt.AlignLeft | Qt.AlignVCenter, "Макс. длина")

        n = len(qs)
        slot_w = pw / n
        single_bw = min(22.0, max(10.0, slot_w * 0.35))

        for i, q in enumerate(qs):
            avg_v = float(q['avg_c'] or 0)
            max_v = float(q['max_c'] or 0)

            center_x = ml + i * slot_w + slot_w / 2
            bx1 = center_x - single_bw - 2
            bx2 = center_x + 2

            bh1 = (avg_v / y_max) * ph
            bh2 = (max_v / y_max) * ph

            p.setBrush(QBrush(QColor("#388bfd" if is_dark else "#0969da")))
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(QRectF(bx1, mt + ph - bh1, single_bw, bh1), 3, 3)

            p.setBrush(QBrush(QColor("#f0883e" if is_dark else "#d47616")))
            p.drawRoundedRect(QRectF(bx2, mt + ph - bh2, single_bw, bh2), 3, 3)

            p.setPen(text_primary)
            p.setFont(QFont("Segoe UI", 8))
            p.drawText(QRectF(bx1 - 6, mt + ph - bh1 - 18, single_bw + 12, 16), Qt.AlignCenter, f"{avg_v:.1f}")
            p.drawText(QRectF(bx2 - 6, mt + ph - bh2 - 18, single_bw + 12, 16), Qt.AlignCenter, str(round(max_v)))

            p.setFont(QFont("Segoe UI", 9, QFont.Bold))
            p.drawText(QRectF(center_x - 30, mt + ph + 6, 60, 18), Qt.AlignCenter, q['name'])

            self.hit_boxes.append((
                QRectF(bx1 - 4, mt, single_bw * 2 + 12, ph + 30),
                {
                    'title': f"Очередь: {q['name']}",
                    'lines': [
                        f"Средняя длина: {q['avg_c']}",
                        f"Максимальная длина: {q['max_c']}",
                        f"Всего заявок: {q['total_e']}",
                        f"Ср. время ожидания: {q['avg_t']}",
                        f"Без ожидания: {q['pct_z']}%"
                    ],
                    'line_no': q['line_no']
                }
            ))

    def _draw_queue_wait_times(self, p, ml, mt, pw, ph, is_dark, text_primary, text_muted, grid_color):
        qs = self.parser.queues
        if not qs:
            return

        max_val = max(1.0, max(float(q['avg_t'] or 0) for q in qs))
        y_max = max_val * 1.2

        for step_i in range(5):
            val = (y_max / 4) * step_i
            y = mt + ph - (val / y_max) * ph
            p.setPen(QPen(grid_color, 1, Qt.DashLine))
            p.drawLine(ml, y, ml + pw, y)
            p.setPen(text_muted)
            p.setFont(QFont("Segoe UI", 8))
            p.drawText(QRectF(ml - 55, y - 9, 48, 18), Qt.AlignRight | Qt.AlignVCenter, f"{val:.1f}с")

        n = len(qs)
        slot_w = pw / n
        bar_w = min(46.0, max(18.0, slot_w * 0.6))

        for i, q in enumerate(qs):
            v = float(q['avg_t'] or 0)
            bx = ml + i * slot_w + (slot_w - bar_w) / 2
            bh = (v / y_max) * ph
            by = mt + ph - bh

            color = QColor("#d29922" if v > 10 else ("#388bfd" if is_dark else "#0969da"))
            p.setBrush(QBrush(color))
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(QRectF(bx, by, bar_w, bh), 4, 4)

            p.setPen(text_primary)
            p.setFont(QFont("Segoe UI", 9, QFont.Bold))
            p.drawText(QRectF(bx - 15, by - 20, bar_w + 30, 18), Qt.AlignCenter, f"{v:.1f}с")

            p.drawText(QRectF(bx - 15, mt + ph + 6, bar_w + 30, 18), Qt.AlignCenter, q['name'])

            self.hit_boxes.append((
                QRectF(bx, mt, bar_w, ph + 30),
                {
                    'title': f"Очередь: {q['name']}",
                    'lines': [
                        f"Ср. время ожидания: {q['avg_t']} тактов",
                        f"$Ср. время (ненулевые): {q['dollar_avg_t']}",
                        f"Всего входов: {q['total_e']}",
                        f"Нулевых входов: {q['zero_e']}"
                    ],
                    'line_no': q['line_no']
                }
            ))

    def _draw_queue_zeros(self, p, ml, mt, pw, ph, is_dark, text_primary, text_muted, grid_color):
        qs = self.parser.queues
        if not qs:
            return

        for step in (0.0, 0.25, 0.5, 0.75, 1.0):
            y = mt + ph - step * ph
            p.setPen(QPen(grid_color, 1, Qt.DashLine))
            p.drawLine(ml, y, ml + pw, y)
            p.setPen(text_muted)
            p.setFont(QFont("Segoe UI", 8))
            p.drawText(QRectF(ml - 55, y - 9, 48, 18), Qt.AlignRight | Qt.AlignVCenter, f"{round(step*100)}%")

        n = len(qs)
        slot_w = pw / n
        bar_w = min(46.0, max(18.0, slot_w * 0.6))

        for i, q in enumerate(qs):
            try:
                v = float(q['pct_z'] or 0)
            except Exception:
                v = 0.0

            bx = ml + i * slot_w + (slot_w - bar_w) / 2
            bh = (v / 100.0) * ph
            by = mt + ph - bh

            if v >= 70:
                color = QColor("#238636" if is_dark else "#1a7f37")
            elif v >= 30:
                color = QColor("#d29922" if is_dark else "#b78103")
            else:
                color = QColor("#da3633" if is_dark else "#cf222e")

            p.setBrush(QBrush(color))
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(QRectF(bx, by, bar_w, bh), 4, 4)

            p.setPen(text_primary)
            p.setFont(QFont("Segoe UI", 9, QFont.Bold))
            p.drawText(QRectF(bx - 15, by - 20, bar_w + 30, 18), Qt.AlignCenter, f"{round(v, 1)}%")

            p.drawText(QRectF(bx - 15, mt + ph + 6, bar_w + 30, 18), Qt.AlignCenter, q['name'])

            self.hit_boxes.append((
                QRectF(bx, mt, bar_w, ph + 30),
                {
                    'title': f"Очередь: {q['name']}",
                    'lines': [
                        f"Доля без ожидания: {q['pct_z']}%",
                        f"Нулевых заявок: {q['zero_e']}",
                        f"Всего заявок: {q['total_e']}"
                    ],
                    'line_no': q['line_no']
                }
            ))

    def _draw_node_composition(self, p, ml, mt, pw, ph, is_dark, text_primary, text_muted, grid_color):
        nodes = self.device_groups
        if not nodes:
            return

        max_val = max(1.0, max(n['total_node_val'] for n in nodes))
        y_max = max_val * 1.25

        for step_i in range(5):
            val = (y_max / 4) * step_i
            y = mt + ph - (val / y_max) * ph
            p.setPen(QPen(grid_color, 1, Qt.DashLine))
            p.drawLine(ml, y, ml + pw, y)
            p.setPen(text_muted)
            p.setFont(QFont("Segoe UI", 8))
            p.drawText(QRectF(ml - 55, y - 9, 48, 18), Qt.AlignRight | Qt.AlignVCenter, f"{val:.1f}с")

        leg_x = ml + pw - 340
        p.fillRect(QRectF(leg_x, mt - 30, 12, 12), QColor("#388bfd" if is_dark else "#0969da"))
        p.setPen(text_primary)
        p.setFont(QFont("Segoe UI", 9))
        p.drawText(QRectF(leg_x + 18, mt - 32, 140, 16), Qt.AlignLeft | Qt.AlignVCenter, "Время обслуж. (t_обсл)")

        p.fillRect(QRectF(leg_x + 175, mt - 30, 12, 12), QColor("#f0883e" if is_dark else "#d47616"))
        p.drawText(QRectF(leg_x + 193, mt - 32, 140, 16), Qt.AlignLeft | Qt.AlignVCenter, "Время в очер. (W_оч)")

        n = len(nodes)
        slot_w = pw / n
        bar_w = min(48.0, max(18.0, slot_w * 0.65))

        for i, nd in enumerate(nodes):
            t_s = nd['avg_serv_val']
            t_w = nd['q_avg_wait_val']
            t_tot = nd['total_node_val']

            bx = ml + i * slot_w + (slot_w - bar_w) / 2
            bh_s = (t_s / y_max) * ph
            bh_w = (t_w / y_max) * ph

            by_s = mt + ph - bh_s
            by_w = by_s - bh_w

            p.setBrush(QBrush(QColor("#388bfd" if is_dark else "#0969da")))
            p.setPen(Qt.NoPen)
            p.drawRect(QRectF(bx, by_s, bar_w, bh_s))

            p.setBrush(QBrush(QColor("#f0883e" if is_dark else "#d47616")))
            p.drawRoundedRect(QRectF(bx, by_w, bar_w, bh_w), 3, 3)

            p.setPen(text_primary)
            p.setFont(QFont("Segoe UI", 9, QFont.Bold))
            p.drawText(QRectF(bx - 20, by_w - 20, bar_w + 40, 18), Qt.AlignCenter, f"{t_tot:.1f}с")

            p.drawText(QRectF(bx - 20, mt + ph + 6, bar_w + 40, 18), Qt.AlignCenter, nd['device'])

            self.hit_boxes.append((
                QRectF(bx, mt, bar_w, ph + 30),
                {
                    'title': f"Узел: {nd['device']} + {nd['queue']}",
                    'lines': [
                        f"Общее время в узле: {t_tot:.3f} тактов",
                        f"Время обслуживания: {t_s:.3f} тактов",
                        f"Время ожидания: {t_w:.3f} тактов",
                        f"Загрузка прибора: {nd['util']}",
                        f"Ср. длина очереди: {nd['q_avg_len']}"
                    ],
                    'line_no': nd['line_no']
                }
            ))

    def _draw_block_executions(self, p, ml, mt, pw, ph, is_dark, text_primary, text_muted, grid_color):
        blks = self.parser.blocks
        if not blks:
            return

        max_val = max(1.0, max(float(b['total'] or 0) for b in blks))
        y_max = max_val * 1.2

        for step_i in range(5):
            val = (y_max / 4) * step_i
            y = mt + ph - (val / y_max) * ph
            p.setPen(QPen(grid_color, 1, Qt.DashLine))
            p.drawLine(ml, y, ml + pw, y)
            p.setPen(text_muted)
            p.setFont(QFont("Segoe UI", 8))
            p.drawText(QRectF(ml - 55, y - 9, 48, 18), Qt.AlignRight | Qt.AlignVCenter, str(round(val)))

        n = len(blks)
        slot_w = pw / n
        bar_w = max(4.0, slot_w - 2.0)

        for i, b in enumerate(blks):
            v = float(b['total'] or 0)
            bx = ml + i * slot_w
            bh = (v / y_max) * ph
            by = mt + ph - bh

            cur_cnt = int(b.get('current', '0') or '0')
            color = QColor("#ffa657" if cur_cnt > 0 else ("#79c0ff" if is_dark else "#0969da"))

            p.setBrush(QBrush(color))
            p.setPen(Qt.NoPen)
            p.drawRect(QRectF(bx, by, bar_w, bh))

            if n <= 25:
                p.setPen(text_primary)
                p.setFont(QFont("Segoe UI", 8))
                p.drawText(QRectF(bx - 10, mt + ph + 6, bar_w + 20, 16), Qt.AlignCenter, b['block'])

            self.hit_boxes.append((
                QRectF(bx, mt, bar_w, ph + 25),
                {
                    'title': f"Блок: {b['block']}",
                    'lines': [
                        f"Всего входов (Total): {b['total']}",
                        f"Транзактов сейчас (Current): {b['current']}"
                    ],
                    'line_no': b['line_no']
                }
            ))

    def _draw_storage_stats(self, p, ml, mt, pw, ph, is_dark, text_primary, text_muted, grid_color):
        stors = self.parser.storages
        if not stors:
            p.setPen(text_muted)
            p.setFont(QFont("Segoe UI", 12))
            p.drawText(QRectF(ml, mt, pw, ph), Qt.AlignCenter, "В модели отсутствуют многоканальные устройства (STORAGE)")
            return

        for step in (0.0, 0.25, 0.5, 0.75, 1.0):
            y = mt + ph - step * ph
            p.setPen(QPen(grid_color, 1, Qt.DashLine))
            p.drawLine(ml, y, ml + pw, y)
            p.setPen(text_muted)
            p.setFont(QFont("Segoe UI", 8))
            p.drawText(QRectF(ml - 55, y - 9, 48, 18), Qt.AlignRight | Qt.AlignVCenter, f"{round(step*100)}%")

        n = len(stors)
        slot_w = pw / n
        bar_w = min(56.0, max(20.0, slot_w * 0.6))

        for i, s in enumerate(stors):
            try:
                val = float(s['util'])
            except Exception:
                val = 0.0

            bx = ml + i * slot_w + (slot_w - bar_w) / 2
            bh = min(val, 1.0) * ph
            by = mt + ph - bh

            color = QColor("#8957e5" if is_dark else "#8250df")
            p.setBrush(QBrush(color))
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(QRectF(bx, by, bar_w, bh), 4, 4)

            p.setPen(text_primary)
            p.setFont(QFont("Segoe UI", 9, QFont.Bold))
            p.drawText(QRectF(bx - 15, by - 20, bar_w + 30, 18), Qt.AlignCenter, f"{round(val*100, 1)}%")

            p.drawText(QRectF(bx - 15, mt + ph + 6, bar_w + 30, 18), Qt.AlignCenter, s['name'])

            p.setFont(QFont("Segoe UI", 8))
            p.setPen(text_muted)
            p.drawText(QRectF(bx - 20, mt + ph + 24, bar_w + 40, 16), Qt.AlignCenter, f"Ёмкость: {s['capacity']}")

            self.hit_boxes.append((
                QRectF(bx, mt, bar_w, ph + 45),
                {
                    'title': f"Память: {s['name']}",
                    'lines': [
                        f"Загрузка (Util): {s['util']}",
                        f"Ёмкость (Capacity): {s['capacity']}",
                        f"Ср. заполнение: {s['avg_contents']}",
                        f"Макс. заполнение: {s['max_contents']}",
                        f"Входов: {s['entries']}"
                    ],
                    'line_no': s['line_no']
                }
            ))

    def _draw_tooltip(self, p, w, h, is_dark):
        item = self.hovered_item
        tw, th = 195, 24 + len(item.get('lines', [])) * 17 + 22
        tx = self.hover_pos.x() + 15
        ty = self.hover_pos.y() + 15

        if tx + tw > w - 10:
            tx = self.hover_pos.x() - tw - 15
        if ty + th > h - 10:
            ty = self.hover_pos.y() - th - 15

        t_rect = QRectF(tx, ty, tw, th)

        p.setBrush(QBrush(QColor("#1b1f20" if is_dark else "#ffffff")))
        p.setPen(QPen(QColor("#bcdfff" if is_dark else "#0969da"), 1.5))
        p.drawRoundedRect(t_rect, 6, 6)

        p.setFont(QFont("Segoe UI", 10, QFont.Bold))
        p.setPen(QColor("#bcdfff" if is_dark else "#0969da"))
        p.drawText(QRectF(tx + 10, ty + 6, tw - 20, 18), Qt.AlignLeft, item['title'])

        p.setFont(QFont("Segoe UI", 9))
        p.setPen(QColor("#e0e5e9" if is_dark else "#1f2328"))
        curr_y = ty + 26
        for line in item.get('lines', []):
            p.drawText(QRectF(tx + 10, curr_y, tw - 20, 16), Qt.AlignLeft, line)
            curr_y += 17

        p.setFont(QFont("Segoe UI", 8))
        p.setPen(QColor("#7a8c9e" if is_dark else "#57606a"))
        p.drawText(QRectF(tx + 10, curr_y + 2, tw - 20, 16), Qt.AlignLeft, "Ctrl + Клик: в листинг")
