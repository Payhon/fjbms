from __future__ import annotations

from PyQt5 import QtCore, QtWidgets

from . import protocol
from .config_models import ProtoConfig
from .mqtt_worker import MqttConfig


class ConfigDialog(QtWidgets.QDialog):
    def __init__(self, parent: QtWidgets.QWidget | None, mqtt_cfg: MqttConfig, proto_cfg: ProtoConfig) -> None:
        super().__init__(parent)
        self.setWindowTitle("参数配置")
        self.setModal(True)
        self.resize(720, 520)

        self._mqtt_cfg = mqtt_cfg
        self._proto_cfg = proto_cfg

        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        tabs = QtWidgets.QTabWidget()
        root.addWidget(tabs, 1)

        # ---- MQTT tab
        tab_mqtt = QtWidgets.QWidget()
        tabs.addTab(tab_mqtt, "MQTT 配置")
        form_mqtt = QtWidgets.QFormLayout(tab_mqtt)
        form_mqtt.setLabelAlignment(QtCore.Qt.AlignRight)

        self.ed_host = QtWidgets.QLineEdit(mqtt_cfg.host)
        self.sp_port = QtWidgets.QSpinBox()
        self.sp_port.setRange(1, 65535)
        self.sp_port.setValue(int(mqtt_cfg.port))

        self.ed_client_id = QtWidgets.QLineEdit(mqtt_cfg.client_id)
        self.ed_device_id = QtWidgets.QLineEdit("")
        self.ed_device_id.setPlaceholderText("用于替换 topic 中的 {device_id}（可为空）")

        self.ed_user = QtWidgets.QLineEdit(mqtt_cfg.username)
        self.ed_pass = QtWidgets.QLineEdit(mqtt_cfg.password)
        self.ed_pass.setEchoMode(QtWidgets.QLineEdit.Password)

        self.ed_sub_topic = QtWidgets.QLineEdit(mqtt_cfg.subscribe_topic or "device/socket/tx/{device_id}")
        self.ed_pub_topic = QtWidgets.QLineEdit(mqtt_cfg.publish_topic or "device/socket/rx/{device_id}")

        self.sp_qos = QtWidgets.QSpinBox()
        self.sp_qos.setRange(0, 2)
        self.sp_qos.setValue(int(mqtt_cfg.qos))

        form_mqtt.addRow("服务器 IP", self.ed_host)
        form_mqtt.addRow("端口", self.sp_port)
        form_mqtt.addRow("客户端 ID", self.ed_client_id)
        form_mqtt.addRow("设备ID", self.ed_device_id)
        form_mqtt.addRow("用户名", self.ed_user)
        form_mqtt.addRow("密码", self.ed_pass)
        form_mqtt.addRow("订阅 Topic", self.ed_sub_topic)
        form_mqtt.addRow("发布 Topic", self.ed_pub_topic)
        form_mqtt.addRow("QoS", self.sp_qos)

        # ---- Protocol tab
        tab_proto = QtWidgets.QWidget()
        tabs.addTab(tab_proto, "协议参数")
        form_proto = QtWidgets.QFormLayout(tab_proto)
        form_proto.setLabelAlignment(QtCore.Qt.AlignRight)

        self.sp_host_addr = QtWidgets.QSpinBox()
        self.sp_host_addr.setRange(0, 255)
        self.sp_host_addr.setDisplayIntegerBase(16)
        self.sp_host_addr.setPrefix("0x")
        self.sp_host_addr.setValue(int(proto_cfg.host_address))

        self.sp_slave_addr = QtWidgets.QSpinBox()
        self.sp_slave_addr.setRange(0, 255)
        self.sp_slave_addr.setDisplayIntegerBase(16)
        self.sp_slave_addr.setPrefix("0x")
        self.sp_slave_addr.setValue(int(proto_cfg.slave_address))

        self.cb_read_func = QtWidgets.QComboBox()
        self.cb_read_func.addItem("保持寄存器 0x03", protocol.FUNC_READ_HOLDING)
        self.cb_read_func.addItem("输入寄存器 0x04", protocol.FUNC_READ_INPUT)
        # set current
        idx = self.cb_read_func.findData(int(proto_cfg.read_function))
        if idx >= 0:
            self.cb_read_func.setCurrentIndex(idx)

        self.sp_write_func = QtWidgets.QSpinBox()
        self.sp_write_func.setRange(0, 255)
        self.sp_write_func.setDisplayIntegerBase(16)
        self.sp_write_func.setPrefix("0x")
        self.sp_write_func.setValue(int(proto_cfg.write_function))

        self.sp_report_func = QtWidgets.QSpinBox()
        self.sp_report_func.setRange(0, 255)
        self.sp_report_func.setDisplayIntegerBase(16)
        self.sp_report_func.setPrefix("0x")
        self.sp_report_func.setValue(int(proto_cfg.report_function))

        self.cb_report_format = QtWidgets.QComboBox()
        self.cb_report_format.addItem("write（帧字段带 start+qty）", "write")
        self.cb_report_format.addItem("read（仅数据，不含 start）", "read")
        self.cb_report_format.addItem("read+addrQty（按文档：data 前 4 字节=start+qty）", "read_addr_qty")
        idx = self.cb_report_format.findData(str(proto_cfg.report_format))
        if idx >= 0:
            self.cb_report_format.setCurrentIndex(idx)

        self.cb_crc_mode = QtWidgets.QComboBox()
        self.cb_crc_mode.addItem("CRC 从 source address 开始（兼容后端）", "source")
        self.cb_crc_mode.addItem("CRC 从 target address 开始（按文档）", "target")
        idx = self.cb_crc_mode.findData(str(proto_cfg.crc_mode))
        if idx >= 0:
            self.cb_crc_mode.setCurrentIndex(idx)

        form_proto.addRow("主机地址", self.sp_host_addr)
        form_proto.addRow("从机地址", self.sp_slave_addr)
        form_proto.addRow("读功能码", self.cb_read_func)
        form_proto.addRow("写功能码", self.sp_write_func)
        form_proto.addRow("上报功能码", self.sp_report_func)
        form_proto.addRow("上报格式", self.cb_report_format)
        form_proto.addRow("CRC 范围", self.cb_crc_mode)

        # ---- Buttons
        btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        btns.accepted.connect(self._on_accept)
        btns.rejected.connect(self.reject)
        root.addWidget(btns, 0)

    def mqtt_config(self) -> MqttConfig:
        return self._mqtt_cfg

    def proto_config(self) -> ProtoConfig:
        return self._proto_cfg

    def _on_accept(self) -> None:
        host = self.ed_host.text().strip()
        if not host:
            QtWidgets.QMessageBox.warning(self, "参数错误", "MQTT 服务器 IP 不能为空")
            return

        device_id = self.ed_device_id.text().strip()
        sub_topic = self.ed_sub_topic.text().strip()
        pub_topic = self.ed_pub_topic.text().strip()
        if "{device_id}" in (sub_topic + pub_topic) and not device_id:
            QtWidgets.QMessageBox.warning(self, "参数错误", "Topic 中包含 {device_id} 占位符，但设备ID为空")
            return
        if device_id:
            sub_topic = sub_topic.replace("{device_id}", device_id)
            pub_topic = pub_topic.replace("{device_id}", device_id)

        if not sub_topic:
            QtWidgets.QMessageBox.warning(self, "参数错误", "订阅 Topic 不能为空")
            return
        if not pub_topic:
            QtWidgets.QMessageBox.warning(self, "参数错误", "发布 Topic 不能为空")
            return

        self._mqtt_cfg = MqttConfig(
            host=host,
            port=int(self.sp_port.value()),
            client_id=self.ed_client_id.text().strip() or "fjbms-bms-gui",
            username=self.ed_user.text(),
            password=self.ed_pass.text(),
            subscribe_topic=sub_topic,
            publish_topic=pub_topic,
            qos=int(self.sp_qos.value()),
        )

        crc_mode: protocol.CRCMode = "target" if self.cb_crc_mode.currentData() == "target" else "source"
        self._proto_cfg = ProtoConfig(
            host_address=int(self.sp_host_addr.value()),
            slave_address=int(self.sp_slave_addr.value()),
            read_function=int(self.cb_read_func.currentData()),
            write_function=int(self.sp_write_func.value()),
            report_function=int(self.sp_report_func.value()),
            report_format=str(self.cb_report_format.currentData()),
            crc_mode=crc_mode,
        )

        self.accept()
