@echo off
chcp 65001 > nul
title Сборка GPSS/H Studio (.exe)

echo ======================================================================
echo             GPSS/H Studio - Запуск автоматической сборки
echo ======================================================================
echo.

cd /d "%~dp0"

:: Проверка наличия python в PATH
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [-] ОШИБКА: Python не найден в переменной PATH.
    echo     Убедитесь, что Python установлен и добавлен в PATH.
    pause
    exit /b 1
)

:: Запуск сборочного скрипта
python build.py %*

if %errorlevel% neq 0 (
    echo.
    echo [-] Во время сборки произошла ошибка.
    pause
    exit /b %errorlevel%
)

echo.
echo [+] Нажмите любую клавишу для закрытия этого окна...
pause > nul

