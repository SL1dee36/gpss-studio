#!/usr/bin/env python3
"""
GPSS/H Studio Nuitka Build Script
Скрипт автоматической компиляции проекта в автономный исполняемый файл .exe с помощью Nuitka.

Использование:
    python builder/build.py [параметры]
    или запустите builder/build.bat (двойным кликом в Windows)

Параметры:
    --mode [onefile|standalone]   Режим сборки (по умолчанию: onefile - единый .exe)
    --clean                       Очистить временные папки сборки после завершения
    --keep-build                  Не удалять промежуточные сборочные кэши
    --no-root-copy                Не копировать итоговый .exe в корень проекта
"""

import argparse
import os
import shutil
import subprocess
import sys
import time

# Определение путей
BUILDER_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BUILDER_DIR, ".."))
ENTRY_POINT = os.path.join(PROJECT_ROOT, "gpss-studio.py")
ICON_PATH = os.path.join(PROJECT_ROOT, "gpss-studio.ico")
DIST_DIR = os.path.join(BUILDER_DIR, "dist")
BUILD_DIR = os.path.join(BUILDER_DIR, "build")

APP_NAME = "gpss-studio"
APP_TITLE = "GPSS Studio"
VERSION = "1.7.0"
VERSION_TUPLE = "1.7.0.0"
COMPANY = "SL1dee36"
COPYRIGHT = "Copyright (c) 2026 Nazaryan Artem. MIT License."


def print_banner():
    banner = f"""
======================================================================
           GPSS/H Studio - Сборщик исполняемого файла (.exe)          
======================================================================
  Версия приложения: {VERSION}
  Корневая папка:    {PROJECT_ROOT}
  Точка входа:       {ENTRY_POINT}
======================================================================
"""
    print(banner)


def check_prerequisites():
    print("[1/4] Проверка зависимостей и сборочного окружения...")

    # Проверка наличия Python 3.8+
    if sys.version_info < (3, 8):
        print("[-] ОШИБКА: Требуется Python 3.8 или выше.")
        sys.exit(1)
    print(f"  [+] Python: {sys.version.split()[0]}")

    # Проверка наличия точки входа и иконки
    if not os.path.exists(ENTRY_POINT):
        print(f"[-] ОШИБКА: Файл точки входа не найден: {ENTRY_POINT}")
        sys.exit(1)
    if not os.path.exists(ICON_PATH):
        print(f"[-] ВНИМАНИЕ: Иконка не найдена: {ICON_PATH}")

    # Проверка наличия PySide6
    try:
        import PySide6
        print(f"  [+] PySide6: v{PySide6.__version__}")
    except ImportError:
        print("[-] ОШИБКА: Библиотека PySide6 не установлена.")
        print("    Установите её командой: pip install PySide6")
        sys.exit(1)

    # Проверка наличия Nuitka
    try:
        import nuitka.Version
        nuitka_ver = nuitka.Version.getNuitkaVersion()
        print(f"  [+] Nuitka: v{nuitka_ver}")
    except Exception:
        print("[-] ОШИБКА: Nuitka не установлена в текущем окружении Python.")
        print("    Установите её командой: pip install nuitka zstandard")
        sys.exit(1)

    print("  [+] Все предварительные проверки пройдены успешно.\n")


def build_command(mode="onefile"):
    print(f"[2/4] Формирование параметров компиляции Nuitka (режим: {mode})...")
    os.makedirs(DIST_DIR, exist_ok=True)
    os.makedirs(BUILD_DIR, exist_ok=True)

    cmd = [
        sys.executable,
        "-m", "nuitka",
        ENTRY_POINT,
        f"--output-dir={DIST_DIR}",
        f"--output-filename={APP_NAME}.exe",
        "--enable-plugin=pyside6",
        "--include-package=app",
        "--assume-yes-for-downloads",
        "--windows-console-mode=disable",
    ]

    # Режим сборки: onefile (единый exe) или standalone (папка с dll)
    if mode == "onefile":
        cmd.append("--onefile")
        cmd.append(f"--onefile-tempdir-spec=%TEMP%\\gpss_studio_{VERSION}")
    else:
        cmd.append("--standalone")

    # Иконка приложения
    if os.path.exists(ICON_PATH):
        cmd.append(f"--windows-icon-from-ico={ICON_PATH}")
        cmd.append(f"--include-data-files={ICON_PATH}=gpss-studio.ico")

    # Метаданные PE-заголовка Windows
    cmd.extend([
        f"--company-name={COMPANY}",
        f"--product-name={APP_TITLE}",
        f"--file-description={APP_TITLE} Desktop IDE",
        f"--product-version={VERSION}",
        f"--file-version={VERSION_TUPLE}",
        f"--copyright={COPYRIGHT}",
    ])

    return cmd


def execute_build(cmd):
    print("[3/4] Запуск компиляции Nuitka...")
    print("      (Процесс может занять 1-3 минуты в зависимости от процессора)\n")
    print(f"Команда:\n{' '.join(cmd)}\n")

    start_time = time.time()
    try:
        process = subprocess.run(cmd, cwd=PROJECT_ROOT)
        elapsed = time.time() - start_time
        if process.returncode != 0:
            print(f"\n[-] Сборка завершилась с ошибкой (код {process.returncode}).")
            sys.exit(process.returncode)
        print(f"\n[+] Компиляция успешно завершена за {elapsed:.1f} сек.")
    except KeyboardInterrupt:
        print("\n[-] Сборка прервана пользователем.")
        sys.exit(130)


def finalize_build(mode, copy_to_root=True, clean_temp=False):
    print("\n[4/4] Финализация сборки и проверка файлов...")

    if mode == "onefile":
        built_exe = os.path.join(DIST_DIR, f"{APP_NAME}.exe")
        if not os.path.exists(built_exe):
            print(f"[-] ОШИБКА: Итоговый файл не обнаружен по пути: {built_exe}")
            sys.exit(1)

        size_mb = os.path.getsize(built_exe) / (1024 * 1024)
        print(f"  [+] Собранный файл: {built_exe}")
        print(f"  [+] Размер файла:   {size_mb:.2f} МБ")

        if copy_to_root:
            target_root_exe = os.path.join(PROJECT_ROOT, f"{APP_NAME}.exe")
            shutil.copy2(built_exe, target_root_exe)
            print(f"  [+] Скопирован в корень проекта: {target_root_exe}")

    else:
        dist_folder = os.path.join(DIST_DIR, f"{APP_NAME}.dist")
        built_exe = os.path.join(dist_folder, f"{APP_NAME}.exe")
        if not os.path.exists(built_exe):
            print(f"[-] ОШИБКА: Исполняемый файл не найден в {dist_folder}")
            sys.exit(1)
        print(f"  [+] Папка дистрибутива: {dist_folder}")

    if clean_temp:
        print("\nОчистка временных сборочных директорий...")
        for pattern in [f"{APP_NAME}.build", f"{APP_NAME}.onefile-build"]:
            p = os.path.join(DIST_DIR, pattern)
            if os.path.exists(p):
                shutil.rmtree(p, ignore_errors=True)
                print(f"  [-] Удалено: {p}")

    print("\n======================================================================")
    print("                    СБОРКА УСПЕШНО ЗАВЕРШЕНА!                         ")
    print("======================================================================")


def main():
    parser = argparse.ArgumentParser(description="GPSS/H Studio Nuitka Builder")
    parser.add_argument(
        "--mode",
        choices=["onefile", "standalone"],
        default="onefile",
        help="Режим сборки (onefile - единый .exe, standalone - папка со всеми dll)",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Удалить временные файлы компиляции (.build) после сборки",
    )
    parser.add_argument(
        "--no-root-copy",
        action="store_true",
        help="Не копировать собранный .exe в корень проекта",
    )
    args = parser.parse_args()

    print_banner()
    check_prerequisites()
    cmd = build_command(mode=args.mode)
    execute_build(cmd)
    finalize_build(
        mode=args.mode,
        copy_to_root=not args.no_root_copy,
        clean_temp=args.clean,
    )


if __name__ == "__main__":
    main()
