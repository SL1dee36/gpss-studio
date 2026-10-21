import os
import shutil

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QComboBox, QHBoxLayout,
    QLineEdit, QPushButton, QCheckBox, QFileDialog, QGroupBox
)

from root import get_app_dir


class SettingsDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки")
        self.resize(650, 520)
        self.config = dict(config)

        self.setMinimumWidth(650)
        self.setMinimumHeight(480)

        self._build_ui()

        # Устанавливаем начальное состояние видимости полей
        self._on_mode_changed(self.combo_mode.currentIndex())

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        # ==================================================================
        # ГРУППА 1: Общие настройки IDE
        # ==================================================================
        group_common = QGroupBox("Общие настройки IDE")
        layout_common = QFormLayout(group_common)
        layout_common.setSpacing(10)
        layout_common.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

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
        layout_common.addRow("Рабочая папка:", box_dir)

        self.combo_theme = QComboBox()
        self.combo_theme.addItems(["Тёмная", "Светлая"])
        if self.config.get("theme", "dark") == "light":
            self.combo_theme.setCurrentIndex(1)
        layout_common.addRow("Тема оформления:", self.combo_theme)

        self.combo_zoom = QComboBox()
        self.combo_zoom.addItems(["75%", "80%", "90%", "100%", "110%", "125%", "150%", "175%", "200%"])
        cur_zoom = f"{self.config.get('zoom', 100)}%"
        idx = self.combo_zoom.findText(cur_zoom)
        if idx >= 0:
            self.combo_zoom.setCurrentIndex(idx)
        else:
            self.combo_zoom.setEditText(cur_zoom)
        layout_common.addRow("Масштаб интерфейса (UI):", self.combo_zoom)

        self.chk_lines = QCheckBox("Показывать номера строк в редакторе")
        self.chk_lines.setChecked(self.config.get("show_line_numbers", False))
        layout_common.addRow("Нумерация строк:", self.chk_lines)

        self.chk_switch_tab = QCheckBox("Переключаться на первую вкладку после симуляции")
        self.chk_switch_tab.setChecked(self.config.get("switch_to_first_tab_after_simulating", False))
        layout_common.addRow("Информация:", self.chk_switch_tab)

        layout.addWidget(group_common)

        form_top = QFormLayout()
        form_top.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.combo_mode = QComboBox()
        self.combo_mode.addItems(["Нативный GPSS/H", "Эмулятор DOSBox"])

        # Определяем начальный режим
        use_dos = self.config.get("use_dos_emulation", False)
        self.combo_mode.setCurrentIndex(1 if use_dos else 0)
        self.combo_mode.currentIndexChanged.connect(self._on_mode_changed)

        form_top.addRow("Среда выполнения:", self.combo_mode)
        layout.addLayout(form_top)

        # ==================================================================
        # ГРУППА 2: Нативные настройки
        # ==================================================================
        self.group_native = QGroupBox("Параметры нативного запуска")
        layout_native = QFormLayout(self.group_native)
        layout_native.setSpacing(10)
        layout_native.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.combo_os = QComboBox()
        self.combo_os.addItems(["Windows", "Linux"])
        if self.config.get("target_os", "windows").lower() == "linux":
            self.combo_os.setCurrentIndex(1)
        self.combo_os.currentIndexChanged.connect(self._on_os_changed)
        layout_native.addRow("Операционная система:", self.combo_os)

        box_exe = QHBoxLayout()
        box_exe.setSpacing(6)
        self.edit_exe = QLineEdit(self.config.get("executable_path", ""))
        btn_browse_exe = QPushButton("Обзор...")
        btn_browse_exe.clicked.connect(self._browse_exe)
        box_exe.addWidget(self.edit_exe, 1)
        box_exe.addWidget(btn_browse_exe)
        layout_native.addRow("Исполняемый файл GPSS:", box_exe)

        layout.addWidget(self.group_native)

        # ==================================================================
        # ГРУППА 3: Настройки DOSBox
        # ==================================================================
        self.group_dos = QGroupBox("Параметры эмуляции DOSBox")
        layout_dos = QFormLayout(self.group_dos)
        layout_dos.setSpacing(10)
        layout_dos.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        box_dosbox = QHBoxLayout()
        box_dosbox.setSpacing(6)
        self.edit_dosbox = QLineEdit(self.config.get("dos_executable_path", ""))
        btn_browse_dosbox = QPushButton("Обзор...")
        btn_browse_dosbox.clicked.connect(self._browse_dosbox)
        box_dosbox.addWidget(self.edit_dosbox, 1)
        box_dosbox.addWidget(btn_browse_dosbox)
        layout_dos.addRow("Путь к dosbox.exe:", box_dosbox)

        box_mount = QHBoxLayout()
        box_mount.setSpacing(6)
        self.edit_mount = QLineEdit(self.config.get("dos_mount_path", ""))
        btn_browse_mount = QPushButton("Обзор...")
        btn_browse_mount.clicked.connect(self._browse_mount)
        box_mount.addWidget(self.edit_mount, 1)
        box_mount.addWidget(btn_browse_mount)
        layout_dos.addRow("Папка монтирования (C:):", box_mount)

        self.chk_abort = QCheckBox("Автоматически закрывать DOSBox после симуляции")
        self.chk_abort.setChecked(self.config.get("dos_abort_after_execution", True))
        layout_dos.addRow("", self.chk_abort)

        layout.addWidget(self.group_dos)

        # --- Кнопки внизу ---
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

    def _on_mode_changed(self, index):
        """Динамически показывает/скрывает блоки настроек."""
        is_dos = (index == 1)

        # Прячем/показываем группы
        self.group_native.setVisible(not is_dos)
        self.group_dos.setVisible(is_dos)

        # Подгоняем размер окна под контент
        self.adjustSize()

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

    # --- Обработчики кнопок "Обзор" ---

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

    def _browse_dosbox(self):
        start_dir = os.path.dirname(self.edit_dosbox.text().strip()) or self.config.get("work_dir", "")
        path, _ = QFileDialog.getOpenFileName(self, "Выбор DOSBox", start_dir,
                                              "Исполняемые файлы (*.exe);;Все файлы (*.*)")
        if path:
            self.edit_dosbox.setText(os.path.normpath(path))

    def _browse_mount(self):
        start_dir = self.edit_mount.text().strip() or self.config.get("work_dir", "")
        path = QFileDialog.getExistingDirectory(self, "Выбор папки для монтирования", start_dir)
        if path:
            self.edit_mount.setText(os.path.normpath(path))

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
        # Сохраняем переключатель режима
        self.config["use_dos_emulation"] = (self.combo_mode.currentIndex() == 1)

        # Сохраняем настройки DOSBox
        self.config["dos_executable_path"] = self.edit_dosbox.text().strip()
        self.config["dos_mount_path"] = self.edit_mount.text().strip()
        self.config["dos_abort_after_execution"] = self.chk_abort.isChecked()

        # Сохраняем настройки нативного запуска
        self.config["target_os"] = self.combo_os.currentText().lower()
        self.config["executable_path"] = self.edit_exe.text().strip()

        # Сохраняем общие настройки
        self.config["work_dir"] = self.edit_work_dir.text().strip()
        self.config["theme"] = "dark" if self.combo_theme.currentIndex() == 0 else "light"
        self.config["show_line_numbers"] = self.chk_lines.isChecked()
        self.config["switch_to_first_tab_after_simulating"] = self.chk_switch_tab.isChecked()

        try:
            zoom_str = self.combo_zoom.currentText().replace("%", "").strip()
            self.config["zoom"] = int(zoom_str)
        except Exception:
            self.config["zoom"] = 100

        self.accept()
