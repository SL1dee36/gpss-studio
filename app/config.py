import json
import os
import shutil
import sys

from root import get_app_dir, get_resource_path


class ConfigManager:
    CONFIG_FILE = "settings.json"

    @classmethod
    def get_config_path(cls):
        app_dir = get_app_dir()
        return os.path.join(app_dir, cls.CONFIG_FILE)

    @classmethod
    def load(cls):
        app_dir = get_app_dir()
        is_win = sys.platform == "win32"
        exe_name = "gpssh.exe" if is_win else "gpssh"
        default_exe = get_resource_path(exe_name)

        defaults = {
            "target_os": "windows" if is_win else "linux",
            "executable_path": default_exe,
            "use_dos_emulation": False,
            "dos_executable_path": r'C:\Program Files (x86)\DOSBox-0.74-3\DOSBox.exe',
            "dos_mount_path": '',
            "dos_abort_after_execution": True,
            "theme": "dark",
            "work_dir": app_dir,
            "show_line_numbers": False,
            "zoom": 100
        }

        path = cls.get_config_path()
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                defaults.update(data)
            except Exception:
                pass

        # Если путь к исполняемому файлу из настроек не существует, пробуем fallback
        if not os.path.exists(defaults.get("executable_path", "")):
            candidate = get_resource_path(exe_name)
            if os.path.exists(candidate):
                defaults["executable_path"] = candidate
            else:
                which_p = shutil.which(exe_name) or shutil.which("gpssh") or shutil.which("gpssh.exe")
                if which_p:
                    defaults["executable_path"] = which_p

        # Если рабочая папка не существует, сбрасываем на папку приложения
        if not os.path.exists(defaults.get("work_dir", "")):
            defaults["work_dir"] = app_dir

        cls.save(defaults)

        return defaults

    @classmethod
    def save(cls, config):
        path = cls.get_config_path()
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception:
            pass


