import os
import shutil
import signal
import subprocess
import sys

from PySide6.QtCore import QThread, Signal


class GPSSSimulationThread(QThread):
    simulation_finished = Signal(bool, int, str, str, str, str)  # (success, retcode, stdout, stderr, lis_text, err_msg)
    status_updated = Signal(str)

    def __init__(self, exe_path, work_dir, gps_file, lis_file, target_os="windows", parent=None):
        super().__init__(parent)
        self.exe_path = exe_path
        self.work_dir = work_dir
        self.gps_file = gps_file
        self.lis_file = lis_file
        self.target_os = target_os
        self._is_cancelled = False
        self._process = None

    def cancel(self):
        self._is_cancelled = True
        proc = self._process
        if proc and proc.poll() is None:
            try:
                if sys.platform == "win32":
                    proc.kill()
                else:
                    if hasattr(os, "killpg") and hasattr(os, "getpgid"):
                        try:
                            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                        except Exception:
                            proc.kill()
                    else:
                        proc.kill()
            except Exception:
                pass

    def run(self):
        self.status_updated.emit("Подготовка к запуску GPSS/H...")

        # Ensure executable permissions on Linux/POSIX
        if sys.platform != "win32" and os.path.exists(self.exe_path):
            try:
                os.chmod(self.exe_path, 0o755)
            except Exception:
                pass

        # Build command list
        cmd = [self.exe_path, "model.gps"]

        # Support Wine on Linux if running a Windows .exe binary
        if sys.platform != "win32" and self.exe_path.lower().endswith(".exe"):
            wine_bin = shutil.which("wine")
            if wine_bin:
                cmd = [wine_bin, self.exe_path, "model.gps"]

        kwargs = {
            "cwd": self.work_dir,
            "stdin": subprocess.PIPE,
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
            "text": True,
            "errors": "replace"
        }

        if sys.platform == "win32":
            kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
        elif hasattr(os, "setsid"):
            kwargs["preexec_fn"] = os.setsid

        try:
            self._process = subprocess.Popen(cmd, **kwargs)
        except Exception as e:
            err_msg = str(e)
            if sys.platform != "win32" and ("Exec format error" in err_msg or "No such file" in err_msg):
                err_msg += (
                    "\n\nПодсказка для Linux: исполняемый файл GPSS/H может быть 32-битным (x86 ELF) или Windows (.exe).\n"
                    "- Для Windows .exe установите Wine: sudo apt install wine\n"
                    "- Для 32-битного ELF установите 32-битные библиотеки: sudo dpkg --add-architecture i386 && sudo apt install libc6:i386"
                )
            self.simulation_finished.emit(False, -1, "", "", "", f"Сбой при запуске GPSS:\n{err_msg}")
            return

        self.status_updated.emit("Выполняется симуляция...")

        stdout, stderr = "", ""
        try:
            stdout, stderr = self._process.communicate(input="model.gps\n", timeout=120)
        except subprocess.TimeoutExpired:
            self.cancel()
            self.simulation_finished.emit(
                False, -1, stdout, stderr, "",
                "Симуляция превысила лимит времени (120 сек).\nВозможно, в модели зациклен переход (проверьте TERMINATE / START / блоки TEST/TRANSFER)."
            )
            return
        except Exception as e:
            self.cancel()
            self.simulation_finished.emit(False, -1, stdout, stderr, "", f"Ошибка выполнения процесса:\n{e}")
            return

        if self._is_cancelled:
            self.simulation_finished.emit(False, -1, stdout, stderr, "", "Симуляция прервана пользователем.")
            return

        retcode = self._process.returncode if self._process else 0

        if not os.path.exists(self.lis_file):
            self.simulation_finished.emit(
                False, retcode, stdout, stderr, "",
                "Файл model.lis не был создан. Проверьте вкладку консоли на наличие синтаксических ошибок GPSS."
            )
            return

        lis_text = ""
        for enc in ("cp866", "utf-8", "latin-1", "windows-1251"):
            try:
                with open(self.lis_file, "r", encoding=enc) as f:
                    lis_text = f.read()
                break
            except UnicodeDecodeError:
                continue

        self.simulation_finished.emit(True, retcode, stdout, stderr, lis_text, "")
