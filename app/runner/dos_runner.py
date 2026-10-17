import os
import shutil
import sys
from typing import Optional

from app.consts import DOS_GPSSH_URL
from app.runner.abc_thread import ISimulationThread
from app.runner.dos_thread import DosBoxSimulationThread

from app.runner.abc_runner import IRunner
from root import get_app_dir


class DosRunner(IRunner):
    def __init__(self, config, target_os):
        self.target_os = target_os
        self.dosbox_path = self.check_dosbox_file(config.get("dos_executable_path", ""))
        self.mount_path = self.check_mount_dir(config.get("dos_mount_path", ""))
        self.abort_after_execution = bool(config.get("dos_abort_after_execution", True))
        self.thread: Optional[ISimulationThread] = None

    def check_dosbox_file(self, dosbox_path):
        if os.path.exists(dosbox_path):
            return dosbox_path
        return r"C:\Program Files (x86)\DOSBox-0.74-3\DOSBox.exe"

    def check_mount_dir(self, mount_path):
        if os.path.exists(mount_path):
            return mount_path
        dosbox_dir = os.path.join(get_app_dir(), "DOSBOX")
        os.makedirs(dosbox_dir, exist_ok=True)

        return dosbox_dir

    def validate_dosbox_path(self):
        if os.path.exists(self.dosbox_path):
            return True

        fallback = r"C:\Program Files (x86)\DOSBox-0.74-3\DOSBox.exe"
        if fallback and os.path.exists(fallback):
            self.dosbox_path = fallback
            return True
        return False

    def validate_mount_dir(self):
        gpssh_dir = os.path.join(self.mount_path, "GPSSH")
        gpssh_exe_dir = os.path.join(gpssh_dir, "GPSSH.EXE")
        return os.path.exists(gpssh_exe_dir)

    def validate_runner_path(self):
        return self.validate_dosbox_path() and self.validate_mount_dir()

    def get_failed_path_msg(self):
        text = ""
        dosbox_installed = self.validate_dosbox_path()
        if not dosbox_installed:
            text = f"Исполняемый файл DOSBox не найден!\n\nПуть: {self.dosbox_path}\n" \
                   f"Укажите правильный путь в настройках (кнопка 'menu' -> Настройки).\n\n"
        else:
            text = f"ПОХОЖЕ, ВЫ НЕ УСТАНОВИЛИ GPSSH.EXE НА ЭМУЛЯТОР DOSBOX\n\n" \
                   f"[1] Программа ожидает увидеть такую установку GPSSH.EXE:\n" \
                   f"MOUNT_DIR\\GPSSH\\GPSSH.EXE\n" \
                   f"Где MOUNT_DIR задаётся в настройках.\n\n" \
                   f"[2] Скачать можно тут: \n{DOS_GPSSH_URL}\n\n" \
                   f"[3] После скачивания, положите файл в папку \n{self.mount_path}\n\n" \
                   f"[4] Запустите DOSBox и введите команды для установки:\n\n" \
                   f"> mount c: {self.mount_path}\n" \
                   f"> INSTALL.EXE\n\n" \
                   f"[5] Завершите установку, соглашаясь со всем. Готово!\n\n"

        extra_hint = ""
        if sys.platform != "win32":
            extra_hint = \
                "Подсказка для Linux: НЕ НАДО ПЫТАТЬСЯ ЗАПУСТИТЬ ЭТО В ЭМУЛЯТОРЕ DOS. Запускай через Wine."

        text += f"Режим запуска: Эмулятор DOS, DOSBox\n" \
                f"Целевая ОС: {'Windows' if self.target_os == 'windows' else 'Linux'}\n\n{extra_hint}"

        return text

    def set_runner_path_from_config(self, config):
        path = config.get("executable_path", "")
        self.dosbox_path = self.check_dosbox_file(path)

    def run_gps(
        self, work_dir, gps_file, lis_file, parent,
        on_simulation_status, on_simulation_finished
    ):
        # Start simulation in background QThread
        self.thread = DosBoxSimulationThread(
            self.dosbox_path, self.mount_path, work_dir, gps_file, lis_file,
            parent=parent, abort_after_execution=self.abort_after_execution
        )
        self.thread.status_updated.connect(on_simulation_status)
        self.thread.simulation_finished.connect(on_simulation_finished)
        self.thread.start()

    def stop(self):
        if self.thread and not self.is_running():
            self.thread.cancel()

    def enshure_stop(self):
        if self.thread and not self.is_running():
            self.thread.cancel()
            self.thread.wait(1500)
