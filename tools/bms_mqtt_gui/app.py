from __future__ import annotations

import os
import sys

from PyQt5 import QtWidgets

# Allow running via: python tools/bms_mqtt_gui/app.py
_PKG_DIR = os.path.dirname(os.path.abspath(__file__))
_TOOLS_DIR = os.path.dirname(_PKG_DIR)
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)

from bms_mqtt_gui.main_window import MainWindow  # noqa: E402


def main() -> int:
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())
