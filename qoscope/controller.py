from PySide6.QtCore import QThread, QTimer, QWaitCondition
from PySide6.QtWidgets import QApplication, QMessageBox
import serial.tools.list_ports
import numpy as np
import time
import sys

from qoscope.workers import AcquisitionWorker
from qoscope.bridge import Bridge
from qoscope.device import Device


class Controller:
    def __init__(self):
        # bridge between frontend and backend
        self.bridge = Bridge(controller=self)

        # device
        self.device = Device()

        # app
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("QOscope")

        # fps stats
        self.fps_timer = QTimer()
        self.fps_timer.timeout.connect(self.update_ui_fps)
        self.spf = 1  # seconds per frame
        self.timestamp_last_capture = 0

        # acquisition thread
        self.continuous_acquisition = False
        self.worker_wait_condition = QWaitCondition()
        self.acquisition_worker = AcquisitionWorker(self.worker_wait_condition, device=self.device)
        self.acquisition_thread = QThread()
        self.acquisition_worker.moveToThread(self.acquisition_thread)
        self.acquisition_thread.started.connect(self.acquisition_worker.run)
        self.acquisition_worker.finished.connect(self.acquisition_thread.quit)
        self.acquisition_thread.finished.connect(self.acquisition_worker.deleteLater)
        self.acquisition_worker.data_ready.connect(self.data_ready_callback)
        self.acquisition_thread.start()

        # default timebase
        self.set_timebase("20 ms")

        # on app exit
        self.app.aboutToQuit.connect(self.on_app_exit)

    def run_app(self):
        return self.app.exec()

    def get_ports_names(self):
        return [p.device for p in serial.tools.list_ports.comports()]

    def update_ui_fps(self):
        self.bridge.set_fps(1 / self.spf)

    def set_timebase(self, timebase):
        # send timebase to device
        self.device.timebase = timebase
        if self.is_device_connected():
            self.device.write_timebase()
        # adjust timebase in the screen
        seconds_per_sample = (
                float(timebase.split()[0]) / 10
                * {"ms": 1e-3, "us": 1e-6}[timebase.split()[1]]
        )
        self.data_time_array = (
                np.arange(0, self.device.BUFFER_SIZE) * seconds_per_sample
        )
        self.bridge.setXRange(0, self.device.BUFFER_SIZE * seconds_per_sample)
        self.bridge.setYRange(0, 5)

    def set_trigger_state(self, state):
        self.device.trigger_on = state
        if self.is_device_connected():
            self.device.write_trigger_state()

    def set_trigger_slope(self, slope):
        self.device.trigger_slope = slope
        if self.is_device_connected():
            self.device.write_trigger_slope()

    def connect_to_device(self, port):
        if port == "":
            self.bridge.set_connection(False)
        elif port not in self.get_ports_names():
            self.bridge.set_connection(False)
        else:
            self.device.connect(port)
            self.bridge.set_connection(True)

    def disconnect_device(self):
        self.device.disconnect()
        self.bridge.set_connection(False)

    def is_device_connected(self):
        return self.device.is_connected()

    def oscilloscope_single_run(self):
        if self.device.is_connected():
            self.device.clean_buffers()
            self.worker_wait_condition.notify_one()
            return True
        else:
            return False

    def oscilloscope_continuous_run(self):
        if self.device.is_connected():
            self.timestamp_last_capture = time.time()
            self.spf = 1
            self.fps_timer.start(500)
            self.continuous_acquisition = True
            self.bridge.set_acquisition_state(True)
            self.device.clean_buffers()
            self.worker_wait_condition.notify_one()
            return True
        else:
            return False

    def oscilloscope_stop(self):
        self.bridge.set_acquisition_state(False)
        self.continuous_acquisition = False
        self.fps_timer.stop()

    def data_ready_callback(self):
        curr_time = time.time()
        self.spf = 0.9 * (curr_time - self.timestamp_last_capture) + 0.1 * self.spf
        self.timestamp_last_capture = curr_time
        self.bridge.update_data(
            self.data_time_array, self.acquisition_worker.data
        )
        if self.continuous_acquisition == True:
            self.worker_wait_condition.notify_one()

    def on_app_exit(self):
        print("exiting...")
