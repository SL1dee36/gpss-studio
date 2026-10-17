import os
import shutil
import subprocess
from PySide6.QtCore import Signal

from app.runner.abc_thread import ISimulationThread


class DosBoxSimulationThread(ISimulationThread):
    # (success, retcode, stdout, stderr, lis_text, err_msg)
    simulation_finished = Signal(bool, int, str, str, str, str)
    status_updated = Signal(str)

    def __init__(
            self, dosbox_path, mount_path, work_dir, gps_file, lis_file,
            parent=None, abort_after_execution=True
    ):
        super().__init__(parent)
        self.dosbox_path = dosbox_path
        self.mount_path = mount_path
        self.work_dir = work_dir
        self.gps_file = gps_file
        self.lis_file = lis_file
        self.abort_after_execution = abort_after_execution
        self._process = None
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True
        proc = self._process
        if proc and proc.poll() is None:
            try:
                proc.kill()
            except Exception:
                pass

    def run(self):
        self.status_updated.emit("Подготовка к запуску DOSBox...")
        dosbox_gpssh_root = os.path.join(self.mount_path, "GPSSH")

        # Помещаем GPS файл в диск DOSBox
        shutil.copy2(self.gps_file, dosbox_gpssh_root)

        # Команды для выполнения внутри DOSBox
        commands = [
            f'MOUNT C "{self.mount_path}"',
            "C:",
            "cd GPSSH",
            "GPSSH MODEL.GPS",
        ]

        if self.abort_after_execution:
            commands.append('exit')
        else:
            commands.append('echo CLOSE THIS WINDOW TO SEE RESULTS IN GPSS-STUDIO')

        # Формируем аргументы для запуска
        args = [self.dosbox_path, "-noconsole"]
        for cmd in commands:
            args.extend(["-c", cmd])

        try:
            self.status_updated.emit("Запуск DOSBox...")
            self._process = subprocess.Popen(
                args,
                cwd=self.mount_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                errors="replace"
            )
        except Exception as e:
            self.simulation_finished.emit(False, -1, "", "", "", f"Не удалось запустить DOSBox:\n{e}")
            return

        self.status_updated.emit("Выполняется симуляция в DOSBox...")

        stdout, stderr = "", ""
        try:
            stdout, stderr = self._process.communicate(timeout=120)
        except subprocess.TimeoutExpired:
            self.cancel()
            self.simulation_finished.emit(
                False, -1, stdout, stderr, "",
                "Симуляция превысила лимит времени (120 сек).\n"
                "DOSBox не был закрыт. Добавьте 'exit' в команды запуска."
            )
            return
        except Exception as e:
            self.cancel()
            self.simulation_finished.emit(False, -1, stdout, stderr, "", f"Ошибка выполнения:\n{e}")
            return

        if self._is_cancelled:
            self.simulation_finished.emit(False, -1, stdout, stderr, "", "Симуляция прервана пользователем.")
            return

        retcode = self._process.returncode if self._process else 0

        # Проверяем, создался ли файл листинга
        dosbox_lis_file = os.path.join(dosbox_gpssh_root, "MODEL.LIS")
        if os.path.exists(dosbox_lis_file):
            # Забираем LIS файл с диска DOSBox
            shutil.copy2(dosbox_lis_file, self.lis_file)
        else:
            self.simulation_finished.emit(
                False, retcode, stdout, stderr, "",
                "Файл model.lis не был создан. Проверьте, отработал ли GPSSH."
            )
            return

        # Читаем листинг
        lis_text = ""
        for enc in ("cp866", "utf-8", "latin-1", "windows-1251"):
            try:
                with open(self.lis_file, "r", encoding=enc) as f:
                    lis_text = f.read()
                break
            except UnicodeDecodeError:
                continue

        self.simulation_finished.emit(True, retcode, stdout, stderr, lis_text, "")
