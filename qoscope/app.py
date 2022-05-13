from PySide6.QtQml import QQmlApplicationEngine
from pathlib import Path
import sys
import os

from qoscope.controller import Controller

os.environ['QT_QUICK_CONTROLS_MATERIAL_VARIANT'] = "Dense"


def main():
    controller = Controller()

    engine = QQmlApplicationEngine()

    # Expose backend to QML
    context = engine.rootContext()
    context.setContextProperty("bridge", controller.bridge)

    qml_file = Path(__file__).parent / "main_window.qml"
    engine.load(qml_file)

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(controller.run_app())


if __name__ == "__main__":
    main()
