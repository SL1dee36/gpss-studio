from PySide6.QtCore import Signal, Qt, QPointF, QRectF
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QFont, QImage, QPixmap
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem, QApplication, \
    QFileDialog

from app.flowchart.items import GPSSBlockGraphicsItem, GPSSEdgeGraphicsItem
from app.parsing.flowchart import GPSSFlowchartParser


class GPSSFlowchartView(QGraphicsView):
    blockClicked = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.theme = "dark"
        self.layout_mode = "lanes"
        self.show_stats = True
        self.code_text = ""
        self.listing_stats = {}
        self.current_zoom = 1.0

    def set_theme(self, theme):
        self.theme = theme
        bg = QColor("#121718" if theme == "dark" else "#f6f8fa")
        self.setBackgroundBrush(QBrush(bg))
        self.rebuild_flowchart()

    def wheelEvent(self, event):
        factor = 1.15 if event.angleDelta().y() > 0 else (1.0 / 1.15)
        new_zoom = self.current_zoom * factor
        if 0.2 <= new_zoom <= 4.0:
            self.current_zoom = new_zoom
            self.scale(factor, factor)

    def zoom_in(self):
        self.current_zoom *= 1.2
        self.scale(1.2, 1.2)

    def zoom_out(self):
        self.current_zoom /= 1.2
        self.scale(1.0 / 1.2, 1.0 / 1.2)

    def zoom_reset(self):
        self.resetTransform()
        self.current_zoom = 1.0

    def zoom_fit(self):
        self.zoom_reset()
        rect = self.scene.itemsBoundingRect()
        if not rect.isEmpty():
            self.fitInView(rect.adjusted(-20, -20, 20, 20), Qt.KeepAspectRatio)

    def update_model(self, code_text, listing_stats=None):
        self.code_text = code_text
        if listing_stats is not None:
            if hasattr(listing_stats, 'blocks'):
                stats = {}
                for b in listing_stats.blocks:
                    blk = b['block']
                    cur = b['current']
                    tot = b['total']
                    if blk.isdigit():
                        stats[int(blk)] = {'current': cur, 'total': tot}
                    else:
                        stats[blk.upper()] = {'current': cur, 'total': tot}
                self.listing_stats = stats
            elif isinstance(listing_stats, dict):
                self.listing_stats = listing_stats
        self.rebuild_flowchart()

    def rebuild_flowchart(self):
        self.scene.clear()
        if not self.code_text.strip():
            return

        blocks, edges, segments, labels = GPSSFlowchartParser.parse(self.code_text)
        if not blocks:
            return

        for b in blocks:
            lbl = b['label'].upper() if b['label'] else ''
            b_num = b['block_num']
            stat = self.listing_stats.get(lbl) or self.listing_stats.get(b_num)
            if stat:
                b['total'] = stat.get('total', '0')
                b['current'] = stat.get('current', '0')

        block_w = 210
        block_h = 66
        v_gap = 38   # Увеличен зазор, чтобы стрелки и бейджи не слипались
        h_gap = 75   # Достаточно места для двухсторонних коридоров между колонками

        block_items = {}
        block_positions = {}

        if self.layout_mode == "lanes":
            num_segs = len(segments)
            cols = num_segs  # Каждому логическому потоку — своя отдельная колонка
            col_x_offsets = []
            cur_x = 35
            for c in range(cols):
                col_x_offsets.append(cur_x)
                cur_x += block_w + h_gap

            for s_idx, seg in enumerate(segments):
                bx = col_x_offsets[s_idx]
                by = 40

                title_item = QGraphicsRectItem(bx, by, block_w, 24)
                is_dark = (self.theme == "dark")
                title_item.setBrush(QBrush(QColor("#1f2426" if is_dark else "#eef3f8")))
                title_item.setPen(QPen(QColor("#454e4f" if is_dark else "#d0d7de"), 1))
                self.scene.addItem(title_item)

                txt_item = QGraphicsTextItem(seg['title'], title_item)
                txt_item.setFont(QFont("Segoe UI", 9, QFont.Bold))
                txt_item.setDefaultTextColor(QColor("#bcdfff" if is_dark else "#0969da"))
                txt_item.setPos(bx + 6, by + 1)

                by += 34

                for b_idx in seg['block_indices']:
                    b = blocks[b_idx]
                    item = GPSSBlockGraphicsItem(
                        b, width=block_w, height=block_h, theme=self.theme,
                        show_stats=self.show_stats, on_click=self.blockClicked.emit
                    )
                    item.setPos(bx, by)
                    self.scene.addItem(item)
                    block_items[b_idx] = item
                    block_positions[b_idx] = (bx, by, s_idx)
                    by += block_h + v_gap
        else:
            bx = 100
            by = 40
            for b_idx, b in enumerate(blocks):
                item = GPSSBlockGraphicsItem(
                    b, width=block_w, height=block_h, theme=self.theme,
                    show_stats=self.show_stats, on_click=self.blockClicked.emit
                )
                item.setPos(bx, by)
                self.scene.addItem(item)
                block_items[b_idx] = item
                block_positions[b_idx] = (bx, by, 0)
                by += block_h + v_gap

        # Построение маршрутов стрелок
        for e in edges:
            u, v = e['from'], e['to']
            if u not in block_positions or v not in block_positions:
                continue

            ux, uy, uc = block_positions[u]
            vx, vy, vc = block_positions[v]

            pts = []

            # 1. Прямой шаг вниз к следующему блоку в той же колонке
            if uc == vc and v == u + 1 and vy > uy:
                pts = [
                    QPointF(ux + block_w / 2, uy + block_h),
                    QPointF(vx + block_w / 2, vy)
                ]

            # 2. Обратный цикл вверх в той же колонке (например, TRANSFER ,MET1 или ,MET2)
            elif uc == vc and vy <= uy:
                # Огибаем слева по выделенному коридору и входим строго в левую грань блока (не трогая заголовок)
                x_corridor = ux - 22
                pts = [
                    QPointF(ux, uy + block_h / 2),
                    QPointF(x_corridor, uy + block_h / 2),
                    QPointF(x_corridor, vy + block_h / 2),
                    QPointF(vx, vy + block_h / 2)
                ]

            # 3. Прыжок вперед через блоки в той же колонке
            elif uc == vc and v > u + 1:
                x_corridor = ux + block_w + 22
                pts = [
                    QPointF(ux + block_w, uy + block_h / 2),
                    QPointF(x_corridor, uy + block_h / 2),
                    QPointF(x_corridor, vy + block_h / 2),
                    QPointF(vx + block_w, vy + block_h / 2)
                ]

            # 4. Переход в правую колонку (например, ветка 5% в подпрограмму JUMP)
            elif uc < vc:
                # Выходим справа, идем по межколоночному коридору и входим в левую грань целевого блока
                x_channel = (ux + block_w + vx) / 2
                pts = [
                    QPointF(ux + block_w, uy + block_h / 2),
                    QPointF(x_channel, uy + block_h / 2),
                    QPointF(x_channel, vy + block_h / 2),
                    QPointF(vx, vy + block_h / 2)
                ]

            # 5. Возврат из правой колонки в левую (например, возврат из JUMP в MET2)
            else:
                # Выходим слева, идем по коридору со смещением и входим в правую грань блока MET2
                x_channel = (vx + block_w + ux) / 2
                pts = [
                    QPointF(ux, uy + block_h / 2),
                    QPointF(x_channel, uy + block_h / 2),
                    QPointF(x_channel, vy + block_h / 2),
                    QPointF(vx + block_w, vy + block_h / 2)
                ]

            edge_item = GPSSEdgeGraphicsItem(
                pts, edge_type=e['type'],
                label=e['label'], theme=self.theme
            )
            self.scene.addItem(edge_item)

        self.scene.setSceneRect(self.scene.itemsBoundingRect().adjusted(-50, -50, 50, 50))

    def copy_to_clipboard(self):
        pixmap = self.render_to_pixmap()
        if pixmap:
            QApplication.clipboard().setPixmap(pixmap)
            return True
        return False

    def export_png(self, parent):
        path, _ = QFileDialog.getSaveFileName(
            parent, "Экспорт блок-схемы в PNG", "", "Изображение PNG (*.png)"
        )
        if not path:
            return False
        pixmap = self.render_to_pixmap()
        if pixmap:
            return pixmap.save(path, "PNG")
        return False

    def render_to_pixmap(self):
        rect = self.scene.itemsBoundingRect().adjusted(-30, -30, 30, 30)
        if rect.isEmpty():
            return None
        img = QImage(int(rect.width()), int(rect.height()), QImage.Format_ARGB32)
        img.fill(QColor("#121718" if self.theme == "dark" else "#f6f8fa"))
        p = QPainter(img)
        p.setRenderHint(QPainter.Antialiasing)
        self.scene.render(p, QRectF(0, 0, rect.width(), rect.height()), rect)
        p.end()
        return QPixmap.fromImage(img)
