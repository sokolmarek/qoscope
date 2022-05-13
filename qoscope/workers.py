from PySide6.QtCore import QObject, Signal, QMutex


class AcquisitionWorker(QObject):
    finished = Signal()
    data_ready = Signal()

    def __init__(self, wait_condition, device, parent=None):
        super().__init__(parent=parent)
        self.wait_condition = wait_condition
        self.device = device
        self.mutex = QMutex()

    def run(self):
        while True:
            self.mutex.lock()
            self.wait_condition.wait(self.mutex)
            self.mutex.unlock()

            self.data = self.device.acquire_single()
            self.data_ready.emit()

        self.finished.emit()
