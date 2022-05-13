from PySide6.QtCore import QObject, Slot, Signal, Property
from PySide6.QtGui import QPolygonF
from PySide6 import QtCharts
import shiboken6 as shiboken
import numpy as np
import ctypes


class Bridge(QObject):
    def __init__(self, controller, parent=None):
        super(Bridge, self).__init__(parent=parent)
        self.controller = controller

        self.is_running = False
        self.is_connected = False
        self.data = []

        self.x_axis = None
        self.y_axis = None

        self.fps = 0

    # Convert and update data
    def update_data(self, x, y):
        size = x.size
        data = QPolygonF()
        data.resize(size)

        address = shiboken.getCppPointer(data.data())[0]
        buffer = (ctypes.c_double * 2 * size).from_address(address)

        memory = np.frombuffer(buffer, np.float64)
        memory[: (size - 1) * 2 + 1: 2] = np.array(x, dtype=np.float64, copy=False)
        memory[1: (size - 1) * 2 + 2: 2] = np.array(y, dtype=np.float64, copy=False)

        self.data = data

    # Acquisition and device buttons handlers
    @Slot(result=bool)
    def on_run_stop_button(self):
        if self.is_running:
            self.is_running = False
            self.controller.oscilloscope_stop()
        else:
            if self.controller.oscilloscope_continuous_run():
                self.is_running = True

    @Slot(result=bool)
    def on_single_button(self):
        self.is_running = False
        return self.controller.oscilloscope_single_run()

    @Slot(str, result=bool)
    def connect_to_device(self, port):
        if not self.is_connected:
            self.controller.connect_to_device(port)
        else:
            self.controller.disconnect_device()
        self.is_connected = self.controller.is_device_connected()
        return self.is_connected

    @Slot()
    def disconnect_from_device(self):
        self.controller.disconnect_device()

    # Update plot
    @Slot(QtCharts.QXYSeries)
    def update_plot(self, series):
        series.replace(self.data)

    @Slot(QtCharts.QXYSeries)
    def clear_plot(self, series):
        series.clear()

    # Expose QtChart axes to backend
    @Slot(QtCharts.QValueAxis, QtCharts.QValueAxis)
    def expose_axes(self, x, y):
        self.x_axis = x
        self.y_axis = y

    # Change X axis range
    def setXRange(self, min, max):
        if self.x_axis:
            self.x_axis.setRange(min, max)

    # Change Y axis range
    def setYRange(self, min, max):
        if self.y_axis:
            self.y_axis.setRange(min, max)

    # Acquisition continuous check
    @Slot(result=bool)
    def get_acquisition_state(self):
        return self.controller.continuous_acquisition

    @Slot(bool)
    def set_acquisition_state(self, status):
        self.controller.continuous_acquisition = status
        self.on_acquisition_state_changed.emit(self.controller.continuous_acquisition)

    # Trigger checkbox handler
    @Slot(result=bool)
    def get_trigger_state(self):
        return self.controller.device.trigger_on

    @Slot(bool)
    def set_trigger_state(self, state):
        self.controller.set_trigger_state(state)
        self.on_trigger_state_changed.emit(self.controller.device.trigger_on)

    # Trigger combobox handler
    @Slot(result=str)
    def get_trigger_slope(self):
        return self.controller.device.trigger_slope

    @Slot(str)
    def set_trigger_slope(self, slope):
        self.controller.set_trigger_slope(slope)
        self.on_trigger_slope_changed.emit(self.controller.device.trigger_slope)

    # Timebase combobox handler
    @Slot(result=str)
    def get_timebase(self):
        return self.controller.device.timebase

    @Slot(str)
    def set_timebase(self, timebase):
        self.controller.set_timebase(timebase)
        self.on_timebase_changed.emit(self.controller.device.timebase)

    # Ports combobox handler
    @Slot(result=list)
    def get_ports(self):
        return self.controller.get_ports_names()

    @Slot(result=bool)
    def get_connection(self):
        return self.is_connected

    @Slot(bool)
    def set_connection(self, c):
        self.is_connected = c
        self.on_connection_changed.emit(self.is_connected)

    @Slot(result=float)
    def get_fps(self):
        return self.fps

    @Slot(float)
    def set_fps(self, val):
        self.fps = val
        self.on_fps_changed.emit(self.fps)

    # Signals
    on_acquisition_state_changed = Signal(bool)
    on_trigger_state_changed = Signal(bool)
    on_trigger_slope_changed = Signal(str)
    on_timebase_changed = Signal(str)
    on_ports_changed = Signal(list)
    on_connection_changed = Signal(bool)
    on_fps_changed = Signal(float)

    # Props
    acquisition_state = Property(
        bool, get_acquisition_state, set_acquisition_state, notify=on_acquisition_state_changed
    )
    trigger_state = Property(
        bool, get_trigger_state, set_trigger_state, notify=on_trigger_state_changed
    )
    trigger_slope = Property(
        str, get_trigger_slope, set_trigger_slope, notify=on_trigger_slope_changed
    )
    timebase = Property(
        str, get_timebase, set_timebase, notify=on_timebase_changed
    )
    ports = Property(
        list, get_ports, notify=on_ports_changed
    )
    connection = Property(
        bool, get_connection, set_connection, notify=on_connection_changed
    )
    qfps = Property(
        float, get_fps, set_fps, notify=on_fps_changed
    )
