from abc import ABC, abstractmethod, ABCMeta

from PySide6.QtCore import QThread, Signal


class _ABCMeta(type(QThread), ABCMeta):
    pass


class ISimulationThread(QThread, ABC, metaclass=_ABCMeta):
    # (success, retcode, stdout, stderr, lis_text, err_msg)
    simulation_finished = Signal(bool, int, str, str, str, str)
    status_updated = Signal(str)

    @abstractmethod
    def cancel(self):
        ...

    @abstractmethod
    def run(self):
        ...
