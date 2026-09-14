import os
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request

WINE_VERSION = "11.17"
WINE_URLS = {
    "linux": (
        "https://github.com/Kron4ek/Wine-Builds/releases/download/"
        f"{WINE_VERSION}/wine-{WINE_VERSION}-amd64-wow64.tar.xz"
    ),
    "darwin": (
        "https://github.com/Gcenx/macOS_Wine_builds/releases/download/"
        f"{WINE_VERSION}/wine-devel-{WINE_VERSION}-osx64.tar.xz"
    ),
}


class SetupError(Exception):
    pass


def data_dir():
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~\\AppData\\Local")
    elif sys.platform == "darwin":
        base = os.path.expanduser("~/Library/Application Support")
    else:
        base = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    return os.path.join(base, "gpss-studio")


class GpssRunner:
    def __init__(self):
        self.native = sys.platform == "win32"
        self.root = data_dir()
        self.wine_dir = os.path.join(self.root, f"wine-{WINE_VERSION}")
        self.prefix = os.path.join(self.root, "prefix")
        self.ready_marker = os.path.join(self.prefix, ".gpss-studio-ready")
        self.wine = os.environ.get("GPSS_WINE") or self._find_wine()

    def _find_wine(self):
        if not os.path.isdir(self.wine_dir):
            return None
        for dirpath, _, files in os.walk(self.wine_dir):
            if os.path.basename(dirpath) == "bin" and "wine" in files and "wineserver" in files:
                return os.path.join(dirpath, "wine")
        return None

    def _wine_tool(self, name):
        path = os.path.join(os.path.dirname(self.wine), name)
        return path if os.path.exists(path) else name

    def _env(self):
        env = dict(os.environ)
        env.update(
            WINEPREFIX=self.prefix,
            WINEDEBUG="-all",
            WINEDLLOVERRIDES="mscoree,mshtml=",
        )
        return env

    def needs_setup(self):
        if self.native:
            return False
        return not (self.wine and os.path.exists(self.ready_marker))

    def setup(self, progress):
        if self.native:
            return
        os.makedirs(self.root, exist_ok=True)
        if not self.wine:
            self._download_wine(progress)
        if sys.platform == "darwin":
            self._ensure_rosetta(progress)

        progress("Первичная настройка Wine (только один раз)...", None)
        try:
            subprocess.run(
                [self._wine_tool("wineboot"), "-i"],
                env=self._env(), capture_output=True, timeout=600,
            )
            subprocess.run(
                [self._wine_tool("wineserver"), "-w"],
                env=self._env(), capture_output=True, timeout=120,
            )
        except (OSError, subprocess.SubprocessError) as e:
            raise SetupError(f"Не удалось инициализировать Wine:\n{e}")
        if not os.path.exists(os.path.join(self.prefix, "system.reg")):
            raise SetupError("Wine не смог создать окружение (WINEPREFIX).")
        open(self.ready_marker, "w").close()

    def _download_wine(self, progress):
        url = WINE_URLS.get(sys.platform)
        machine = platform.machine().lower()
        if url is None or (sys.platform == "linux" and machine not in ("x86_64", "amd64")):
            raise SetupError(
                f"Платформа {sys.platform}/{machine} пока не поддерживается автоматически.\n"
                "Установите Wine вручную и укажите путь к нему в переменной GPSS_WINE."
            )

        archive = os.path.join(self.root, os.path.basename(url))
        part = archive + ".part"
        try:
            with urllib.request.urlopen(url, timeout=60) as resp, open(part, "wb") as f:
                total = int(resp.headers.get("Content-Length") or 0)
                done, last_pct = 0, -1
                while True:
                    chunk = resp.read(1 << 16)
                    if not chunk:
                        break
                    f.write(chunk)
                    done += len(chunk)
                    pct = done * 100 // total if total else None
                    if pct != last_pct:
                        last_pct = pct
                        progress(f"Загрузка Wine {WINE_VERSION}: {done >> 20} из {total >> 20} МБ", pct)
        except Exception as e:
            if not shutil.which("curl"):
                raise SetupError(f"Не удалось скачать Wine:\n{e}")
            progress(f"Загрузка Wine {WINE_VERSION} через curl...", None)
            r = subprocess.run(["curl", "-fL", "-o", part, url], capture_output=True, text=True)
            if r.returncode != 0:
                raise SetupError(f"Не удалось скачать Wine:\n{e}\n{r.stderr}")
        os.replace(part, archive)

        progress("Распаковка Wine...", None)
        shutil.rmtree(self.wine_dir, ignore_errors=True)
        try:
            with tarfile.open(archive) as tar:
                if hasattr(tarfile, "tar_filter"):
                    tar.extractall(self.wine_dir, filter="tar")
                else:
                    tar.extractall(self.wine_dir)
        except (tarfile.TarError, OSError) as e:
            shutil.rmtree(self.wine_dir, ignore_errors=True)
            raise SetupError(f"Не удалось распаковать Wine:\n{e}")
        finally:
            os.remove(archive)

        self.wine = self._find_wine()
        if not self.wine:
            raise SetupError("В скачанном архиве не найден исполняемый файл wine.")

    def _ensure_rosetta(self, progress):
        if platform.machine() != "arm64":
            return
        if subprocess.run(["arch", "-x86_64", "/usr/bin/true"], capture_output=True).returncode == 0:
            return
        progress("Установка Rosetta 2 (macOS попросит пароль администратора)...", None)
        script = 'do shell script "softwareupdate --install-rosetta --agree-to-license" with administrator privileges'
        r = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
        if r.returncode != 0:
            raise SetupError(f"Не удалось установить Rosetta 2:\n{r.stderr}")

    def run(self, exe_path, work_dir, model_name, timeout):
        if self.native:
            cmd, env = [exe_path, model_name], None
        else:
            if self.needs_setup():
                raise SetupError("Wine ещё не настроен.")
            subprocess.run(
                [self._wine_tool("wineserver"), "-p", "900"], env=self._env(),
                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            cmd, env = [self.wine, exe_path, model_name], self._env()

        with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=out,
                stderr=err,
                cwd=work_dir,
                env=env,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            try:
                proc.stdin.write((model_name + "\n").encode("ascii"))
                proc.stdin.close()
            except OSError:
                pass
            try:
                returncode = proc.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
                if not self.native:
                    subprocess.run(
                        [self._wine_tool("wineserver"), "-k"], env=self._env(),
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    )
                raise
            out.seek(0)
            err.seek(0)
            return subprocess.CompletedProcess(
                cmd, returncode,
                out.read().decode("utf-8", errors="replace"),
                err.read().decode("utf-8", errors="replace"),
            )
