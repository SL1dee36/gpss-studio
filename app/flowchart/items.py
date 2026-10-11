import math

from PySide6.QtCore import QRectF, Qt, QPointF
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QPainterPath, QFont, QPolygonF
from PySide6.QtWidgets import QGraphicsItem

from app.consts import BLOCK_COLORS_DARK, BLOCK_COLORS_LIGHT


class GPSSBlockGraphicsItem(QGraphicsItem):
    def __init__(self, block_data, width=210, height=66, theme="dark", show_stats=True, on_click=None):
        super().__init__()
        self.block_data = block_data
        self.w = width
        self.h = height
        self.theme = theme
        self.show_stats = show_stats
        self.on_click = on_click
        self.is_hovered = False
        self.setAcceptHoverEvents(True)
        self.setZValue(2)

    def boundingRect(self):
        return QRectF(0, 0, self.w, self.h)

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)
        is_dark = (self.theme == "dark")

        bg_color = QColor("#1b1f20") if is_dark else QColor("#ffffff")
        border_color = QColor("#bcdfff" if is_dark else "#0969da") if self.is_hovered else (QColor("#454e4f") if is_dark else QColor("#d0d7de"))
        text_primary = QColor("#e0e5e9") if is_dark else QColor("#1f2328")
        text_muted = QColor("#7a8c9e") if is_dark else QColor("#57606a")

        color_palette = BLOCK_COLORS_DARK if is_dark else BLOCK_COLORS_LIGHT
        op_color = color_palette.get(self.block_data['op'], color_palette['OTHER'])

        rect = QRectF(0, 0, self.w, self.h)
        painter.setBrush(QBrush(bg_color))
        pen_width = 2 if self.is_hovered else 1
        painter.setPen(QPen(border_color, pen_width))
        painter.drawRoundedRect(rect, 6, 6)

        # Category strip
        strip_rect = QRectF(0, 0, 6, self.h)
        strip_path = QPainterPath()
        strip_path.addRoundedRect(strip_rect, 6, 6)
        painter.fillPath(strip_path, QBrush(op_color))
        painter.fillRect(QRectF(3, 0, 3, self.h), QBrush(op_color))

        # Opcode
        painter.setFont(QFont("Segoe UI", 10, QFont.Bold))
        painter.setPen(op_color)
        painter.drawText(QRectF(12, 6, 120, 20), Qt.AlignLeft | Qt.AlignVCenter, self.block_data['op'])

        # Line number
        painter.setFont(QFont("Segoe UI", 9))
        painter.setPen(text_muted)
        line_str = f"L{self.block_data['line_no']}"
        painter.drawText(QRectF(self.w - 45, 6, 38, 20), Qt.AlignRight | Qt.AlignVCenter, line_str)

        # Label badge
        if self.block_data['label']:
            lbl_text = f"[{self.block_data['label']}]"
            painter.setFont(QFont("Consolas", 9, QFont.Bold))
            painter.setPen(QColor("#7ee787" if is_dark else "#1a7f37"))
            painter.drawText(QRectF(self.w - 115, 6, 68, 20), Qt.AlignRight | Qt.AlignVCenter, lbl_text)

        # Operands
        operands = self.block_data.get('operands', '')
        if operands:
            painter.setFont(QFont("Consolas", 10))
            painter.setPen(text_primary)
            painter.drawText(QRectF(12, 26, self.w - 24, 18), Qt.AlignLeft | Qt.AlignVCenter, operands)

        # Statistics / Comment
        if self.show_stats and (self.block_data.get('total') != '0' or self.block_data.get('current') != '0'):
            tot_str = f"Входов: {self.block_data.get('total', '0')}"
            cur_val = int(self.block_data.get('current', '0') or '0')

            painter.setFont(QFont("Segoe UI", 8))
            painter.setPen(text_muted)
            painter.drawText(QRectF(12, 45, 95, 16), Qt.AlignLeft | Qt.AlignVCenter, tot_str)

            if cur_val > 0:
                cur_str = f"Занято: {cur_val}"
                painter.setFont(QFont("Segoe UI", 8, QFont.Bold))
                painter.setPen(QColor("#ffa657" if is_dark else "#b78103"))
                painter.drawText(QRectF(self.w - 95, 45, 85, 16), Qt.AlignRight | Qt.AlignVCenter, cur_str)
        elif self.block_data.get('comment'):
            painter.setFont(QFont("Segoe UI", 8))
            painter.setPen(text_muted)
            painter.drawText(QRectF(12, 45, self.w - 24, 16), Qt.AlignLeft | Qt.AlignVCenter, self.block_data['comment'])

    def hoverEnterEvent(self, event):
        self.is_hovered = True
        self.update()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.is_hovered = False
        self.update()
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.on_click:
            self.on_click(self.block_data['line_no'])
        super().mousePressEvent(event)


class GPSSEdgeGraphicsItem(QGraphicsItem):
    def __init__(self, points, edge_type="seq", label="", theme="dark"):
        super().__init__()
        self.points = points
        self.edge_type = edge_type
        self.label = label
        self.theme = theme
        self.setZValue(1)

    def boundingRect(self):
        if not self.points:
            return QRectF()
        xs = [p.x() for p in self.points]
        ys = [p.y() for p in self.points]
        m = 45
        return QRectF(min(xs) - m, min(ys) - m, max(xs) - min(xs) + m * 2, max(ys) - min(ys) + m * 2)

    def paint(self, painter, option, widget=None):
        if len(self.points) < 2:
            return

        painter.setRenderHint(QPainter.Antialiasing)
        is_dark = (self.theme == "dark")

        if self.edge_type in ("jump", "prob", "both"):
            line_color = QColor("#bcdfff" if is_dark else "#0969da")
            pen_style = Qt.SolidLine
        elif self.edge_type == "branch":
            line_color = QColor("#f0883e" if is_dark else "#d47616")
            pen_style = Qt.DashLine
        else:
            line_color = QColor("#7a8c9e" if is_dark else "#8c959f")
            pen_style = Qt.SolidLine

        pen = QPen(line_color, 1.5, pen_style)
        painter.setPen(pen)

        path = QPainterPath()
        path.moveTo(self.points[0])

        radius = 8.0
        for i in range(1, len(self.points) - 1):
            p_prev = self.points[i - 1]
            p_curr = self.points[i]
            p_next = self.points[i + 1]

            v1 = p_curr - p_prev
            len1 = math.hypot(v1.x(), v1.y())
            v2 = p_next - p_curr
            len2 = math.hypot(v2.x(), v2.y())

            r = min(radius, len1 / 2.0, len2 / 2.0)
            if r > 0.1 and len1 > 0 and len2 > 0:
                p_start = p_curr - (v1 / len1) * r
                p_end = p_curr + (v2 / len2) * r
                path.lineTo(p_start)
                path.quadTo(p_curr, p_end)
            else:
                path.lineTo(p_curr)

        path.lineTo(self.points[-1])
        painter.drawPath(path)

        # Стрелочный наконечник
        p_last = self.points[-1]
        p_pre = self.points[-2]
        angle = math.atan2(p_last.y() - p_pre.y(), p_last.x() - p_pre.x())

        arrow_size = 7
        p1 = p_last
        p2 = p_last - QPointF(arrow_size * math.cos(angle - math.pi / 6), arrow_size * math.sin(angle - math.pi / 6))
        p3 = p_last - QPointF(arrow_size * math.cos(angle + math.pi / 6), arrow_size * math.sin(angle + math.pi / 6))

        painter.setBrush(QBrush(line_color))
        painter.drawPolygon(QPolygonF([p1, p2, p3]))

        # Отрисовка бейджа без наложения на стрелку
        if self.label:
            badge_text = self.label
            painter.setFont(QFont("Segoe UI", 8, QFont.Bold))
            badge_bg = QColor("#1f2426" if is_dark else "#f6f8fa")
            badge_w = 40
            badge_h = 16

            is_purely_vertical = (len(self.points) == 2 and abs(self.points[0].x() - self.points[1].x()) < 1.0)
            mid_pt = path.pointAtPercent(0.5)

            if is_purely_vertical:
                # Смещаем вправо от вертикальной оси — линия и наконечник остаются полностью видимыми
                bx = mid_pt.x() + 8
                by = mid_pt.y() - badge_h / 2
            else:
                bx = mid_pt.x() - badge_w / 2
                by = mid_pt.y() - badge_h - 4

            badge_rect = QRectF(bx, by, badge_w, badge_h)
            painter.setBrush(QBrush(badge_bg))
            painter.setPen(QPen(line_color, 1))
            painter.drawRoundedRect(badge_rect, 4, 4)
            painter.setPen(line_color)
            painter.drawText(badge_rect, Qt.AlignCenter, badge_text)
