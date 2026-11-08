# Description: Lightweight desktop IDE and simulation runner for Wolverine Software GPSS/H
# Author: Nazaryan Artem @Sl1dee36
# Date: 27.09.2026
# Current version: v1.6.1
# License: MIT

import os
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from app.main_window import GPSSStudio
from root import get_resource_path


def main():
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("sl1dee36.gpssstudio.ide.1.6.1")
        except Exception:
            pass

    app = QApplication(sys.argv)

    icon_path = get_resource_path("gpss-studio.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    window = GPSSStudio()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
