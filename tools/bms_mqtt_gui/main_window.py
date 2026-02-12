from __future__ import annotations

import datetime as _dt
import os
from dataclasses import asdict
from typing import Optional

from PyQt5 import QtCore, QtGui, QtWidgets

from . import protocol
from .config_dialog import ConfigDialog
from .config_models import ProtoConfig
from .mqtt_worker import MqttConfig, MqttWorker
from .register_loader import load_register_defs_from_basic_md, load_register_defs_from_socket_md
from .register_meta import build_register_meta
from .profiles import load_profiles
from .typed_editors import EditorSpec, create_editor, editor_get_value, editor_set_value
from .socket_payload import bytes_to_hex_upper, encode_socket_payload
from .persistence import (
    load_mqtt_config,
    load_proto_config,
    load_ui_state,
    save_mqtt_config,
    save_proto_config,
    save_ui_state,
)


def _ts() -> str:
    return _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("BMS Modbus over MQTT Simulator (PyQt5)")
        self.resize(1200, 720)

        self._updating_table = False
        self._pending_reads: dict[tuple[int, int], list[tuple[int, int]]] = {}  # (deviceAddr, func) -> [(start, qty)]

        self._register_meta: dict[int, object] = {}
        self._raw_regs: dict[int, int] = {}
        self._profiles = load_profiles("tools/bms_mqtt_gui/device_profiles")
        self._current_profile_id: str = ""

        # Runtime configs (edited via the "参数配置" dialog)
        default_mqtt = MqttConfig(
            host="127.0.0.1",
            port=1883,
            # Use a unique default; duplicate client_id will cause the broker to kick old connections.
            client_id=f"fjbms-bms-gui-{os.getpid()}",
            username="",
            password="",
            # Device publishes to tx, and subscribes rx for commands.
            subscribe_topic="device/socket/rx/{device_id}",
            publish_topic="device/socket/tx/{device_id}",
            qos=1,
        )
        self._mqtt_cfg, self._device_id, self._sub_topic_tpl, self._pub_topic_tpl = load_mqtt_config(default_mqtt)
        self._proto_cfg = load_proto_config(ProtoConfig())

        ui_state = load_ui_state()
        self._restore_geometry = ui_state.get("geometry")
        self._restore_window_state = ui_state.get("window_state")
        self._restore_profile_id = str(ui_state.get("profile_id") or "")
        self._restore_auto_respond = bool(ui_state.get("auto_respond") or False)

        self._build_ui()
        self._setup_mqtt_thread()

        # Restore window state after widgets are created.
        try:
            if isinstance(self._restore_geometry, QtCore.QByteArray):
                self.restoreGeometry(self._restore_geometry)
            if isinstance(self._restore_window_state, QtCore.QByteArray):
                self.restoreState(self._restore_window_state)
        except Exception:
            pass

    def _build_ui(self) -> None:
        self._build_menu()
        self._build_toolbar()

        cw = QtWidgets.QWidget()
        self.setCentralWidget(cw)

        root = QtWidgets.QHBoxLayout(cw)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(10)

        # Left / Right strict split: 60% / 40%
        self.left_frame = QtWidgets.QFrame()
        self.left_frame.setFrameShape(QtWidgets.QFrame.Box)
        self.left_frame.setFrameShadow(QtWidgets.QFrame.Plain)
        left_layout = QtWidgets.QVBoxLayout(self.left_frame)
        left_layout.setContentsMargins(10, 10, 10, 10)
        left_layout.setSpacing(10)

        self.right_frame = QtWidgets.QFrame()
        self.right_frame.setFrameShape(QtWidgets.QFrame.Box)
        self.right_frame.setFrameShadow(QtWidgets.QFrame.Plain)
        right_layout = QtWidgets.QVBoxLayout(self.right_frame)
        right_layout.setContentsMargins(10, 10, 10, 10)
        right_layout.setSpacing(10)

        root.addWidget(self.left_frame, 3)
        root.addWidget(self.right_frame, 2)

        # --- Left: Register table (only)
        reg_box = QtWidgets.QGroupBox("寄存器表格")
        reg_layout = QtWidgets.QVBoxLayout(reg_box)

        self.table = QtWidgets.QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["寄存器地址(Hex)", "寄存器数值", "描述"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked | QtWidgets.QAbstractItemView.SelectedClicked)
        self.table.itemChanged.connect(self._on_table_item_changed)
        reg_layout.addWidget(self.table)

        btns = QtWidgets.QHBoxLayout()
        self.btn_add = QtWidgets.QPushButton("新增寄存器")
        self.btn_del = QtWidgets.QPushButton("删除选中行")
        self.btn_clear = QtWidgets.QPushButton("清空表格")
        self.btn_read = QtWidgets.QPushButton("读取寄存器")
        self.btn_write = QtWidgets.QPushButton("写入寄存器")
        self.btn_report = QtWidgets.QPushButton("主动上报（选中地址）")

        for b in (self.btn_add, self.btn_del, self.btn_clear, self.btn_read, self.btn_write, self.btn_report):
            btns.addWidget(b)
        btns.addStretch(1)
        reg_layout.addLayout(btns)

        left_layout.addWidget(reg_box, 1)

        # --- Right: Log panel
        log_box = QtWidgets.QGroupBox("MQTT 交互日志")
        log_layout = QtWidgets.QVBoxLayout(log_box)

        self.log_edit = QtWidgets.QTextEdit()
        self.log_edit.setReadOnly(True)
        self.log_edit.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.log_scroll = self.log_edit.verticalScrollBar()  # explicit QScrollBar as required
        log_layout.addWidget(self.log_edit)

        right_layout.addWidget(log_box, 1)

        self.btn_add.clicked.connect(self._on_add_row)
        self.btn_del.clicked.connect(self._on_delete_selected_rows)
        self.btn_clear.clicked.connect(self._on_clear_table)
        self.btn_read.clicked.connect(self._on_read_selected)
        self.btn_write.clicked.connect(self._on_write_selected)
        self.btn_report.clicked.connect(self._on_report_selected)

        self._load_default_registers()

        self.statusBar().showMessage("MQTT: disconnected")

    def _fmt_addr(self, addr: int) -> str:
        # Prefer 4-hex-digit display, but keep width flexible for bigger values.
        if addr <= 0xFFFF:
            return f"0x{addr:04X}"
        return f"0x{addr:X}"

    def _parse_addr_cell(self, s: str) -> Optional[int]:
        t = (s or "").strip()
        if not t:
            return None
        try:
            if t.startswith(("0x", "0X")):
                return int(t, 16)
            # Allow plain hex (contains A-F) or decimal digits.
            if any(c in "abcdefABCDEF" for c in t):
                return int(t, 16)
            return int(t, 10)
        except Exception:
            return None

    def _build_menu(self) -> None:
        mb = self.menuBar()

        menu_cfg = mb.addMenu("参数配置")
        act_open_cfg = QtWidgets.QAction("打开配置...", self)
        act_open_cfg.triggered.connect(self._open_config_dialog)
        menu_cfg.addAction(act_open_cfg)

        act_load_regs = QtWidgets.QAction("从文档加载寄存器地址", self)
        act_load_regs.triggered.connect(lambda: self._load_default_registers(force=True))
        menu_cfg.addAction(act_load_regs)

        menu_cfg.addSeparator()
        self.act_auto_respond = QtWidgets.QAction("自动响应读/写请求（模拟从机）", self)
        self.act_auto_respond.setCheckable(True)
        self.act_auto_respond.setChecked(bool(getattr(self, "_restore_auto_respond", False)))
        menu_cfg.addAction(self.act_auto_respond)

        menu_mqtt = mb.addMenu("MQTT")
        self.act_connect = QtWidgets.QAction("连接", self)
        self.act_disconnect = QtWidgets.QAction("断开", self)
        self.act_disconnect.setEnabled(False)
        self.act_connect.triggered.connect(self._on_connect_clicked)
        self.act_disconnect.triggered.connect(self._on_disconnect_clicked)
        menu_mqtt.addAction(self.act_connect)
        menu_mqtt.addAction(self.act_disconnect)

    def _build_toolbar(self) -> None:
        tb = self.addToolBar("Main")
        tb.setMovable(False)

        act_cfg = QtWidgets.QAction("参数配置", self)
        act_cfg.triggered.connect(self._open_config_dialog)
        tb.addAction(act_cfg)

        tb.addSeparator()
        tb.addAction(self.act_connect)
        tb.addAction(self.act_disconnect)

        tb.addSeparator()
        tb.addWidget(QtWidgets.QLabel("设备模板:"))
        self.cb_profile = QtWidgets.QComboBox()
        self.cb_profile.setMinimumWidth(220)
        self.cb_profile.addItem("(选择模板加载寄存器)", "")
        for p in self._profiles:
            self.cb_profile.addItem(p.name, p.id)
        self.cb_profile.currentIndexChanged.connect(self._on_profile_changed)
        tb.addWidget(self.cb_profile)

        # Restore last profile selection.
        if getattr(self, "_restore_profile_id", ""):
            idx = self.cb_profile.findData(self._restore_profile_id)
            if idx >= 0:
                self.cb_profile.setCurrentIndex(idx)

    def _open_config_dialog(self) -> None:
        dlg = ConfigDialog(
            self,
            self._mqtt_cfg,
            self._proto_cfg,
            self._device_id,
            self._sub_topic_tpl,
            self._pub_topic_tpl,
        )
        if dlg.exec_() != QtWidgets.QDialog.Accepted:
            return
        self._mqtt_cfg = dlg.mqtt_config()
        self._proto_cfg = dlg.proto_config()
        self._device_id = dlg.device_id()
        self._sub_topic_tpl = dlg.sub_topic_tpl()
        self._pub_topic_tpl = dlg.pub_topic_tpl()

        # Persist to disk.
        save_mqtt_config(self._mqtt_cfg, self._device_id, self._sub_topic_tpl, self._pub_topic_tpl)
        save_proto_config(self._proto_cfg)

        QtCore.QMetaObject.invokeMethod(
            self._mqtt_worker,
            "set_crc_mode",
            QtCore.Qt.QueuedConnection,
            QtCore.Q_ARG(object, self._proto_cfg.crc_mode),
        )
        self._log("CONFIG", f"MQTT={self._mqtt_cfg.host}:{self._mqtt_cfg.port} sub={self._mqtt_cfg.subscribe_topic} pub={self._mqtt_cfg.publish_topic}")
        self._log(
            "CONFIG",
            f"PROTO host=0x{self._proto_cfg.host_address:02X} slave=0x{self._proto_cfg.slave_address:02X} read=0x{self._proto_cfg.read_function:02X} write=0x{self._proto_cfg.write_function:02X} report=0x{self._proto_cfg.report_function:02X} format={self._proto_cfg.report_format} crc={self._proto_cfg.crc_mode}",
        )

    def _setup_mqtt_thread(self) -> None:
        self._mqtt_thread = QtCore.QThread(self)
        self._mqtt_worker = MqttWorker()
        self._mqtt_worker.moveToThread(self._mqtt_thread)

        self._mqtt_worker.sig_log.connect(self._log_line)
        self._mqtt_worker.sig_connected.connect(self._on_mqtt_connected)
        self._mqtt_worker.sig_disconnected.connect(self._on_mqtt_disconnected)
        self._mqtt_worker.sig_subscribed.connect(lambda t: self._log("MQTT", f"订阅成功: {t}"))
        self._mqtt_worker.sig_frame.connect(self._on_mqtt_frame)

        self._mqtt_thread.start()
        QtCore.QMetaObject.invokeMethod(self._mqtt_worker, "set_crc_mode", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(object, self._proto_cfg.crc_mode))

    # ---------- Logging ----------
    def _log(self, category: str, msg: str) -> None:
        self._log_line(f"[{category}] {msg}")

    def _log_line(self, line: str) -> None:
        full = f"{_ts()} {line}"
        self.log_edit.append(full)
        # auto-scroll to bottom
        self.log_edit.moveCursor(QtGui.QTextCursor.End)
        self.log_edit.ensureCursorVisible()
        self.log_scroll.setValue(self.log_scroll.maximum())

    # ---------- MQTT connect/disconnect ----------
    def _on_connect_clicked(self) -> None:
        cfg = self._mqtt_cfg
        if not cfg.host:
            self._log("ERROR", "请先在【参数配置】中填写 MQTT 服务器 IP")
            return
        if "{device_id}" in (cfg.subscribe_topic + cfg.publish_topic):
            self._log("ERROR", "Topic 中包含 {device_id} 占位符，请在【参数配置】中填写设备ID或替换掉占位符")
            return
        if not cfg.subscribe_topic or not cfg.publish_topic:
            self._log("ERROR", "请先在【参数配置】中填写订阅/发布 Topic")
            return

        # Avoid using a shared default client_id; brokers will kick old connections.
        if cfg.client_id.strip() == "fjbms-bms-gui":
            cfg = MqttConfig(
                host=cfg.host,
                port=cfg.port,
                client_id=f"{cfg.client_id}-{os.getpid()}",
                username=cfg.username,
                password=cfg.password,
                subscribe_topic=cfg.subscribe_topic,
                publish_topic=cfg.publish_topic,
                qos=cfg.qos,
                keepalive=cfg.keepalive,
            )
            self._mqtt_cfg = cfg
            self._log("MQTT", f"client_id 自动修正为唯一值: {cfg.client_id}")

        self.act_connect.setEnabled(False)
        self.act_disconnect.setEnabled(True)
        self.statusBar().showMessage("MQTT: connecting...")
        QtCore.QMetaObject.invokeMethod(self._mqtt_worker, "connect_mqtt", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(object, asdict(cfg)))

    def _on_disconnect_clicked(self) -> None:
        QtCore.QMetaObject.invokeMethod(self._mqtt_worker, "disconnect_mqtt", QtCore.Qt.QueuedConnection)

    def _on_mqtt_connected(self) -> None:
        self._log("MQTT", "连接成功")
        self.act_connect.setEnabled(False)
        self.act_disconnect.setEnabled(True)
        self.statusBar().showMessage(f"MQTT: connected ({self._mqtt_cfg.host}:{self._mqtt_cfg.port})")

    def _on_mqtt_disconnected(self) -> None:
        self._log("MQTT", "连接已断开")
        self.act_connect.setEnabled(True)
        self.act_disconnect.setEnabled(False)
        self.statusBar().showMessage("MQTT: disconnected")

    def _publish_frame_bytes(self, frame_bytes: bytes, note: str) -> None:
        cfg = self._mqtt_cfg
        hex_str = bytes_to_hex_upper(frame_bytes)
        payload = encode_socket_payload(hex_str)
        self._log("MQTT", f"发布: topic={cfg.publish_topic} {note} hex={hex_str}")
        QtCore.QMetaObject.invokeMethod(
            self._mqtt_worker,
            "publish",
            QtCore.Qt.QueuedConnection,
            QtCore.Q_ARG(str, cfg.publish_topic),
            QtCore.Q_ARG(object, payload),
            QtCore.Q_ARG(int, 1),
        )

    # ---------- Table helpers ----------
    def _selected_addresses(self) -> list[int]:
        addrs: list[int] = []
        for idx in self.table.selectionModel().selectedRows():
            r = idx.row()
            it = self.table.item(r, 0)
            if it is None:
                continue
            v = self._parse_addr_cell(it.text() or "")
            if v is None:
                continue
            addrs.append(int(v))
        return sorted(set(addrs))

    def _row_for_address(self, addr: int) -> Optional[int]:
        for r in range(self.table.rowCount()):
            it = self.table.item(r, 0)
            if not it:
                continue
            v = self._parse_addr_cell(it.text() or "")
            if v is not None and int(v) == int(addr):
                return int(r)
        return None

    def _get_value_as_u16(self, addr: int) -> int:
        # Source of truth for protocol frames.
        if int(addr) in self._raw_regs:
            return int(self._raw_regs[int(addr)]) & 0xFFFF
        return 0xFFFF

    def _set_value_u16(self, addr: int, v: int) -> None:
        self._updating_table = True
        try:
            self._raw_regs[int(addr)] = int(v) & 0xFFFF
            r = self._row_for_address(addr)
            if r is None:
                r = self.table.rowCount()
                self.table.insertRow(r)
                self.table.setItem(r, 0, QtWidgets.QTableWidgetItem(self._fmt_addr(int(addr))))
                self._ensure_value_editor(r, int(addr))
                self._render_field_to_row(int(addr))
                self.table.setItem(r, 2, QtWidgets.QTableWidgetItem(""))
            else:
                self._ensure_value_editor(r, int(addr))
                self._render_field_to_row(int(addr))
        finally:
            self._updating_table = False

    def _ensure_value_editor(self, row: int, addr: int) -> None:
        # Create a typed editor for the value cell, based on register meta.
        if self.table.cellWidget(row, 1) is not None:
            return
        m = self._register_meta.get(int(addr))
        if m is not None and int(getattr(m, "field_index", 0)) != 0:
            # Non-leading word of a multi-register field: show raw word, read-only.
            le = QtWidgets.QLineEdit(self.table)
            le.setReadOnly(True)
            le.setEnabled(False)
            self.table.setCellWidget(row, 1, le)
            return

        spec = getattr(m, "editor", None) if m is not None else None
        if not isinstance(spec, EditorSpec):
            spec = EditorSpec(kind="u16")
        w = create_editor(self.table, spec)
        self.table.setCellWidget(row, 1, w)

        # Bind change events so edits update raw registers.
        if isinstance(w, QtWidgets.QSpinBox):
            w.valueChanged.connect(lambda _=0, a=int(addr): self._on_value_widget_changed(a))
        elif isinstance(w, QtWidgets.QDoubleSpinBox):
            w.valueChanged.connect(lambda _=0.0, a=int(addr): self._on_value_widget_changed(a))
        elif isinstance(w, QtWidgets.QComboBox):
            w.currentIndexChanged.connect(lambda _=0, a=int(addr): self._on_value_widget_changed(a))
        elif isinstance(w, QtWidgets.QLineEdit):
            w.editingFinished.connect(lambda a=int(addr): self._on_value_widget_changed(a))

    def _set_cell_value_text(self, row: int, value_text: str) -> None:
        addr_it = self.table.item(row, 0)
        addr = self._parse_addr_cell(addr_it.text() if addr_it else "") or 0
        m = self._register_meta.get(int(addr))
        spec = getattr(m, "editor", None) if m is not None else None
        if not isinstance(spec, EditorSpec):
            spec = EditorSpec(kind="u16")
        w = self.table.cellWidget(row, 1)
        if w is not None:
            editor_set_value(w, spec, value_text)
        else:
            self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(value_text))

    def _on_value_widget_changed(self, addr: int) -> None:
        if self._updating_table:
            return
        m = self._register_meta.get(int(addr))
        if m is None:
            return
        row = self._row_for_address(addr)
        if row is None:
            return
        spec = getattr(m, "editor", EditorSpec(kind="u16"))
        w = self.table.cellWidget(row, 1)
        if w is None:
            return
        text = editor_get_value(w, spec)
        try:
            self._encode_field_from_text(int(addr), text)
        except Exception as e:
            self._log("ERROR", f"输入解析失败 addr={self._fmt_addr(int(addr))}: {e}")

    def _encode_field_from_text(self, addr: int, text: str) -> None:
        m = self._register_meta.get(int(addr))
        if m is None:
            return
        start = int(getattr(m, "field_start", addr))
        codec = getattr(m, "codec", None)
        if codec is None:
            self._raw_regs[int(addr)] = int(float(text)) & 0xFFFF
            self._render_field_to_row(int(addr))
            return

        kind = str(getattr(codec, "kind", "u16"))
        if kind == "u16":
            self._raw_regs[start] = int(float(text)) & 0xFFFF
        elif kind == "i16":
            v = int(float(text))
            self._raw_regs[start] = v & 0xFFFF
        elif kind in ("u32", "i32"):
            v = int(float(text)) & 0xFFFFFFFF
            self._raw_regs[start] = (v >> 16) & 0xFFFF
            self._raw_regs[start + 1] = v & 0xFFFF
        elif kind == "scaled_u16":
            scale = int(getattr(codec, "scale", 1) or 1)
            v = int(round(float(text) * float(scale)))
            self._raw_regs[start] = v & 0xFFFF
        elif kind == "scaled_i32":
            scale = int(getattr(codec, "scale", 1) or 1)
            v = int(round(float(text) * float(scale))) & 0xFFFFFFFF
            self._raw_regs[start] = (v >> 16) & 0xFFFF
            self._raw_regs[start + 1] = v & 0xFFFF
        elif kind == "ascii":
            self._encode_ascii(start, int(getattr(codec, "len_regs", 1)), text)
        elif kind == "mac":
            self._encode_mac(start, int(getattr(codec, "len_regs", 5)), text)

        field_len = int(getattr(m, "field_len_regs", 1))
        for i in range(field_len):
            self._render_field_to_row(start + i)

    def _encode_ascii(self, start: int, len_regs: int, text: str) -> None:
        byte_len = len_regs * 2
        bs = (text or "").encode("ascii", errors="ignore")[:byte_len]
        bs = bs + b"\x00" * (byte_len - len(bs))
        for i in range(0, byte_len, 2):
            self._raw_regs[start + (i // 2)] = ((bs[i] & 0xFF) << 8) | (bs[i + 1] & 0xFF)

    def _encode_mac(self, start: int, len_regs: int, mac: str) -> None:
        byte_len = len_regs * 2
        s = (mac or "").strip().replace("-", ":").upper()
        parts = [p for p in s.split(":") if p]
        mac_bytes: list[int] = []
        for p in parts[:byte_len]:
            try:
                mac_bytes.append(int(p, 16) & 0xFF)
            except Exception:
                pass
        while len(mac_bytes) < byte_len:
            mac_bytes.append(0)
        mac_bytes = mac_bytes[:byte_len]
        for i in range(0, byte_len, 2):
            self._raw_regs[start + (i // 2)] = ((mac_bytes[i] & 0xFF) << 8) | (mac_bytes[i + 1] & 0xFF)

    def _render_field_to_row(self, addr: int) -> None:
        m = self._register_meta.get(int(addr))
        if m is None:
            return
        start = int(getattr(m, "field_start", addr))
        codec = getattr(m, "codec", None)
        row = self._row_for_address(addr)
        if row is None:
            return
        # For non-leading words of multi-register fields, just show raw u16.
        if int(getattr(m, "field_index", 0)) != 0:
            v = self._raw_regs.get(int(addr), 0) & 0xFFFF
            self._set_cell_value_text(row, f"0x{v:04X}")
            return
        if codec is None:
            self._set_cell_value_text(row, str(self._raw_regs.get(int(addr), 0)))
            return
        kind = str(getattr(codec, "kind", "u16"))
        if kind == "ascii":
            text = self._decode_ascii(start, int(getattr(codec, "len_regs", 1)))
            self._set_cell_value_text(row, text)
            return
        if kind == "mac":
            text = self._decode_mac(start, int(getattr(codec, "len_regs", 5)))
            self._set_cell_value_text(row, text)
            return
        if kind in ("u32", "i32"):
            v = ((self._raw_regs.get(start, 0) & 0xFFFF) << 16) | (self._raw_regs.get(start + 1, 0) & 0xFFFF)
            self._set_cell_value_text(row, str(int(v)))
            return
        if kind == "scaled_u16":
            scale = int(getattr(codec, "scale", 1) or 1)
            v = self._raw_regs.get(start, 0) & 0xFFFF
            self._set_cell_value_text(row, str(float(v) / float(scale)))
            return
        if kind == "scaled_i32":
            scale = int(getattr(codec, "scale", 1) or 1)
            v = ((self._raw_regs.get(start, 0) & 0xFFFF) << 16) | (self._raw_regs.get(start + 1, 0) & 0xFFFF)
            if v & 0x80000000:
                v = -((~v + 1) & 0xFFFFFFFF)
            self._set_cell_value_text(row, str(float(v) / float(scale)))
            return
        v = self._raw_regs.get(int(addr), 0) & 0xFFFF
        if kind == "i16" and v & 0x8000:
            v = -((~v + 1) & 0xFFFF)
        self._set_cell_value_text(row, str(int(v)))

    def _decode_ascii(self, start: int, len_regs: int) -> str:
        bs = bytearray()
        for i in range(len_regs):
            v = self._raw_regs.get(start + i, 0) & 0xFFFF
            bs.append((v >> 8) & 0xFF)
            bs.append(v & 0xFF)
        raw = bytes(bs)
        if b"\x00" in raw:
            raw = raw.split(b"\x00", 1)[0]
        return raw.decode("ascii", errors="ignore")

    def _decode_mac(self, start: int, len_regs: int) -> str:
        bs: list[int] = []
        for i in range(len_regs):
            v = self._raw_regs.get(start + i, 0) & 0xFFFF
            bs.append((v >> 8) & 0xFF)
            bs.append(v & 0xFF)
        show = bs[:6]
        return ":".join(f"{b:02X}" for b in show)

    def _contiguous_groups(self, addrs: list[int]) -> list[list[int]]:
        if not addrs:
            return []
        groups: list[list[int]] = []
        cur: list[int] = [addrs[0]]
        for a in addrs[1:]:
            if a == cur[-1] + 1:
                cur.append(a)
            else:
                groups.append(cur)
                cur = [a]
        groups.append(cur)
        return groups

    # ---------- Table validation ----------
    def _on_table_item_changed(self, item: QtWidgets.QTableWidgetItem) -> None:
        if self._updating_table:
            return
        r, c = item.row(), item.column()
        txt = (item.text() or "").strip()

        def _mark_bad(msg: str) -> None:
            item.setBackground(QtGui.QColor("#FFDDDD"))
            self._log("VALIDATE", f"第 {r + 1} 行 {('地址' if c == 0 else '数值')} 非法: {msg}")

        item.setBackground(QtGui.QColor("white"))
        if c == 0:
            if txt == "":
                _mark_bad("不能为空")
                return
            v = self._parse_addr_cell(txt)
            if v is None:
                _mark_bad("必须是十进制或十六进制（如 0x0100）")
                return
            # normalize
            self._updating_table = True
            try:
                item.setText(self._fmt_addr(int(v)))
                # Ensure value editor is present for this address.
                self._ensure_value_editor(r, int(v))
            finally:
                self._updating_table = False
        # Value column is rendered as typed editor widgets.

    # ---------- Buttons ----------
    def _on_add_row(self) -> None:
        self._updating_table = True
        try:
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, QtWidgets.QTableWidgetItem(""))
            self.table.setItem(r, 1, QtWidgets.QTableWidgetItem(""))
            self.table.setItem(r, 2, QtWidgets.QTableWidgetItem(""))
        finally:
            self._updating_table = False

    def _on_delete_selected_rows(self) -> None:
        rows = sorted({i.row() for i in self.table.selectionModel().selectedRows()}, reverse=True)
        if not rows:
            return
        self._updating_table = True
        try:
            for r in rows:
                self.table.removeRow(r)
        finally:
            self._updating_table = False

    def _on_clear_table(self) -> None:
        self._updating_table = True
        try:
            self.table.setRowCount(0)
        finally:
            self._updating_table = False

    def _on_read_selected(self) -> None:
        addrs = self._selected_addresses()
        if not addrs:
            self._log("ERROR", "请先选中要读取的寄存器行（可多选）")
            return
        func = int(self._proto_cfg.read_function)
        host = int(self._proto_cfg.host_address)
        slave = int(self._proto_cfg.slave_address)
        crc_mode = self._proto_cfg.crc_mode

        for grp in self._contiguous_groups(addrs):
            start = grp[0]
            qty = len(grp)
            frame = protocol.build_read_request(host, slave, func, start, qty, crc_mode=crc_mode)
            self._pending_reads.setdefault((slave, func), []).append((start, qty))
            self._publish_frame_bytes(frame, note=f"READ start=0x{start:04X} qty={qty} func=0x{func:02X}")

    def _on_write_selected(self) -> None:
        addrs = self._selected_addresses()
        if not addrs:
            self._log("ERROR", "请先选中要写入的寄存器行（可多选）")
            return
        func = int(self._proto_cfg.write_function)
        host = int(self._proto_cfg.host_address)
        slave = int(self._proto_cfg.slave_address)
        crc_mode = self._proto_cfg.crc_mode

        for grp in self._contiguous_groups(addrs):
            start = grp[0]
            regs = [self._get_value_as_u16(a) for a in grp]
            frame = protocol.build_write_request(host, slave, func, start, regs, crc_mode=crc_mode)
            self._publish_frame_bytes(frame, note=f"WRITE start=0x{start:04X} qty={len(regs)} func=0x{func:02X}")

    def _on_report_selected(self) -> None:
        addrs = self._selected_addresses()
        if not addrs:
            self._log("ERROR", "请先选中要上报的寄存器地址（可多选）")
            return

        report_func = int(self._proto_cfg.report_function)
        host = int(self._proto_cfg.host_address)
        slave = int(self._proto_cfg.slave_address)
        crc_mode = self._proto_cfg.crc_mode
        report_format = str(self._proto_cfg.report_format)

        groups = self._contiguous_groups(addrs)
        for grp in groups:
            start = grp[0]
            regs = [self._get_value_as_u16(a) for a in grp]

            if report_format == "write":
                # Project backend supports this: write-request style carrying startAddress + data.
                frame = protocol.build_write_request(slave, host, report_func, start, regs, crc_mode=crc_mode)
                note = f"REPORT(write) start=0x{start:04X} qty={len(regs)} func=0x{report_func:02X}"
            elif report_format == "read_addr_qty":
                # Match doc/oriigin/device_comm_protocol_basic.md: data begins with start+qty then data.
                data = protocol.be_u16(start) + protocol.be_u16(len(regs)) + protocol.regs_to_be_bytes(regs)
                frame = protocol.build_read_response(slave, host, report_func, data, crc_mode=crc_mode)
                note = f"REPORT(read+addrQty) start=0x{start:04X} qty={len(regs)} func=0x{report_func:02X}"
            else:
                # read-only data; receiver must know start address by config.
                data = protocol.regs_to_be_bytes(regs)
                frame = protocol.build_read_response(slave, host, report_func, data, crc_mode=crc_mode)
                note = f"REPORT(read) qty={len(regs)} func=0x{report_func:02X}"

            self._publish_frame_bytes(frame, note=note)

    # ---------- MQTT frame handling ----------
    def _on_mqtt_frame(self, topic: str, parsed_obj: object, hex_str: str) -> None:
        parsed: protocol.ParsedFrame = parsed_obj  # emitted from worker
        self._log(
            "PROTO",
            f"解析成功: type={parsed.type} func=0x{parsed.function_code:02X} src=0x{parsed.source_address:02X} dst=0x{parsed.target_address:02X} crcMode={parsed.crc_mode_used}",
        )

        host = int(self._proto_cfg.host_address)
        slave = int(self._proto_cfg.slave_address)
        crc_mode = self._proto_cfg.crc_mode

        # Auto-respond mode: act as device (subscribe rx, publish tx).
        if self.act_auto_respond.isChecked():
            try:
                if parsed.type == "read_request" and parsed.start_address is not None and parsed.quantity is not None:
                    regs = [self._get_value_as_u16(parsed.start_address + i) for i in range(int(parsed.quantity))]
                    # 0x0F socket protocol: data starts with start+qty
                    if parsed.function_code == protocol.FUNC_CLOUD_SOCKET:
                        data = protocol.be_u16(int(parsed.start_address)) + protocol.be_u16(int(parsed.quantity)) + protocol.regs_to_be_bytes(regs)
                    else:
                        data = protocol.regs_to_be_bytes(regs)
                    resp = protocol.build_read_response(slave, host, parsed.function_code, data, crc_mode=crc_mode)
                    self._publish_frame_bytes(resp, note=f"AUTO-RESP READ qty={parsed.quantity}")
                elif parsed.type == "write_request" and parsed.start_address is not None and parsed.data is not None:
                    regs = protocol.split_regs_be(parsed.data)
                    for i, v in enumerate(regs):
                        self._set_value_u16(parsed.start_address + i, v)
                    resp = protocol.build_write_response(
                        slave, host, parsed.function_code, int(parsed.start_address), int(parsed.quantity or len(regs)), crc_mode=crc_mode
                    )
                    self._publish_frame_bytes(resp, note=f"AUTO-RESP WRITE qty={parsed.quantity or len(regs)}")
                return
            except Exception as e:
                self._log("ERROR", f"自动响应失败: {e}")
                return

        # Client mode: parse responses / reports and update table.
        try:
            report_func = int(self._proto_cfg.report_function)
            if parsed.type == "read_response" and parsed.data is not None:
                data = parsed.data
                # doc style report: data = start(2) + qty(2) + regs...
                if (
                    (parsed.function_code == report_func and str(self._proto_cfg.report_format) == "read_addr_qty")
                    or parsed.function_code == protocol.FUNC_CLOUD_SOCKET
                ) and len(data) >= 4:
                    start = (data[0] << 8) | data[1]
                    qty = (data[2] << 8) | data[3]
                    regs = protocol.split_regs_be(data[4:])
                    if qty and len(regs) != qty:
                        self._log("PROTO", f"上报数量不一致: declared={qty} actual={len(regs)}")
                    for i, v in enumerate(regs):
                        self._set_value_u16(start + i, v)
                    self._log("PROTO", f"回填上报(read+addrQty): start=0x{start:04X} qty={len(regs)}")
                    # clear one pending read if exists
                    key = (parsed.source_address, parsed.function_code)
                    pend = self._pending_reads.get(key) or []
                    if pend:
                        pend.pop(0)
                    return

                key = (parsed.source_address, parsed.function_code)
                pend = self._pending_reads.get(key) or []
                if pend:
                    start, qty = pend.pop(0)
                    regs = protocol.split_regs_be(data)
                    # In case receiver truncates or sends fewer regs; fill what we have.
                    for i in range(min(len(regs), qty)):
                        self._set_value_u16(start + i, regs[i])
                    self._log("PROTO", f"回填读取响应: start=0x{start:04X} qty={qty} got={len(regs)}")
                else:
                    self._log("PROTO", "收到 read_response，但没有匹配的 pending read（可能是上报/其它请求的响应）")

            elif parsed.type == "write_response":
                self._log(
                    "PROTO",
                    f"写入响应: start=0x{(parsed.start_address or 0):04X} qty={parsed.quantity}",
                )

            elif parsed.type == "write_request" and parsed.data is not None:
                # Treat write_request with report_func as report(write) update.
                if parsed.function_code == report_func and parsed.start_address is not None:
                    regs = protocol.split_regs_be(parsed.data)
                    for i, v in enumerate(regs):
                        self._set_value_u16(parsed.start_address + i, v)
                    self._log("PROTO", f"回填上报(write): start=0x{parsed.start_address:04X} qty={len(regs)}")
                else:
                    self._log("PROTO", f"收到 write_request（非上报/未开启自动响应），已忽略 func=0x{parsed.function_code:02X}")
            elif parsed.type == "error":
                self._log("PROTO", f"错误响应: func=0x{parsed.function_code:02X} err=0x{(parsed.error_code or 0):02X}")
        except Exception as e:
            self._log("ERROR", f"解析处理异常: {e}")

    def _load_default_registers(self, force: bool = False) -> None:
        if self.table.rowCount() > 0 and not force:
            return
        defs = load_register_defs_from_basic_md("doc/oriigin/device_comm_protocol_basic.md")
        defs += load_register_defs_from_socket_md("doc/oriigin/device_comm_protocol_socket.md")
        if not defs:
            self._log("DOC", "未从文档解析到寄存器地址（可手动添加）")
            return
        # de-dup by address, prefer first occurrence (basic.md)
        uniq: dict[int, object] = {}
        for d in defs:
            uniq.setdefault(int(d.address), d)

        self._register_meta = build_register_meta([uniq[a] for a in sorted(uniq.keys())])
        self._raw_regs = {int(addr): 0 for addr in uniq.keys()}
        self._updating_table = True
        try:
            self.table.setRowCount(0)
            for addr in sorted(uniq.keys()):
                r = self.table.rowCount()
                self.table.insertRow(r)
                self.table.setItem(r, 0, QtWidgets.QTableWidgetItem(self._fmt_addr(int(addr))))
                self._ensure_value_editor(r, int(addr))
                self._render_field_to_row(int(addr))
                self.table.setItem(r, 2, QtWidgets.QTableWidgetItem(getattr(uniq[addr], "desc", "")))
        finally:
            self._updating_table = False
        self._log("DOC", f"已从文档加载寄存器: {len(uniq)} 条")

    def _on_profile_changed(self) -> None:
        pid = str(self.cb_profile.currentData() or "")
        if not pid:
            return
        prof = None
        for p in self._profiles:
            if p.id == pid:
                prof = p
                break
        if prof is None:
            return
        self._apply_profile(prof.raw)
        self._current_profile_id = pid
        self._log("PROFILE", f"已加载设备模板: {prof.name}")

    def _apply_profile(self, raw: dict) -> None:
        # Ensure base registers loaded.
        self._load_default_registers(force=True)

        status = raw.get("status") if isinstance(raw, dict) else None
        cloud = raw.get("cloud_socket") if isinstance(raw, dict) else None
        if not isinstance(status, dict):
            status = {}
        if not isinstance(cloud, dict):
            cloud = {}

        # 0x100: H=S, L=N
        s = int(status.get("series_count_s") or 16)
        n = int(status.get("temp_count_n") or 4)
        self._set_value_u16(0x100, ((s & 0xFF) << 8) | (n & 0xFF))

        # Socket registers
        # 0x900 经度(4 bytes), 0x902 纬度(4 bytes)
        self._set_reg_i32_from_float(0x900, float(cloud.get("longitude") or 0.0), scale=100000)
        self._set_reg_i32_from_float(0x902, float(cloud.get("latitude") or 0.0), scale=100000)
        # 0x904 速度(2 bytes)
        self._set_value_u16(0x904, int(round(float(cloud.get("speed_kmh") or 0.0) * 1000)) & 0xFFFF)
        self._set_value_u16(0x905, int(cloud.get("altitude_m") or 0) & 0xFFFF)
        self._set_value_u16(0x906, int(cloud.get("rssi") or 0) & 0xFFFF)
        self._set_value_u16(0x907, int(cloud.get("tac") or 0) & 0xFFFF)
        self._set_reg_u32(0x908, int(cloud.get("cell_id") or 0))

        # IMEI/ICCID/module_sw_ver as ASCII fields
        self._set_ascii_field(0x90A, 18, str(cloud.get("imei") or ""))
        self._set_ascii_field(0x913, 22, str(cloud.get("iccid") or ""))
        self._set_ascii_field(0x91E, 12, str(cloud.get("module_sw_ver") or ""))

        # Dynamic status fields (best-effort, based on S/N)
        self._set_dynamic_status_fields(s, n, status)

    def _set_reg_i32_from_float(self, start: int, value: float, scale: int) -> None:
        v = int(round(value * float(scale)))
        self._set_reg_i32(start, v)

    def _set_reg_u32(self, start: int, value: int) -> None:
        v = int(value) & 0xFFFFFFFF
        hi = (v >> 16) & 0xFFFF
        lo = v & 0xFFFF
        self._set_value_u16(start, hi)
        self._set_value_u16(start + 1, lo)

    def _set_reg_i32(self, start: int, value: int) -> None:
        v = int(value) & 0xFFFFFFFF
        hi = (v >> 16) & 0xFFFF
        lo = v & 0xFFFF
        self._set_value_u16(start, hi)
        self._set_value_u16(start + 1, lo)

    def _set_ascii_field(self, start: int, byte_len: int, text: str) -> None:
        bs = (text or "").encode("ascii", errors="ignore")[:byte_len]
        bs = bs + b"\x00" * (byte_len - len(bs))
        for i in range(0, byte_len, 2):
            hi = bs[i]
            lo = bs[i + 1] if i + 1 < len(bs) else 0
            self._set_value_u16(start + (i // 2), ((hi & 0xFF) << 8) | (lo & 0xFF))

    def _set_dynamic_status_fields(self, s: int, n: int, status: dict) -> None:
        # The docs define a dynamic layout starting at 0x141.
        cell_voltages_start = 0x141
        cell_temps_start = cell_voltages_start + int(s)
        hw_model_start = cell_temps_start + int(n)
        battery_group_id_start = hw_model_start + 16
        board_code_start = battery_group_id_start + 16
        bt_mac_start = board_code_start + 16

        self._set_ascii_field(hw_model_start, 32, str(status.get("hardware_model") or ""))
        self._set_ascii_field(battery_group_id_start, 32, str(status.get("battery_group_id") or ""))
        self._set_ascii_field(board_code_start, 32, str(status.get("board_code") or ""))
        self._set_mac_field(bt_mac_start, str(status.get("bluetooth_mac") or ""))

    def _set_mac_field(self, start: int, mac: str) -> None:
        # Store 10 bytes (5 regs). Usually first 6 bytes are meaningful.
        s = (mac or "").strip().replace("-", ":").upper()
        parts = [p for p in s.split(":") if p]
        mac_bytes: list[int] = []
        for p in parts[:6]:
            try:
                mac_bytes.append(int(p, 16) & 0xFF)
            except Exception:
                pass
        while len(mac_bytes) < 10:
            mac_bytes.append(0)
        mac_bytes = mac_bytes[:10]
        for i in range(0, 10, 2):
            self._set_value_u16(start + (i // 2), ((mac_bytes[i] & 0xFF) << 8) | (mac_bytes[i + 1] & 0xFF))

    # ---------- Cleanup ----------
    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        try:
            # Persist UI state.
            save_ui_state(
                auto_respond=bool(self.act_auto_respond.isChecked()),
                profile_id=str(self.cb_profile.currentData() or ""),
                geometry=self.saveGeometry(),
                window_state=self.saveState(),
            )
            # Ensure the MQTT loop thread is stopped before quitting the QThread.
            QtCore.QMetaObject.invokeMethod(self._mqtt_worker, "disconnect_mqtt", QtCore.Qt.BlockingQueuedConnection)
            self._mqtt_thread.quit()
            self._mqtt_thread.wait(1500)
        except Exception:
            pass
        event.accept()
