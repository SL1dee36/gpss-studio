from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QVBoxLayout, QPushButton


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
        add_item("Шаблоны моделей...", self.main_window.open_templates)
        add_item("Открыть...  (Ctrl+O)", self.main_window.open_file)
        add_item("Сохранить  (Ctrl+S)", self.main_window.save_file)
        add_item("Сохранить как...  (Ctrl+Shift+S)", self.main_window.save_file_as)

        sep = QFrame()
        sep.setObjectName("popup_separator")
        sep.setFixedHeight(1)
        layout.addWidget(sep)

        add_item("Экспорт отчёта (HTML / PDF)...", self.main_window.export_report)
        add_item("Рабочая папка (.gps / .lis)", self.main_window.open_work_directory)
        add_item("Настройки...", self.main_window.open_settings)

    def show_under(self, widget):
        pos = widget.mapToGlobal(widget.rect().bottomLeft())
        x = pos.x() - (self.width() - widget.width())
        y = pos.y() + 4
        self.move(x, y)
        self.show()
