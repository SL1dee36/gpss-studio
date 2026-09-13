import os
import re
import sys
import subprocess
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QPlainTextEdit, QLabel, QSplitter, QMessageBox,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QSizePolicy, QLineEdit
)
from PySide6.QtGui import (
    QFont, QFontMetrics, QKeySequence, QShortcut, QColor, 
    QPainter, QPen, QTextCursor, QTextBlockUserData
)
from PySide6.QtCore import Qt, QRect

CODE_VAR_16 = """GENERATE 13,3
QUEUE AAA
SEIZE MEM
DEPART AAA
ADVANCE 18
RELEASE MEM
TERMINATE 1
START 20
END"""

STYLE_SHEET = """
QMainWindow {
    background-color: #181825;
}
QWidget {
    color: #cdd6f4;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 13px;
}
QFrame#top_panel {
    background-color: #1e1e2e;
    border: 1px solid #313244;
    border-radius: 8px;
    padding: 4px 8px;
}
QPlainTextEdit {
    background-color: #11111b;
    color: #cdd6f4;
    border: 1px solid #313244;
    border-radius: 6px;
    selection-background-color: #45475a;
}
QPushButton {
    font-weight: bold;
    border-radius: 6px;
    padding: 6px 14px;
    border: none;
}
QPushButton#btn_run {
    background-color: #a6e3a1;
    color: #11111b;
}
QPushButton#btn_run:hover {
    background-color: #94e2d5;
}
QPushButton#btn_reset {
    background-color: #313244;
    color: #cdd6f4;
}
QPushButton#btn_reset:hover {
    background-color: #45475a;
}
QTabWidget::pane {
    border: 1px solid #313244;
    border-radius: 6px;
    background-color: #11111b;
}
QTabBar::tab {
    background-color: #181825;
    color: #a6adc8;
    padding: 8px 16px;
    margin-right: 4px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}
QTabBar::tab:selected {
    background-color: #313244;
    color: #cdd6f4;
    font-weight: bold;
}
QTableWidget {
    background-color: #11111b;
    gridline-color: #313244;
    border: none;
}
QHeaderView::section {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-weight: bold;
    border: 1px solid #313244;
    padding: 6px;
}
"""


class BlockUserData(QTextBlockUserData):
    def __init__(self, label=""):
        super().__init__()
        self.label = label


class LabelGutter(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
        self.inline_edit = QLineEdit(self)
        self.inline_edit.setMaxLength(4)
        self.inline_edit.hide()
        self.inline_edit.setStyleSheet(
            "background-color: #181825; color: #f9e2af; border: 1px solid #89b4fa; "
            "font-family: Consolas; font-size: 11px; padding: 0px 2px;"
        )
        self.inline_edit.returnPressed.connect(self._finish_edit)
        self.inline_edit.editingFinished.connect(self._finish_edit)
        self.editing_block = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(event.rect(), QColor("#161622"))

        font = self.editor.font()
        painter.setFont(font)
        fm = QFontMetrics(font)

        block = self.editor.firstVisibleBlock()
        block_num = block.blockNumber()
        top = int(self.editor.blockBoundingGeometry(block).translated(self.editor.contentOffset()).top())
        bottom = top + int(self.editor.blockBoundingRect(block).height())

        pen_empty = QColor("#585b70")
        pen_filled = QColor("#f9e2af")

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                ud = block.userData()
                lbl = ud.label if (ud and hasattr(ud, "label") and ud.label) else ""

                if lbl:
                    painter.setPen(pen_filled)
                    painter.drawText(4, top, self.width() - 8, fm.height(), Qt.AlignCenter, lbl)
                else:
                    painter.setPen(pen_empty)
                    painter.drawText(4, top, self.width() - 8, fm.height(), Qt.AlignCenter, "_ _")

            block = block.next()
            top = bottom
            bottom = top + int(self.editor.blockBoundingRect(block).height())
            block_num += 1

        painter.setPen(QPen(QColor("#45475a"), 1))
        painter.drawLine(self.width() - 1, event.rect().top(), self.width() - 1, event.rect().bottom())

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

    def _start_edit(self, block, y, h):
        self.editing_block = block
        ud = block.userData()
        val = ud.label if (ud and hasattr(ud, "label")) else ""
        self.inline_edit.setText(val)
        self.inline_edit.setGeometry(2, int(y) + 1, self.width() - 4, int(h) - 2)
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
        self.inline_edit.hide()
        self.editing_block = None
        self.update()


class GPSSCodeEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.gutter = LabelGutter(self)

        self.blockCountChanged.connect(self.update_gutter_width)
        self.updateRequest.connect(self.update_gutter)
        self.update_gutter_width(0)

    def gutter_width(self):
        return self.fontMetrics().horizontalAdvance("W") * 3 + 14

    def update_gutter_width(self, _):
        self.setViewportMargins(self.gutter_width(), 0, 0, 0)

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

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Tab:
            self.insertPlainText("  ")
        else:
            super().keyPressEvent(event)


class GPSSStudio(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GPSS/H Studio")
        self.resize(1180, 720)
        self.setStyleSheet(STYLE_SHEET)

        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.exe_path = os.path.join(self.current_dir, "gpssh.exe")
        self.gps_file = os.path.join(self.current_dir, "model.gps")
        self.lis_file = os.path.join(self.current_dir, "model.lis")

        self._build_ui()
        QShortcut(QKeySequence("F5"), self, self.run_simulation)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(12, 12, 12, 12)
        root_layout.setSpacing(10)

        top_panel = QFrame()
        top_panel.setObjectName("top_panel")
        top_panel.setFixedHeight(46)
        top_layout = QHBoxLayout(top_panel)
        top_layout.setContentsMargins(6, 4, 6, 4)

        self.btn_run = QPushButton("▶ Запустить (F5)")
        self.btn_run.setObjectName("btn_run")
        self.btn_run.setFixedHeight(32)
        self.btn_run.clicked.connect(self.run_simulation)

        btn_reset = QPushButton("Сбросить")
        btn_reset.setObjectName("btn_reset")
        btn_reset.setFixedHeight(32)
        btn_reset.clicked.connect(lambda: self.editor.setPlainText(CODE_VAR_16))

        self.lbl_status = QLabel(f"Рабочая папка: {self.current_dir}")
        self.lbl_status.setStyleSheet("color: #6c7086; margin-left: 10px; font-size: 11px;")

        top_layout.addWidget(self.btn_run)
        top_layout.addWidget(btn_reset)
        top_layout.addWidget(self.lbl_status)
        top_layout.addStretch()

        root_layout.addWidget(top_panel)

        splitter = QSplitter(Qt.Horizontal)
        mono_font = QFont("Consolas", 11)
        mono_font.setStyleHint(QFont.Monospace)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)

        lbl_header = QLabel("<b>Метка (1-2) │ Код модели GPSS (начиная с 3-й позиции)</b>")
        lbl_header.setStyleSheet("color: #a6adc8; font-size: 12px;")
        left_layout.addWidget(lbl_header)

        self.editor = GPSSCodeEditor()
        self.editor.setFont(mono_font)
        self.editor.setTabStopDistance(QFontMetrics(mono_font).horizontalAdvance(' ') * 8)
        self.editor.setPlainText(CODE_VAR_16)
        left_layout.addWidget(self.editor)
        splitter.addWidget(left_widget)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(6)

        self.tabs = QTabWidget()

        self.summary_table = QTableWidget()
        self.summary_table.setColumnCount(3)
        self.summary_table.setHorizontalHeaderLabels(["Параметр", "Значение", "Пояснение"])
        self.summary_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.summary_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.summary_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tabs.addTab(self.summary_table, "📊 Сводка для отчёта")

        self.lis_viewer = QPlainTextEdit()
        self.lis_viewer.setFont(mono_font)
        self.lis_viewer.setReadOnly(True)
        self.lis_viewer.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.tabs.addTab(self.lis_viewer, "📄 Полный листинг (.lis)")

        self.console_viewer = QPlainTextEdit()
        self.console_viewer.setFont(mono_font)
        self.console_viewer.setReadOnly(True)
        self.tabs.addTab(self.console_viewer, "💻 Вывод консоли")

        right_layout.addWidget(self.tabs)
        splitter.addWidget(right_widget)

        splitter.setSizes([500, 660])
        root_layout.addWidget(splitter, 1)

    def run_simulation(self):
        if not os.path.exists(self.exe_path):
            QMessageBox.critical(
                self, "Ошибка",
                f"Файл gpssh.exe не найден!\n\nПоместите скрипт в папку с gpssh.exe:\n{self.current_dir}"
            )
            return

        full_code_lines = []
        block = self.editor.document().firstBlock()
        while block.isValid():
            line_text = block.text().replace("\xa0", " ").lstrip(" \t")
            ud = block.userData()
            label = ud.label.strip() if (ud and hasattr(ud, "label")) else ""

            if not line_text and not label:
                block = block.next()
                continue

            if label:
                if label.startswith("*"):
                    full_code_lines.append(f"{label} {line_text}")
                else:
                    full_code_lines.append(f"{label:<2} {line_text}")
            else:
                full_code_lines.append(f"  {line_text}")

            block = block.next()

        code = "\n".join(full_code_lines).rstrip() + "\r\n"

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
            process = subprocess.run(
                [self.exe_path, "model.gps"],
                input="model.gps\n",
                cwd=self.current_dir,
                capture_output=True,
                text=True,
                timeout=5
            )
        except subprocess.TimeoutExpired:
            QMessageBox.warning(self, "Таймаут", "Процесс GPSS завис. Проверьте условия завершения модели.")
            return
        except Exception as e:
            QMessageBox.critical(self, "Ошибка запуска", f"Сбой при запуске gpssh.exe:\n{e}")
            return

        self.console_viewer.setPlainText(f"STDOUT:\n{process.stdout}\n\nSTDERR:\n{process.stderr}")

        if not os.path.exists(self.lis_file):
            self.tabs.setCurrentIndex(2)
            self.lis_viewer.setPlainText("Файл model.lis не был создан. Проверьте вкладку консоли.")
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

    def _parse_and_fill_summary(self, text):
        data = []

        clock_match = re.search(r"Absolute Clock:\s*([\d\.]+)", text, re.IGNORECASE)
        clock = clock_match.group(1) if clock_match else "Н/Д"
        data.append(("Время моделирования (Absolute Clock)", clock, "Общая длительность работы системы в тактах"))

        mem_match = re.search(r"MEM\s+([\d\.]+)\s+(\d+)\s+([\d\.]+)", text)
        if mem_match:
            util, entries, avg_time = mem_match.groups()
            data.append(("Обработано заявок ОП (Entries)", entries, "Количество заявок, обслуженных памятью"))
            data.append(("Коэффициент загрузки ОП (Avg-Util)", util, "Доля времени занятости памяти (от 0 до 1)"))
            data.append(("Среднее время обработки (Avg Time/Xact)", avg_time, "Время обработки одного запроса памятью (такты)"))

        q_match = re.search(r"AAA\s+(\d+)\s+([\d\.]+)\s+(\d+)\s+\d+\s+[\d\.]+\s+([\d\.]+)", text)
        if q_match:
            q_max, q_avg, q_total, q_time = q_match.groups()
            data.append(("Всего заявок в очереди (Total Entries)", q_total, "Сколько всего заявок поступило от процессора"))
            data.append(("Макс. длина очереди (Maximum Contents)", q_max, "Пиковое число заявок, ожидавших в очереди"))
            data.append(("Средняя длина очереди (Average Contents)", q_avg, "Среднее количество ожидающих запросов"))
            data.append(("Среднее время ожидания (Average Time/Unit)", q_time, "Среднее время нахождения запроса в очереди (такты)"))

        self.summary_table.setRowCount(len(data))
        for row, (param, val, desc) in enumerate(data):
            it_param = QTableWidgetItem(param)
            it_val = QTableWidgetItem(val)
            it_val.setTextAlignment(Qt.AlignCenter)
            it_val.setForeground(QColor("#a6e3a1"))
            it_desc = QTableWidgetItem(desc)

            self.summary_table.setItem(row, 0, it_param)
            self.summary_table.setItem(row, 1, it_val)
            self.summary_table.setItem(row, 2, it_desc)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GPSSStudio()
    window.show()
    sys.exit(app.exec())