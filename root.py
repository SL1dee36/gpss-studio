import os
import sys


def get_app_dir():
    if "__compiled__" in globals():
        c = globals()["__compiled__"]
        if hasattr(c, "containing_dir") and c.containing_dir:
            return os.path.abspath(c.containing_dir)
        if hasattr(c, "original_argv0") and c.original_argv0:
            return os.path.dirname(os.path.abspath(c.original_argv0))
    if hasattr(sys, "_MEIPASS") and getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    if getattr(sys, "frozen", False) and sys.argv and sys.argv[0]:
        return os.path.dirname(os.path.abspath(sys.argv[0]))
    return os.path.dirname(os.path.abspath(__file__))


def get_resource_path(relative_path):
    app_dir = get_app_dir()
    app_path = os.path.join(app_dir, relative_path)
    if os.path.exists(app_path):
        return app_path

    candidates = []
    if hasattr(sys, "_MEIPASS"):
        candidates.append(sys._MEIPASS)
    try:
        candidates.append(os.path.dirname(os.path.abspath(__file__)))
    except Exception:
        pass
    candidates.append(os.getcwd())

    for c_dir in candidates:
        if c_dir:
            full_path = os.path.join(c_dir, relative_path)
            if os.path.exists(full_path):
                return full_path

    return app_path
