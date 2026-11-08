import runpy
import os
import sys

target = os.path.join(os.path.dirname(os.path.realpath(__file__)), "gpss-studio.py")

sys.argv[0] = target
sys.path.insert(0, os.path.dirname(target))

# Запускаем gpss-studio.py как главный модуль
runpy.run_path(target, run_name="__main__")
