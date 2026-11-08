from abc import ABC, abstractmethod
from app.runner.abc_thread import ISimulationThread


class IRunner(ABC):
    thread: ISimulationThread

    @abstractmethod
    def run_gps(
        self, work_dir, gps_file, lis_file, parent,
        on_simulation_status, on_simulation_finished
    ):
        ...

    @abstractmethod
    def stop(self):
        ...

    @abstractmethod
    def ensure_stop(self):
        ...

    @abstractmethod
    def validate_runner_path(self) -> bool:
        ...

    @abstractmethod
    def get_failed_path_msg(self):
        ...

    @abstractmethod
    def set_runner_path_from_config(self, config):
        ...

    def is_running(self):
        if self.thread and self.thread.isRunning():
            return True
        return False
