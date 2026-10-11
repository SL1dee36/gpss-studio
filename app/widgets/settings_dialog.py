import os
import shutil

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QComboBox, QHBoxLayout, QLineEdit, QPushButton, \
    QCheckBox, QFileDialog

from root import get_app_dir


class SettingsDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки")
        self.resize(540, 310)
        self.config = dict(config)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.combo_os = QComboBox()
        self.combo_os.addItems(["Windows", "Linux"])
        if self.config.get("target_os", "windows").lower() == "linux":
            self.combo_os.setCurrentIndex(1)
        else:
            self.combo_os.setCurrentIndex(0)
        self.combo_os.currentIndexChanged.connect(self._on_os_changed)
        form.addRow("Операционная система:", self.combo_os)

        box_exe = QHBoxLayout()
        box_exe.setSpacing(6)
        self.edit_exe = QLineEdit(self.config.get("executable_path", ""))
        btn_browse_exe = QPushButton("Обзор...")
        btn_browse_exe.clicked.connect(self._browse_exe)
        box_exe.addWidget(self.edit_exe, 1)
        box_exe.addWidget(btn_browse_exe)
        form.addRow("Исполняемый файл GPSS:", box_exe)

        box_dir = QHBoxLayout()
        box_dir.setSpacing(6)
        self.edit_work_dir = QLineEdit(self.config.get("work_dir", ""))
        btn_browse_dir = QPushButton("Обзор...")
        btn_browse_dir.clicked.connect(self._browse_work_dir)
        btn_open_dir = QPushButton("Открыть")
        btn_open_dir.clicked.connect(self._open_folder)
        box_dir.addWidget(self.edit_work_dir, 1)
        box_dir.addWidget(btn_browse_dir)
        box_dir.addWidget(btn_open_dir)
        form.addRow("Рабочая папка:", box_dir)

        self.combo_theme = QComboBox()
        self.combo_theme.addItems(["Тёмная", "Светлая"])
        if self.config.get("theme", "dark") == "light":
            self.combo_theme.setCurrentIndex(1)
        else:
            self.combo_theme.setCurrentIndex(0)
        form.addRow("Тема оформления:", self.combo_theme)

        self.combo_zoom = QComboBox()
        self.combo_zoom.addItems(["75%", "80%", "90%", "100%", "110%", "125%", "150%", "175%", "200%"])
        cur_zoom = f"{self.config.get('zoom', 100)}%"
        idx = self.combo_zoom.findText(cur_zoom)
        if idx >= 0:
            self.combo_zoom.setCurrentIndex(idx)
        else:
            self.combo_zoom.setEditText(cur_zoom)
        form.addRow("Масштаб интерфейса (UI):", self.combo_zoom)

        self.chk_lines = QCheckBox("Показывать номера строк в редакторе")
        self.chk_lines.setChecked(self.config.get("show_line_numbers", False))
        form.addRow("Нумерация строк:", self.chk_lines)

        layout.addLayout(form)
        layout.addStretch()

        btns_layout = QHBoxLayout()
        btns_layout.addStretch()
        btn_cancel = QPushButton("Отмена")
        btn_cancel.clicked.connect(self.reject)
        btn_save = QPushButton("Сохранить")
        btn_save.setObjectName("btn_save")
        btn_save.clicked.connect(self._save)
        btns_layout.addWidget(btn_cancel)
        btns_layout.addWidget(btn_save)

        layout.addLayout(btns_layout)

    def _on_os_changed(self, _):
        chosen_os = self.combo_os.currentText().lower()
        cur_path = self.edit_exe.text().strip()
        dirname, basename = os.path.split(cur_path)
        if basename in ("gpssh.exe", "gpssh", ""):
            new_name = "gpssh.exe" if chosen_os == "windows" else "gpssh"
            candidate = os.path.join(dirname or self.config.get("work_dir", ""), new_name)
            if not os.path.exists(candidate):
                which_p = shutil.which(new_name)
                if which_p:
                    candidate = which_p
            self.edit_exe.setText(candidate)

    def _browse_exe(self):
        cur_os = self.combo_os.currentText().lower()
        start_dir = os.path.dirname(self.edit_exe.text().strip()) or self.config.get("work_dir", "")
        if cur_os == "windows":
            filter_str = "Исполняемые файлы (*.exe);;Все файлы (*.*)"
        else:
            filter_str = "Исполняемые файлы (gpssh * *.exe);;Все файлы (*.*)"
        path, _ = QFileDialog.getOpenFileName(self, "Выбор исполняемого файла GPSS", start_dir, filter_str)
        if path:
            self.edit_exe.setText(os.path.normpath(path))

    def _browse_work_dir(self):
        start_dir = self.edit_work_dir.text().strip() or os.getcwd()
        path = QFileDialog.getExistingDirectory(self, "Выбор рабочей папки", start_dir)
        if path:
            self.edit_work_dir.setText(os.path.normpath(path))

    def _open_folder(self):
        folder = self.edit_work_dir.text().strip()
        if not os.path.isdir(folder):
            folder = get_app_dir()
        QDesktopServices.openUrl(QUrl.fromLocalFile(folder))

    def _save(self):
        self.config["target_os"] = self.combo_os.currentText().lower()
        self.config["executable_path"] = self.edit_exe.text().strip()
        self.config["work_dir"] = self.edit_work_dir.text().strip()
        self.config["theme"] = "dark" if self.combo_theme.currentIndex() == 0 else "light"
        self.config["show_line_numbers"] = self.chk_lines.isChecked()
        try:
            zoom_str = self.combo_zoom.currentText().replace("%", "").strip()
            self.config["zoom"] = int(zoom_str)
        except Exception:
            self.config["zoom"] = 100
        self.accept()
