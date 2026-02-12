from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional

from PyQt5 import QtCore, QtWidgets


ValueKind = Literal["u16", "i16", "u32", "i32", "float", "ascii", "mac", "bool"]


@dataclass(frozen=True)
class EditorSpec:
    kind: ValueKind
    min_value: Optional[int] = None
    max_value: Optional[int] = None
    decimals: int = 0
    step: float = 1.0
    choices: Optional[list[tuple[str, int]]] = None
    placeholder: str = ""


def create_editor(parent: QtWidgets.QWidget, spec: EditorSpec) -> QtWidgets.QWidget:
    if spec.kind == "bool":
        cb = QtWidgets.QComboBox(parent)
        cb.addItem("False", 0)
        cb.addItem("True", 1)
        return cb

    if spec.kind in ("u16", "i16"):
        sp = QtWidgets.QSpinBox(parent)
        if spec.kind == "u16":
            sp.setRange(0, 0xFFFF)
        else:
            sp.setRange(-0x8000, 0x7FFF)
        if spec.min_value is not None or spec.max_value is not None:
            sp.setRange(spec.min_value or sp.minimum(), spec.max_value or sp.maximum())
        sp.setSingleStep(int(spec.step) if spec.step else 1)
        return sp

    if spec.kind in ("u32", "i32"):
        sp = QtWidgets.QLineEdit(parent)
        sp.setPlaceholderText(spec.placeholder or "32-bit number")
        return sp

    if spec.kind == "float":
        dsp = QtWidgets.QDoubleSpinBox(parent)
        dsp.setDecimals(int(spec.decimals) if spec.decimals else 3)
        dsp.setRange(-1e12, 1e12)
        dsp.setSingleStep(float(spec.step) if spec.step else 0.1)
        return dsp

    if spec.kind == "mac":
        le = QtWidgets.QLineEdit(parent)
        le.setPlaceholderText(spec.placeholder or "AA:BB:CC:DD:EE:FF")
        return le

    if spec.kind == "ascii":
        le = QtWidgets.QLineEdit(parent)
        le.setPlaceholderText(spec.placeholder or "ASCII")
        return le

    # default
    return QtWidgets.QLineEdit(parent)


def editor_get_value(widget: QtWidgets.QWidget, spec: EditorSpec) -> str:
    # Always return text; caller decides how to encode.
    if isinstance(widget, QtWidgets.QComboBox):
        return str(int(widget.currentData()))
    if isinstance(widget, QtWidgets.QSpinBox):
        return str(int(widget.value()))
    if isinstance(widget, QtWidgets.QDoubleSpinBox):
        return str(float(widget.value()))
    if isinstance(widget, QtWidgets.QLineEdit):
        return widget.text().strip()
    return ""


def editor_set_value(widget: QtWidgets.QWidget, spec: EditorSpec, value_text: str) -> None:
    t = (value_text or "").strip()
    if isinstance(widget, QtWidgets.QComboBox):
        try:
            v = int(t, 10)
        except Exception:
            v = 0
        idx = widget.findData(v)
        if idx >= 0:
            widget.setCurrentIndex(idx)
        return
    if isinstance(widget, QtWidgets.QSpinBox):
        try:
            widget.setValue(int(float(t)))
        except Exception:
            pass
        return
    if isinstance(widget, QtWidgets.QDoubleSpinBox):
        try:
            widget.setValue(float(t))
        except Exception:
            pass
        return
    if isinstance(widget, QtWidgets.QLineEdit):
        widget.setText(t)
        return

