import os
import shutil
import sys
from typing import Optional

from app.runner.abc_runner import IRunner
from app.runner.abc_thread import ISimulationThread
from app.runner.windows_thread import WindowsSimulationThread
from root import get_resource_path


class WindowsRunner(IRunner):
    def __init__(self, config, target_os):
        self.target_os = target_os
        self.exe_path = self.check_exe_file(config.get("executable_path", ""))
        self.thread: Optional[ISimulationThread] = None

    def check_exe_file(self, exe_path):
        if not os.path.exists(exe_path):
            exe_name = "gpssh.exe" if self.target_os == "windows" else "gpssh"
            exe_path = get_resource_path(exe_name)
            if not os.path.exists(exe_path):
                which_p = shutil.which(exe_name) or shutil.which("gpssh") or shutil.which("gpssh.exe")
                if which_p:
                    exe_path = which_p
        return exe_path

    def validate_runner_path(self):
        if os.path.exists(self.exe_path):
            return True

        exe_name = "gpssh.exe" if self.target_os == "windows" else "gpssh"
        fallback = shutil.which(self.exe_path) or shutil.which(exe_name) or shutil.which("gpssh") or shutil.which("gpssh.exe") or get_resource_path(exe_name)
        if fallback and os.path.exists(fallback):
            self.exe_path = fallback
            return True

        return False

    def get_failed_path_msg(self):
        extra_hint = ""
        if sys.platform != "win32" and self.exe_path.lower().endswith(".exe"):
            if not shutil.which("wine"):
                extra_hint = \
                    "\n\nПодсказка для Linux: запуск Windows .exe требует установленного Wine (apt install wine)."
        return (
            f"Исполняемый файл GPSS не найден!\n\nПуть: {self.exe_path}\n"
            f"Целевая ОС: {'Windows' if self.target_os == 'windows' else 'Linux'}\n\n"
            f"Укажите правильный путь в настройках (кнопка 'menu' -> Настройки).{extra_hint}"
        )

    def set_runner_path_from_config(self, config):
        path = config.get("executable_path", "")
        self.exe_path = self.check_exe_file(path)

    def run_gps(
        self, work_dir, gps_file, lis_file, parent,
        on_simulation_status, on_simulation_finished
    ):
        # Start simulation in background QThread
        self.thread = WindowsSimulationThread(
            self.exe_path, work_dir, gps_file, lis_file,
            target_os=self.target_os, parent=parent
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
