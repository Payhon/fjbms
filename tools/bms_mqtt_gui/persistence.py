from __future__ import annotations

from dataclasses import asdict

from PyQt5 import QtCore

from .config_models import ProtoConfig
from .mqtt_worker import MqttConfig


ORG_NAME = "FJBMS"
APP_NAME = "BMS_MQTT_GUI"


def _s() -> QtCore.QSettings:
    return QtCore.QSettings(ORG_NAME, APP_NAME)


def load_mqtt_config(default_cfg: MqttConfig) -> tuple[MqttConfig, str, str, str]:
    s = _s()
    device_id = str(s.value("mqtt/device_id", "", type=str) or "")
    sub_tpl = str(s.value("mqtt/sub_topic_tpl", default_cfg.subscribe_topic, type=str) or default_cfg.subscribe_topic)
    pub_tpl = str(s.value("mqtt/pub_topic_tpl", default_cfg.publish_topic, type=str) or default_cfg.publish_topic)

    cfg = MqttConfig(
        host=str(s.value("mqtt/host", default_cfg.host, type=str) or default_cfg.host),
        port=int(s.value("mqtt/port", default_cfg.port, type=int) or default_cfg.port),
        client_id=str(s.value("mqtt/client_id", default_cfg.client_id, type=str) or default_cfg.client_id),
        username=str(s.value("mqtt/username", default_cfg.username, type=str) or default_cfg.username),
        password=str(s.value("mqtt/password", default_cfg.password, type=str) or default_cfg.password),
        subscribe_topic=str(s.value("mqtt/subscribe_topic", default_cfg.subscribe_topic, type=str) or default_cfg.subscribe_topic),
        publish_topic=str(s.value("mqtt/publish_topic", default_cfg.publish_topic, type=str) or default_cfg.publish_topic),
        qos=int(s.value("mqtt/qos", default_cfg.qos, type=int) or default_cfg.qos),
        keepalive=int(s.value("mqtt/keepalive", default_cfg.keepalive, type=int) or default_cfg.keepalive),
    )
    return cfg, device_id, sub_tpl, pub_tpl


def save_mqtt_config(cfg: MqttConfig, device_id: str, sub_tpl: str, pub_tpl: str) -> None:
    s = _s()
    s.setValue("mqtt/host", cfg.host)
    s.setValue("mqtt/port", int(cfg.port))
    s.setValue("mqtt/client_id", cfg.client_id)
    s.setValue("mqtt/username", cfg.username)
    s.setValue("mqtt/password", cfg.password)
    s.setValue("mqtt/subscribe_topic", cfg.subscribe_topic)
    s.setValue("mqtt/publish_topic", cfg.publish_topic)
    s.setValue("mqtt/qos", int(cfg.qos))
    s.setValue("mqtt/keepalive", int(cfg.keepalive))
    s.setValue("mqtt/device_id", device_id)
    s.setValue("mqtt/sub_topic_tpl", sub_tpl)
    s.setValue("mqtt/pub_topic_tpl", pub_tpl)


def load_proto_config(default_cfg: ProtoConfig) -> ProtoConfig:
    s = _s()
    crc_mode = str(s.value("proto/crc_mode", default_cfg.crc_mode, type=str) or default_cfg.crc_mode)
    return ProtoConfig(
        host_address=int(s.value("proto/host_address", default_cfg.host_address, type=int) or default_cfg.host_address),
        slave_address=int(s.value("proto/slave_address", default_cfg.slave_address, type=int) or default_cfg.slave_address),
        read_function=int(s.value("proto/read_function", default_cfg.read_function, type=int) or default_cfg.read_function),
        write_function=int(s.value("proto/write_function", default_cfg.write_function, type=int) or default_cfg.write_function),
        report_function=int(s.value("proto/report_function", default_cfg.report_function, type=int) or default_cfg.report_function),
        report_format=str(s.value("proto/report_format", default_cfg.report_format, type=str) or default_cfg.report_format),
        crc_mode="target" if crc_mode == "target" else "source",
    )


def save_proto_config(cfg: ProtoConfig) -> None:
    s = _s()
    s.setValue("proto/host_address", int(cfg.host_address))
    s.setValue("proto/slave_address", int(cfg.slave_address))
    s.setValue("proto/read_function", int(cfg.read_function))
    s.setValue("proto/write_function", int(cfg.write_function))
    s.setValue("proto/report_function", int(cfg.report_function))
    s.setValue("proto/report_format", str(cfg.report_format))
    s.setValue("proto/crc_mode", str(cfg.crc_mode))


def load_ui_state() -> dict[str, object]:
    s = _s()
    return {
        "auto_respond": bool(s.value("ui/auto_respond", False, type=bool)),
        "profile_id": str(s.value("ui/profile_id", "", type=str) or ""),
        "geometry": s.value("ui/geometry", None),
        "window_state": s.value("ui/window_state", None),
    }


def save_ui_state(*, auto_respond: bool, profile_id: str, geometry: QtCore.QByteArray, window_state: QtCore.QByteArray) -> None:
    s = _s()
    s.setValue("ui/auto_respond", bool(auto_respond))
    s.setValue("ui/profile_id", str(profile_id or ""))
    s.setValue("ui/geometry", geometry)
    s.setValue("ui/window_state", window_state)

