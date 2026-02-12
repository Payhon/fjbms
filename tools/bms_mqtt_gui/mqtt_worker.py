from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Optional

import paho.mqtt.client as mqtt
from PyQt5 import QtCore

from . import protocol
from .socket_payload import decode_socket_payload, hex_to_bytes


@dataclass(frozen=True)
class MqttConfig:
    host: str
    port: int
    client_id: str
    username: str
    password: str
    subscribe_topic: str
    publish_topic: str
    qos: int = 1
    keepalive: int = 30


class MqttWorker(QtCore.QObject):
    sig_log = QtCore.pyqtSignal(str)  # already timestamped by UI
    sig_connected = QtCore.pyqtSignal()
    sig_disconnected = QtCore.pyqtSignal()
    sig_subscribed = QtCore.pyqtSignal(str)
    sig_frame = QtCore.pyqtSignal(str, object, str)  # topic, ParsedFrame, hex_str

    def __init__(self) -> None:
        super().__init__()
        self._client: Optional[mqtt.Client] = None
        self._stop = threading.Event()
        self._cfg: Optional[MqttConfig] = None
        self._crc_mode: protocol.CRCMode = "source"

    def _disconnect_current(self) -> None:
        if self._client is None:
            return
        try:
            # Disconnect first so DISCONNECT is sent.
            self._client.disconnect()
        except Exception:
            pass
        try:
            # Stop background loop thread.
            self._client.loop_stop()
        except Exception:
            pass
        self._client = None

    @QtCore.pyqtSlot(object)
    def set_crc_mode(self, mode: str) -> None:
        self._crc_mode = "target" if str(mode).lower().strip() == "target" else "source"

    @QtCore.pyqtSlot(object)
    def connect_mqtt(self, cfg_obj: object) -> None:
        try:
            cfg = cfg_obj if isinstance(cfg_obj, MqttConfig) else MqttConfig(**dict(cfg_obj))  # type: ignore[arg-type]
        except Exception as e:
            self.sig_log.emit(f"[MQTT][ERROR] bad config: {e}")
            self.sig_disconnected.emit()
            return

        self._cfg = cfg
        self._stop.clear()

        # If a previous client exists, close it first.
        self._disconnect_current()

        try:
            client = mqtt.Client(client_id=cfg.client_id, clean_session=True)
            if cfg.username or cfg.password:
                client.username_pw_set(cfg.username, cfg.password)

            client.on_connect = self._on_connect
            client.on_disconnect = self._on_disconnect
            client.on_message = self._on_message
            # Backoff for reconnect attempts.
            try:
                client.reconnect_delay_set(min_delay=1, max_delay=30)
            except Exception:
                pass

            self._client = client
            self.sig_log.emit(f"[MQTT] connecting to {cfg.host}:{cfg.port} client_id={cfg.client_id!r}")
            client.connect_async(cfg.host, int(cfg.port), keepalive=int(cfg.keepalive))
            client.loop_start()
        except Exception as e:
            self.sig_log.emit(f"[MQTT][ERROR] connect failed: {e}")
            self._client = None
            self.sig_disconnected.emit()
            return

    @QtCore.pyqtSlot()
    def disconnect_mqtt(self) -> None:
        self._stop.set()
        self._disconnect_current()

    @QtCore.pyqtSlot(str, object, int)
    def publish(self, topic: str, payload_obj: object, qos: int = 1) -> None:
        if not topic:
            self.sig_log.emit("[MQTT][ERROR] publish topic is empty")
            return
        try:
            payload = bytes(payload_obj)  # type: ignore[arg-type]
        except Exception:
            payload = str(payload_obj).encode("utf-8")
        if self._client is None:
            self.sig_log.emit("[MQTT][ERROR] publish ignored: not connected")
            return
        try:
            self._client.publish(topic, payload, qos=int(qos), retain=False)
        except Exception as e:
            self.sig_log.emit(f"[MQTT][ERROR] publish failed: {e}")

    # paho callbacks (executed in this QThread because we call loop() here)
    def _on_connect(self, client: mqtt.Client, _userdata, _flags, rc: int) -> None:
        if rc != 0:
            self.sig_log.emit(f"[MQTT][ERROR] connected with rc={rc}")
            return
        self.sig_log.emit("[MQTT] connected")
        self.sig_connected.emit()
        if self._cfg and self._cfg.subscribe_topic:
            try:
                client.subscribe(self._cfg.subscribe_topic, qos=int(self._cfg.qos))
                self.sig_log.emit(f"[MQTT] subscribe ok: {self._cfg.subscribe_topic}")
                self.sig_subscribed.emit(self._cfg.subscribe_topic)
            except Exception as e:
                self.sig_log.emit(f"[MQTT][ERROR] subscribe failed: {e}")

    def _on_disconnect(self, _client: mqtt.Client, _userdata, rc: int) -> None:
        self.sig_log.emit(f"[MQTT] disconnected rc={rc}")
        self.sig_disconnected.emit()

        # Best-effort auto-reconnect for unexpected disconnects.
        if rc != 0 and not self._stop.is_set() and self._client is not None:
            try:
                self.sig_log.emit("[MQTT] attempting reconnect...")
                self._client.reconnect()
            except Exception as e:
                self.sig_log.emit(f"[MQTT][ERROR] reconnect failed: {e}")

    def _on_message(self, _client: mqtt.Client, _userdata, msg: mqtt.MQTTMessage) -> None:
        topic = msg.topic or ""
        payload = msg.payload or b""
        try:
            hex_str = decode_socket_payload(payload)
            frame_bytes = hex_to_bytes(hex_str)
            parsed = protocol.parse_frame(frame_bytes, crc_mode=self._crc_mode, allow_crc_fallback=True)
            self.sig_log.emit(
                f"[MQTT][RX] topic={topic} len={len(payload)} hexLen={len(hex_str)} frameLen={len(frame_bytes)} func=0x{parsed.function_code:02X} type={parsed.type}"
            )
            self.sig_frame.emit(topic, parsed, hex_str.upper())
        except Exception as e:
            # Always log raw (truncated) for troubleshooting.
            preview = payload[:200]
            self.sig_log.emit(f"[MQTT][RX][ERROR] topic={topic} parse failed: {e}; payloadPreview={preview!r}")
