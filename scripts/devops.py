#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
import tarfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import paramiko
import yaml
from tqdm import tqdm

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = Path(__file__).resolve().parent
CONFIG_DIR = SCRIPTS_DIR / "config"
OUTPUT_DIR = REPO_ROOT / "dist" / "devops"

QUIET = False


def _now_ts() -> str:
    return time.strftime("%Y%m%d_%H%M%S", time.localtime())


def _eprint(msg: str) -> None:
    print(msg, file=sys.stderr)


def _cprint(msg: str) -> None:
    if not QUIET:
        print(msg)


def _cprint_err(msg: str) -> None:
    if not QUIET:
        _eprint(msg)


def _truncate(text: str, limit: int = 4000) -> str:
    if len(text) <= limit:
        return text
    head = text[:limit]
    return head + f"\n... (truncated, total={len(text)} chars)"


def _remote_prefix(host: str, port: int) -> str:
    return f"[remote {host}:{port}]"


def _format_env_keys(env: Optional[Dict[str, str]]) -> str:
    if not env:
        return ""
    keys = ", ".join(sorted(env.keys()))
    return f"  # env: {keys}"


def _run_local(cmd: list[str], cwd: Path) -> None:
    proc = subprocess.run(cmd, cwd=str(cwd))
    if proc.returncode != 0:
        raise SystemExit(proc.returncode)


def _load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise SystemExit(f"Invalid config (expected mapping): {path}")
    return data


def _expand_path(p: str) -> str:
    return os.path.expanduser(os.path.expandvars(p))


def _require_file(path: Path, hint: str) -> None:
    if not path.exists():
        raise SystemExit(f"Missing file: {path}\n{hint}")


def _quote(cmd: str) -> str:
    # convenience for when config provides raw shell strings
    return cmd if cmd.strip() else ""


@dataclass(frozen=True)
class SSHConn:
    host: str
    port: int
    username: str
    key_path: Optional[str]
    password: Optional[str]
    connect_timeout_sec: int = 15
    allow_agent: bool = False
    look_for_keys: bool = False


class SSHClient:
    def __init__(self, conn: SSHConn, *, known_hosts: Optional[str] = None) -> None:
        self._conn = conn
        self._client = paramiko.SSHClient()
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if known_hosts:
            try:
                self._client.load_host_keys(_expand_path(known_hosts))
            except FileNotFoundError:
                pass
        else:
            try:
                self._client.load_system_host_keys()
            except Exception:
                pass
        self._sftp: Optional[paramiko.SFTPClient] = None

    def __enter__(self) -> "SSHClient":
        use_password_only = self._conn.password is not None
        key_filename = None
        passphrase = None
        if self._conn.key_path and not use_password_only:
            key_filename = _expand_path(self._conn.key_path)
            passphrase = os.environ.get("SSH_KEY_PASSPHRASE")

        self._client.connect(
            hostname=self._conn.host,
            port=self._conn.port,
            username=self._conn.username,
            password=self._conn.password,
            key_filename=key_filename,
            passphrase=passphrase,
            allow_agent=(False if use_password_only else self._conn.allow_agent),
            look_for_keys=(False if use_password_only else self._conn.look_for_keys),
            timeout=self._conn.connect_timeout_sec,
            banner_timeout=self._conn.connect_timeout_sec,
            auth_timeout=self._conn.connect_timeout_sec,
        )
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        try:
            if self._sftp is not None:
                self._sftp.close()
        finally:
            self._client.close()

    def sftp(self) -> paramiko.SFTPClient:
        if self._sftp is None:
            self._sftp = self._client.open_sftp()
        return self._sftp

    def exec(
        self,
        cmd: str,
        *,
        check: bool = True,
        get_pty: bool = False,
        env: Optional[Dict[str, str]] = None,
    ) -> Tuple[str, str, int]:
        env_prefix = ""
        if env:
            env_prefix = " ".join(f"{k}={shlex.quote(v)}" for k, v in env.items()) + " "
        full = env_prefix + cmd
        stdin, stdout, stderr = self._client.exec_command(full, get_pty=get_pty)
        out = stdout.read().decode("utf-8", errors="replace")
        err = stderr.read().decode("utf-8", errors="replace")
        code = stdout.channel.recv_exit_status()
        if check and code != 0:
            raise SystemExit(f"Remote command failed ({code}): {cmd}\n{err.strip()}")
        return out, err, code

    def run(
        self,
        cmd: str,
        *,
        check: bool = True,
        get_pty: bool = False,
        env: Optional[Dict[str, str]] = None,
        show_output: bool = True,
    ) -> Tuple[str, str, int]:
        prefix = _remote_prefix(self._conn.host, self._conn.port)
        _cprint(f"{prefix}$ {cmd}{_format_env_keys(env)}")
        out, err, code = self.exec(cmd, check=False, get_pty=get_pty, env=env)
        if show_output:
            if out.strip():
                _cprint(_truncate(out.rstrip()))
            if err.strip():
                _cprint_err(_truncate(err.rstrip()))
        if check and code != 0:
            raise SystemExit(f"Remote command failed ({code}): {cmd}\n{err.strip()}")
        if not show_output and code != 0:
            _cprint_err(f"{prefix} exit={code}")
        return out, err, code

    def upload_file(self, local_path: Path, remote_path: str, *, desc: str) -> None:
        st = local_path.stat()
        bar = tqdm(total=st.st_size, unit="B", unit_scale=True, desc=desc)

        def _cb(transferred: int, total: int) -> None:
            bar.total = total
            bar.n = transferred
            bar.refresh()

        self.sftp().put(str(local_path), remote_path, callback=_cb)
        bar.close()

    def stream_to_local_file(self, cmd: str, local_path: Path, *, desc: str, env: Dict[str, str]) -> None:
        prefix = _remote_prefix(self._conn.host, self._conn.port)
        _cprint(f"{prefix}$ {cmd}{_format_env_keys(env)}")
        transport = self._client.get_transport()
        if transport is None:
            raise SystemExit("SSH transport not available")
        channel = transport.open_session()
        env_prefix = " ".join(f"{k}={shlex.quote(v)}" for k, v in env.items()) + " "
        channel.exec_command(env_prefix + cmd)
        local_path.parent.mkdir(parents=True, exist_ok=True)
        bar = tqdm(unit="B", unit_scale=True, desc=desc)
        with local_path.open("wb") as f:
            while True:
                data = channel.recv(1024 * 64)
                if not data:
                    break
                f.write(data)
                bar.update(len(data))
        bar.close()
        code = channel.recv_exit_status()
        if code != 0:
            raise SystemExit(f"Remote streaming command failed ({code}): {cmd}")


def _cfg_for_env(env: str, config_path: Optional[str]) -> Dict[str, Any]:
    if config_path:
        p = Path(config_path)
        _require_file(p, "Pass --config /path/to/config.yml or create scripts/config/{test,prod}.yml")
        return _load_yaml(p)
    p = CONFIG_DIR / f"{env}.yml"
    _require_file(
        p,
        f"Create {p} by copying {CONFIG_DIR}/{env}.example.yml and filling in values.",
    )
    return _load_yaml(p)


def _ssh_from_cfg(cfg: Dict[str, Any]) -> Tuple[SSHConn, bool, str]:
    ssh_cfg = cfg.get("ssh") or {}
    if not isinstance(ssh_cfg, dict):
        raise SystemExit("Config error: ssh must be a mapping")
    host = str(ssh_cfg.get("host", "")).strip()
    if not host:
        raise SystemExit("Config error: ssh.host is required")
    port = int(ssh_cfg.get("port", 22))
    user = str(ssh_cfg.get("user", "")).strip()
    if not user:
        raise SystemExit("Config error: ssh.user is required")
    auth_mode = str(ssh_cfg.get("auth", "auto")).strip().lower()
    if auth_mode not in ("auto", "password", "key"):
        raise SystemExit("Config error: ssh.auth must be one of: auto | password | key")

    key_path = ssh_cfg.get("key_path")
    password = None
    # Prefer password_env; allow literal password for special cases (not recommended).
    if ssh_cfg.get("password") is not None:
        password = str(ssh_cfg.get("password"))
    password_env = ssh_cfg.get("password_env")
    if password_env:
        password = os.environ.get(str(password_env))
        if password is None:
            raise SystemExit(f"Missing env var for ssh.password_env: {password_env}")

    use_sudo = bool(ssh_cfg.get("use_sudo", False))
    # If logging in as root, sudo is unnecessary and may not exist.
    if user == "root":
        use_sudo = False
    known_hosts = str(ssh_cfg.get("known_hosts", "")).strip() or None
    allow_agent = bool(ssh_cfg.get("allow_agent", False))
    look_for_keys = bool(ssh_cfg.get("look_for_keys", False))

    if auth_mode == "password":
        if password is None:
            raise SystemExit("Config error: ssh.auth=password requires ssh.password_env (recommended) or ssh.password")
        key_path = None
        allow_agent = False
        look_for_keys = False
    elif auth_mode == "key":
        if not key_path:
            raise SystemExit("Config error: ssh.auth=key requires ssh.key_path")
        # keep allow_agent/look_for_keys from config (defaults false)
    else:
        # auto: if password exists, force password-only (no keys/agent) to avoid surprises.
        if password is not None:
            key_path = None
            allow_agent = False
            look_for_keys = False
        elif not key_path and not allow_agent and not look_for_keys:
            raise SystemExit(
                "Config error: ssh auth is not configured. Set ssh.password_env (password login) or ssh.key_path (key login)."
            )

    return (
        SSHConn(
            host=host,
            port=port,
            username=user,
            key_path=key_path,
            password=password,
            allow_agent=allow_agent,
            look_for_keys=look_for_keys,
        ),
        use_sudo,
        known_hosts or "",
    )


def _sudo_prefix(use_sudo: bool) -> str:
    return "sudo -n " if use_sudo else ""


def _exec_sh(ssh: SSHClient, use_sudo: bool, script: str, *, check: bool = True) -> Tuple[str, str, int]:
    """
    Execute a shell script on remote host.
    Use this for constructs like `if/then`, pipes, redirects, and compound commands.
    """
    prefix = "sudo -n " if use_sudo else ""
    return ssh.run(f"{prefix}bash -lc {shlex.quote(script)}", check=check)


def _tar_dir(src_dir: Path, out_path: Path) -> None:
    src_dir = src_dir.resolve()
    if not src_dir.is_dir():
        raise SystemExit(f"Expected directory: {src_dir}")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(out_path, "w:gz") as tf:
        tf.add(src_dir, arcname=".")


def _remote_replace_dir_from_tar(
    ssh: SSHClient,
    use_sudo: bool,
    *,
    remote_bundle: str,
    remote_dest_dir: str,
    remote_tmp_dir: str,
    remote_backup_dir: str,
    label: str,
    ts: str,
) -> None:
    """
    Backup remote_dest_dir (if exists), then replace it with content of remote_bundle.
    """
    backup_file = f"{remote_backup_dir.rstrip('/')}/{label}_{ts}.tar.gz"
    _exec_sh(
        ssh,
        use_sudo,
        f"if [ -d {shlex.quote(remote_dest_dir)} ]; then "
        f"tar -czf {shlex.quote(backup_file)} -C {shlex.quote(remote_dest_dir)} .; "
        f"fi",
        check=False,
    )

    extract_dir = f"{remote_tmp_dir.rstrip('/')}/{label}_extract_{ts}"
    new_dir = f"{remote_dest_dir}.__new__{ts}"
    old_dir = f"{remote_dest_dir}.__old__{ts}"
    _exec_sh(
        ssh,
        use_sudo,
        f"rm -rf {shlex.quote(extract_dir)} {shlex.quote(new_dir)} {shlex.quote(old_dir)} && "
        f"mkdir -p {shlex.quote(extract_dir)} {shlex.quote(new_dir)} && "
        f"tar -xzf {shlex.quote(remote_bundle)} -C {shlex.quote(extract_dir)} && "
        f"cp -a {shlex.quote(extract_dir)}/. {shlex.quote(new_dir)}/ && "
        f"if [ -d {shlex.quote(remote_dest_dir)} ]; then mv {shlex.quote(remote_dest_dir)} {shlex.quote(old_dir)}; fi && "
        f"mv {shlex.quote(new_dir)} {shlex.quote(remote_dest_dir)} && "
        f"rm -rf {shlex.quote(old_dir)} {shlex.quote(extract_dir)}",
    )


def _render_systemd_install_script(
    *,
    service_name: str,
    work_dir: str,
    exec_start: str,
    log_file: str,
    unit_path: str,
) -> str:
    return f"""#!/usr/bin/env bash
set -euo pipefail

SERVICE_NAME={shlex.quote(service_name)}
UNIT_PATH={shlex.quote(unit_path)}
WORK_DIR={shlex.quote(work_dir)}
LOG_FILE={shlex.quote(log_file)}

SUDO=""
if [ "$(id -u)" -ne 0 ]; then
  command -v sudo >/dev/null 2>&1 || {{ echo "sudo is required when not running as root" >&2; exit 1; }}
  SUDO="sudo -n"
fi

echo "[fjbms] Installing systemd unit: $UNIT_PATH"

$SUDO mkdir -p "$WORK_DIR"
$SUDO mkdir -p "$(dirname "$LOG_FILE")"

$SUDO tee "$UNIT_PATH" >/dev/null <<'UNIT'
[Unit]
Description=fjbms backend
After=network.target

[Service]
Type=simple
WorkingDirectory={work_dir}
ExecStart=/bin/bash -lc {shlex.quote(exec_start)}
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
UNIT

$SUDO systemctl daemon-reload
$SUDO systemctl enable "$SERVICE_NAME" >/dev/null 2>&1 || true
$SUDO systemctl restart "$SERVICE_NAME"
$SUDO systemctl status "$SERVICE_NAME" --no-pager

echo ""
echo "[fjbms] Commands:"
echo "  sudo systemctl status $SERVICE_NAME"
echo "  sudo systemctl restart $SERVICE_NAME"
echo "  sudo systemctl stop $SERVICE_NAME"
"""


def _backend_temp_stop(ssh: SSHClient, use_sudo: bool, *, pid_file: str, stop_timeout_sec: int) -> None:
    stop_inner = (
        f"if [ -f {shlex.quote(pid_file)} ]; then "
        f"pid=$(cat {shlex.quote(pid_file)} || true); "
        "echo \"pidfile found: " + shlex.quote(pid_file) + ", pid=$pid\"; "
        "if [ -n \"$pid\" ] && kill -0 \"$pid\" 2>/dev/null; then "
        "echo \"stopping pid $pid\"; "
        "kill \"$pid\" 2>/dev/null || true; "
        f"for i in $(seq 1 {stop_timeout_sec}); do "
        "sleep 1; "
        "kill -0 \"$pid\" 2>/dev/null || break; "
        "done; "
        "if kill -0 \"$pid\" 2>/dev/null; then "
        "echo \"pid $pid still alive, sending SIGKILL\"; "
        "kill -9 \"$pid\" 2>/dev/null || true; "
        "else echo \"pid $pid stopped\"; fi; "
        "else echo \"pid not running\"; fi; "
        f"rm -f {shlex.quote(pid_file)}; "
        "else echo \"pidfile not found\"; fi"
    )
    ssh.run(f"{_sudo_prefix(use_sudo)}bash -lc {shlex.quote(stop_inner)}", check=False)


def _backend_temp_start(
    ssh: SSHClient,
    use_sudo: bool,
    *,
    work_dir: str,
    binary_path: str,
    config_flag: str,
    config_path: str,
    log_file: str,
    pid_file: str,
) -> None:
    start_inner = (
        f"cd {shlex.quote(work_dir)} && "
        f"echo \"starting: {shlex.quote(binary_path)} {shlex.quote(config_flag)} {shlex.quote(config_path)}\" && "
        f"nohup {shlex.quote(binary_path)} {shlex.quote(config_flag)} {shlex.quote(config_path)} "
        f">> {shlex.quote(log_file)} 2>&1 & "
        f"pid=$!; echo \"started pid $pid (log: {shlex.quote(log_file)})\"; "
        f"echo $pid > {shlex.quote(pid_file)}"
    )
    ssh.run(f"{_sudo_prefix(use_sudo)}bash -lc {shlex.quote(start_inner)}")


def build_frontend(service_env: str) -> None:
    frontend_dir = REPO_ROOT / "frontend"
    script = "build" if service_env == "prod" else "build:test"
    _run_local(["pnpm", script], cwd=frontend_dir)


def build_backend(goos: str, goarch: str) -> Path:
    backend_dir = REPO_ROOT / "backend"
    out_dir = backend_dir / "bin"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "fjbms"

    env = os.environ.copy()
    env["GOOS"] = goos
    env["GOARCH"] = goarch
    env.setdefault("CGO_ENABLED", "0")

    proc = subprocess.run(
        ["go", "build", "-trimpath", "-ldflags", "-s -w", "-o", str(out_path), "."],
        cwd=str(backend_dir),
        env=env,
    )
    if proc.returncode != 0:
        raise SystemExit(proc.returncode)
    return out_path


def _remote_mkdir(ssh: SSHClient, use_sudo: bool, path: str) -> None:
    ssh.run(f"{_sudo_prefix(use_sudo)}mkdir -p {shlex.quote(path)}")


def deploy_frontend(cfg: Dict[str, Any], service_env: str, *, skip_build: bool) -> None:
    frontend_cfg = cfg.get("frontend") or {}
    if not isinstance(frontend_cfg, dict):
        raise SystemExit("Config error: frontend must be a mapping")

    remote_target_dir = str(frontend_cfg.get("remote_target_dir", "")).strip()
    remote_tmp_dir = str(frontend_cfg.get("remote_tmp_dir", "/tmp/fjbms-deploy")).strip()
    remote_backup_dir = str(frontend_cfg.get("backup_dir", "")).strip()
    if not remote_target_dir or not remote_backup_dir:
        raise SystemExit("Config error: frontend.remote_target_dir and frontend.backup_dir are required")

    ts = _now_ts()
    if not skip_build:
        build_frontend(service_env)
    dist_dir = REPO_ROOT / "frontend" / "dist"
    _require_file(dist_dir, "Frontend build output missing; did the build succeed?")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    bundle = OUTPUT_DIR / f"frontend_{service_env}_{ts}.tar.gz"
    with tarfile.open(bundle, "w:gz") as tf:
        tf.add(dist_dir, arcname=".")

    ssh_conn, use_sudo, known_hosts = _ssh_from_cfg(cfg)
    with SSHClient(ssh_conn, known_hosts=known_hosts or None) as ssh:
        # Upload uses SFTP as the SSH user (no sudo). Keep tmp dir user-writable.
        _remote_mkdir(ssh, False, remote_tmp_dir)
        _remote_mkdir(ssh, use_sudo, remote_backup_dir)

        # Backup current
        backup_file = f"{remote_backup_dir.rstrip('/')}/frontend_{ts}.tar.gz"
        _exec_sh(
            ssh,
            use_sudo,
            f"if [ -d {shlex.quote(remote_target_dir)} ]; then "
            f"tar -czf {shlex.quote(backup_file)} -C {shlex.quote(remote_target_dir)} .; "
            f"fi",
        )

        remote_bundle = f"{remote_tmp_dir.rstrip('/')}/{bundle.name}"
        ssh.upload_file(bundle, remote_bundle, desc="upload(frontend)")

        extract_dir = f"{remote_tmp_dir.rstrip('/')}/frontend_extract_{ts}"
        new_dir = f"{remote_target_dir}.__new__{ts}"
        old_dir = f"{remote_target_dir}.__old__{ts}"

        ssh.run(f"{_sudo_prefix(use_sudo)}rm -rf {shlex.quote(extract_dir)} {shlex.quote(new_dir)} {shlex.quote(old_dir)}")
        ssh.run(f"{_sudo_prefix(use_sudo)}mkdir -p {shlex.quote(extract_dir)} {shlex.quote(new_dir)}")
        ssh.run(f"{_sudo_prefix(use_sudo)}tar -xzf {shlex.quote(remote_bundle)} -C {shlex.quote(extract_dir)}")
        ssh.run(f"{_sudo_prefix(use_sudo)}cp -a {shlex.quote(extract_dir)}/. {shlex.quote(new_dir)}/")

        _exec_sh(
            ssh,
            use_sudo,
            f"if [ -d {shlex.quote(remote_target_dir)} ]; then "
            f"mv {shlex.quote(remote_target_dir)} {shlex.quote(old_dir)}; "
            f"fi",
        )
        ssh.run(f"{_sudo_prefix(use_sudo)}mv {shlex.quote(new_dir)} {shlex.quote(remote_target_dir)}")
        ssh.run(f"{_sudo_prefix(use_sudo)}rm -rf {shlex.quote(old_dir)} {shlex.quote(extract_dir)} {shlex.quote(remote_bundle)}")


def update_frontend(cfg: Dict[str, Any], service_env: str, *, skip_build: bool) -> None:
    """
    Lightweight frontend update:
    - build dist locally (unless skip_build)
    - tar.gz dist
    - upload to remote tmp
    - extract to a new dir and atomically swap into place
    - no remote tar backup (fast path)
    """
    frontend_cfg = cfg.get("frontend") or {}
    if not isinstance(frontend_cfg, dict):
        raise SystemExit("Config error: frontend must be a mapping")

    remote_target_dir = str(frontend_cfg.get("remote_target_dir", "")).strip()
    remote_tmp_dir = str(frontend_cfg.get("remote_tmp_dir", "/tmp/fjbms-deploy")).strip()
    if not remote_target_dir:
        raise SystemExit("Config error: frontend.remote_target_dir is required")

    ts = _now_ts()
    if not skip_build:
        build_frontend(service_env)
    dist_dir = REPO_ROOT / "frontend" / "dist"
    _require_file(dist_dir, "Frontend build output missing; did the build succeed?")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    bundle = OUTPUT_DIR / f"frontend_update_{service_env}_{ts}.tar.gz"
    with tarfile.open(bundle, "w:gz") as tf:
        tf.add(dist_dir, arcname=".")

    ssh_conn, use_sudo, known_hosts = _ssh_from_cfg(cfg)
    with SSHClient(ssh_conn, known_hosts=known_hosts or None) as ssh:
        _remote_mkdir(ssh, False, remote_tmp_dir)

        remote_bundle = f"{remote_tmp_dir.rstrip('/')}/{bundle.name}"
        ssh.upload_file(bundle, remote_bundle, desc="upload(frontend-update)")

        extract_dir = f"{remote_tmp_dir.rstrip('/')}/frontend_update_extract_{ts}"
        new_dir = f"{remote_target_dir}.__new__{ts}"
        old_dir = f"{remote_target_dir}.__old__{ts}"

        _exec_sh(
            ssh,
            use_sudo,
            f"rm -rf {shlex.quote(extract_dir)} {shlex.quote(new_dir)} {shlex.quote(old_dir)} && "
            f"mkdir -p {shlex.quote(extract_dir)} {shlex.quote(new_dir)} && "
            f"tar -xzf {shlex.quote(remote_bundle)} -C {shlex.quote(extract_dir)} && "
            f"cp -a {shlex.quote(extract_dir)}/. {shlex.quote(new_dir)}/",
        )

        _exec_sh(
            ssh,
            use_sudo,
            f"if [ -d {shlex.quote(remote_target_dir)} ]; then "
            f"mv {shlex.quote(remote_target_dir)} {shlex.quote(old_dir)}; "
            f"fi && "
            f"mv {shlex.quote(new_dir)} {shlex.quote(remote_target_dir)}",
        )

        ssh.run(
            f"{_sudo_prefix(use_sudo)}rm -rf {shlex.quote(old_dir)} {shlex.quote(extract_dir)} {shlex.quote(remote_bundle)}",
            check=False,
        )


def deploy_backend(
    cfg: Dict[str, Any],
    env_name: str,
    goos: str,
    goarch: str,
    *,
    skip_build: bool,
) -> None:
    backend_cfg = cfg.get("backend") or {}
    if not isinstance(backend_cfg, dict):
        raise SystemExit("Config error: backend must be a mapping")

    remote_binary_path = str(backend_cfg.get("remote_binary_path", "")).strip()
    remote_tmp_dir = str(backend_cfg.get("remote_tmp_dir", "/tmp/fjbms-deploy")).strip()
    remote_backup_dir = str(backend_cfg.get("backup_dir", "")).strip()
    restart_command = str(backend_cfg.get("restart_command", "")).strip()

    local_config_path = str(backend_cfg.get("local_config_path", "")).strip()
    remote_config_path = str(backend_cfg.get("remote_config_path", "")).strip()
    remote_work_dir = str(backend_cfg.get("remote_work_dir", "")).strip()
    remote_log_file = str(backend_cfg.get("remote_log_file", "")).strip()
    remote_pid_file = str(backend_cfg.get("remote_pid_file", "")).strip()
    config_flag = str(backend_cfg.get("config_flag", "-config")).strip() or "-config"
    stop_timeout_sec = int(backend_cfg.get("stop_timeout_sec", 15))
    start_mode = str(backend_cfg.get("start_mode", "")).strip().lower()
    if not start_mode:
        start_mode = "systemd" if env_name == "prod" else "temp"
    if start_mode not in ("temp", "systemd"):
        raise SystemExit("Config error: backend.start_mode must be temp | systemd")

    local_configs_dir = str(backend_cfg.get("local_configs_dir", "backend/configs")).strip()
    local_sql_dir = str(backend_cfg.get("local_sql_dir", "backend/sql")).strip()
    remote_configs_dir = str(backend_cfg.get("remote_configs_dir", "")).strip()
    remote_sql_dir = str(backend_cfg.get("remote_sql_dir", "")).strip()
    if not remote_binary_path or not remote_backup_dir:
        raise SystemExit("Config error: backend.remote_binary_path and backend.backup_dir are required")
    if local_config_path or remote_config_path:
        if not local_config_path or not remote_config_path:
            raise SystemExit("Config error: backend.local_config_path and backend.remote_config_path must be set together")
        _require_file(Path(local_config_path), "backend.local_config_path points to a missing file")

    ts = _now_ts()
    if skip_build:
        local_bin = REPO_ROOT / "backend" / "bin" / "fjbms"
        _require_file(local_bin, "Backend binary missing; run build first.")
    else:
        local_bin = build_backend(goos, goarch)

    ssh_conn, use_sudo, known_hosts = _ssh_from_cfg(cfg)
    with SSHClient(ssh_conn, known_hosts=known_hosts or None) as ssh:
        # Upload uses SFTP as the SSH user (no sudo). Keep tmp dir user-writable.
        _remote_mkdir(ssh, False, remote_tmp_dir)
        _remote_mkdir(ssh, use_sudo, remote_backup_dir)

        if not remote_work_dir:
            remote_work_dir = str(Path(remote_binary_path).parent)
        if not remote_configs_dir:
            remote_configs_dir = f"{remote_work_dir.rstrip('/')}/configs"
        if not remote_sql_dir:
            remote_sql_dir = f"{remote_work_dir.rstrip('/')}/sql"

        # Backup current binary
        backup_file = f"{remote_backup_dir.rstrip('/')}/backend_{ts}.bin"
        _exec_sh(
            ssh,
            use_sudo,
            f"if [ -f {shlex.quote(remote_binary_path)} ]; then "
            f"cp -a {shlex.quote(remote_binary_path)} {shlex.quote(backup_file)}; "
            f"fi",
            check=False,
        )

        remote_upload = f"{remote_tmp_dir.rstrip('/')}/{local_bin.name}.{ts}"
        ssh.upload_file(local_bin, remote_upload, desc="upload(backend)")

        # Replace atomically in same filesystem when possible
        remote_dir = shlex.quote(str(Path(remote_binary_path).parent))
        ssh.exec(f"{_sudo_prefix(use_sudo)}mkdir -p {remote_dir}")
        ssh.run(f"{_sudo_prefix(use_sudo)}install -m 0755 {shlex.quote(remote_upload)} {shlex.quote(remote_binary_path)}")
        ssh.run(f"{_sudo_prefix(use_sudo)}rm -f {shlex.quote(remote_upload)}")

        # Upload configs directory (required for rsa keys / casbin.conf / etc)
        local_cfg_dir = (REPO_ROOT / local_configs_dir).resolve()
        if local_cfg_dir.exists():
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            cfg_bundle = OUTPUT_DIR / f"backend_configs_{ts}.tar.gz"
            _tar_dir(local_cfg_dir, cfg_bundle)
            remote_cfg_bundle = f"{remote_tmp_dir.rstrip('/')}/{cfg_bundle.name}"
            ssh.upload_file(cfg_bundle, remote_cfg_bundle, desc="upload(configs-dir)")
            _remote_mkdir(ssh, use_sudo, remote_configs_dir)
            _remote_replace_dir_from_tar(
                ssh,
                use_sudo,
                remote_bundle=remote_cfg_bundle,
                remote_dest_dir=remote_configs_dir,
                remote_tmp_dir=remote_tmp_dir,
                remote_backup_dir=remote_backup_dir,
                label="backend_configs",
                ts=ts,
            )
            ssh.run(f"{_sudo_prefix(use_sudo)}rm -f {shlex.quote(remote_cfg_bundle)}", check=False)

        # Upload sql directory (migrations/schema files)
        local_sql_dir_path = (REPO_ROOT / local_sql_dir).resolve()
        if local_sql_dir_path.exists():
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            sql_bundle = OUTPUT_DIR / f"backend_sql_{ts}.tar.gz"
            _tar_dir(local_sql_dir_path, sql_bundle)
            remote_sql_bundle = f"{remote_tmp_dir.rstrip('/')}/{sql_bundle.name}"
            ssh.upload_file(sql_bundle, remote_sql_bundle, desc="upload(sql-dir)")
            _remote_mkdir(ssh, use_sudo, remote_sql_dir)
            _remote_replace_dir_from_tar(
                ssh,
                use_sudo,
                remote_bundle=remote_sql_bundle,
                remote_dest_dir=remote_sql_dir,
                remote_tmp_dir=remote_tmp_dir,
                remote_backup_dir=remote_backup_dir,
                label="backend_sql",
                ts=ts,
            )
            ssh.run(f"{_sudo_prefix(use_sudo)}rm -f {shlex.quote(remote_sql_bundle)}", check=False)

        # Deploy backend config file (optional)
        if local_config_path and remote_config_path:
            config_backup = f"{remote_backup_dir.rstrip('/')}/backend_config_{ts}.yml"
            _exec_sh(
                ssh,
                use_sudo,
                f"if [ -f {shlex.quote(remote_config_path)} ]; then "
                f"cp -a {shlex.quote(remote_config_path)} {shlex.quote(config_backup)}; "
                f"fi",
                check=False,
            )

            local_cfg = Path(local_config_path)
            remote_cfg_upload = f"{remote_tmp_dir.rstrip('/')}/{local_cfg.name}.{ts}"
            ssh.upload_file(local_cfg, remote_cfg_upload, desc="upload(config)")

            cfg_dir = shlex.quote(str(Path(remote_config_path).parent))
            ssh.run(f"{_sudo_prefix(use_sudo)}mkdir -p {cfg_dir}")
            ssh.run(f"{_sudo_prefix(use_sudo)}install -m 0644 {shlex.quote(remote_cfg_upload)} {shlex.quote(remote_config_path)}")
            ssh.run(f"{_sudo_prefix(use_sudo)}rm -f {shlex.quote(remote_cfg_upload)}")

        # Restart / run backend
        if restart_command:
            ssh.run(f"{_sudo_prefix(use_sudo)}{_quote(restart_command)}", get_pty=False)
            return

        # Default: choose start mode by env/config.
        if not remote_config_path:
            raise SystemExit(
                "Config error: backend.remote_config_path is required when restart_command is not set "
                "(for direct binary start)."
            )
        if not remote_log_file:
            remote_log_file = f"{remote_work_dir.rstrip('/')}/backend.log"
        if not remote_pid_file:
            remote_pid_file = f"{remote_work_dir.rstrip('/')}/backend.pid"

        ssh.run(f"{_sudo_prefix(use_sudo)}mkdir -p {shlex.quote(remote_work_dir)}")
        ssh.run(f"{_sudo_prefix(use_sudo)}mkdir -p {shlex.quote(str(Path(remote_log_file).parent))}")

        if start_mode == "systemd":
            systemd_cfg = backend_cfg.get("systemd") or {}
            if not isinstance(systemd_cfg, dict):
                raise SystemExit("Config error: backend.systemd must be a mapping")
            service_name = str(systemd_cfg.get("service_name", "fjbms-backend")).strip() or "fjbms-backend"
            unit_path = str(systemd_cfg.get("unit_path", f"/etc/systemd/system/{service_name}.service")).strip()
            install_script_path = str(
                systemd_cfg.get("install_script_path", f"{remote_work_dir.rstrip('/')}/install_{service_name}_systemd.sh")
            ).strip()
            auto_install = bool(systemd_cfg.get("auto_install", True))

            exec_start_inner = (
                f"cd {shlex.quote(remote_work_dir)} && "
                f"exec {shlex.quote(remote_binary_path)} {shlex.quote(config_flag)} {shlex.quote(remote_config_path)} "
                f">> {shlex.quote(remote_log_file)} 2>&1"
            )
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            local_installer = OUTPUT_DIR / f"install_systemd_{service_name}_{ts}.sh"
            local_installer.write_text(
                _render_systemd_install_script(
                    service_name=service_name,
                    work_dir=remote_work_dir,
                    exec_start=exec_start_inner,
                    log_file=remote_log_file,
                    unit_path=unit_path,
                ),
                encoding="utf-8",
            )
            remote_installer_upload = f"{remote_tmp_dir.rstrip('/')}/{local_installer.name}"
            ssh.upload_file(local_installer, remote_installer_upload, desc="upload(systemd-installer)")
            ssh.run(
                f"{_sudo_prefix(use_sudo)}install -m 0755 {shlex.quote(remote_installer_upload)} {shlex.quote(install_script_path)}"
            )
            ssh.run(f"{_sudo_prefix(use_sudo)}rm -f {shlex.quote(remote_installer_upload)}", check=False)

            if auto_install:
                _exec_sh(ssh, use_sudo, f"bash {shlex.quote(install_script_path)}")
            return

        _backend_temp_stop(ssh, use_sudo, pid_file=remote_pid_file, stop_timeout_sec=stop_timeout_sec)
        _backend_temp_start(
            ssh,
            use_sudo,
            work_dir=remote_work_dir,
            binary_path=remote_binary_path,
            config_flag=config_flag,
            config_path=remote_config_path,
            log_file=remote_log_file,
            pid_file=remote_pid_file,
        )


def update_backend(
    cfg: Dict[str, Any],
    env_name: str,
    goos: str,
    goarch: str,
    *,
    skip_build: bool,
    with_config: bool = False,
) -> None:
    """
    Lightweight backend update:
    - upload new binary
    - optionally upload config.yml (with_config)
    - restart using start_mode:
      - test: temp (pid + nohup)
      - prod: systemd (systemctl restart)
    """
    backend_cfg = cfg.get("backend") or {}
    if not isinstance(backend_cfg, dict):
        raise SystemExit("Config error: backend must be a mapping")

    remote_binary_path = str(backend_cfg.get("remote_binary_path", "")).strip()
    remote_tmp_dir = str(backend_cfg.get("remote_tmp_dir", "/tmp/fjbms-deploy")).strip()
    remote_work_dir = str(backend_cfg.get("remote_work_dir", "")).strip()
    remote_log_file = str(backend_cfg.get("remote_log_file", "")).strip()
    remote_pid_file = str(backend_cfg.get("remote_pid_file", "")).strip()
    config_flag = str(backend_cfg.get("config_flag", "-config")).strip() or "-config"
    stop_timeout_sec = int(backend_cfg.get("stop_timeout_sec", 15))

    local_config_path = str(backend_cfg.get("local_config_path", "")).strip()
    remote_config_path = str(backend_cfg.get("remote_config_path", "")).strip()
    restart_command = str(backend_cfg.get("restart_command", "")).strip()

    start_mode = str(backend_cfg.get("start_mode", "")).strip().lower()
    if not start_mode:
        start_mode = "systemd" if env_name == "prod" else "temp"
    if start_mode not in ("temp", "systemd"):
        raise SystemExit("Config error: backend.start_mode must be temp | systemd")

    if not remote_binary_path:
        raise SystemExit("Config error: backend.remote_binary_path is required")

    ts = _now_ts()
    if skip_build:
        local_bin = REPO_ROOT / "backend" / "bin" / "fjbms"
        _require_file(local_bin, "Backend binary missing; run build first.")
    else:
        local_bin = build_backend(goos, goarch)

    if with_config:
        if not local_config_path or not remote_config_path:
            raise SystemExit("Config error: update --with-config requires backend.local_config_path + backend.remote_config_path")
        _require_file(Path(local_config_path), "backend.local_config_path points to a missing file")

    ssh_conn, use_sudo, known_hosts = _ssh_from_cfg(cfg)
    with SSHClient(ssh_conn, known_hosts=known_hosts or None) as ssh:
        _remote_mkdir(ssh, False, remote_tmp_dir)

        remote_upload = f"{remote_tmp_dir.rstrip('/')}/{local_bin.name}.{ts}"
        ssh.upload_file(local_bin, remote_upload, desc="upload(backend-update)")
        remote_dir = shlex.quote(str(Path(remote_binary_path).parent))
        ssh.run(f"{_sudo_prefix(use_sudo)}mkdir -p {remote_dir}")
        ssh.run(f"{_sudo_prefix(use_sudo)}install -m 0755 {shlex.quote(remote_upload)} {shlex.quote(remote_binary_path)}")
        ssh.run(f"{_sudo_prefix(use_sudo)}rm -f {shlex.quote(remote_upload)}", check=False)

        if with_config:
            local_cfg = Path(local_config_path)
            remote_cfg_upload = f"{remote_tmp_dir.rstrip('/')}/{local_cfg.name}.{ts}"
            ssh.upload_file(local_cfg, remote_cfg_upload, desc="upload(config-update)")
            cfg_dir = shlex.quote(str(Path(remote_config_path).parent))
            ssh.run(f"{_sudo_prefix(use_sudo)}mkdir -p {cfg_dir}")
            ssh.run(f"{_sudo_prefix(use_sudo)}install -m 0644 {shlex.quote(remote_cfg_upload)} {shlex.quote(remote_config_path)}")
            ssh.run(f"{_sudo_prefix(use_sudo)}rm -f {shlex.quote(remote_cfg_upload)}", check=False)

        # If an environment uses a custom restart hook, honor it.
        if restart_command:
            ssh.run(f"{_sudo_prefix(use_sudo)}{_quote(restart_command)}", get_pty=False)
            return

        if start_mode == "systemd":
            systemd_cfg = backend_cfg.get("systemd") or {}
            if not isinstance(systemd_cfg, dict):
                raise SystemExit("Config error: backend.systemd must be a mapping")
            service_name = str(systemd_cfg.get("service_name", "fjbms-backend")).strip() or "fjbms-backend"
            ssh.run(f"{_sudo_prefix(use_sudo)}systemctl restart {shlex.quote(service_name)}")
            ssh.run(f"{_sudo_prefix(use_sudo)}systemctl status {shlex.quote(service_name)} --no-pager", check=False)
            return

        # temp mode
        if not remote_config_path:
            raise SystemExit("Config error: backend.remote_config_path is required for temp start")
        if not remote_work_dir:
            remote_work_dir = str(Path(remote_binary_path).parent)
        if not remote_log_file:
            remote_log_file = f"{remote_work_dir.rstrip('/')}/backend.log"
        if not remote_pid_file:
            remote_pid_file = f"{remote_work_dir.rstrip('/')}/backend.pid"

        ssh.run(f"{_sudo_prefix(use_sudo)}mkdir -p {shlex.quote(remote_work_dir)}")
        ssh.run(f"{_sudo_prefix(use_sudo)}mkdir -p {shlex.quote(str(Path(remote_log_file).parent))}")

        _backend_temp_stop(ssh, use_sudo, pid_file=remote_pid_file, stop_timeout_sec=stop_timeout_sec)
        _backend_temp_start(
            ssh,
            use_sudo,
            work_dir=remote_work_dir,
            binary_path=remote_binary_path,
            config_flag=config_flag,
            config_path=remote_config_path,
            log_file=remote_log_file,
            pid_file=remote_pid_file,
        )


def db_export(cfg: Dict[str, Any]) -> Path:
    db_cfg = cfg.get("db") or {}
    if not isinstance(db_cfg, dict):
        raise SystemExit("Config error: db must be a mapping")

    db_type = str(db_cfg.get("type", "mysql")).strip().lower()
    host = str(db_cfg.get("host", "127.0.0.1")).strip()
    port = int(db_cfg.get("port", 3306 if db_type == "mysql" else 5432))
    user = str(db_cfg.get("user", "")).strip()
    database = str(db_cfg.get("database", "")).strip()
    password_env = db_cfg.get("password_env")
    password = os.environ.get(str(password_env)) if password_env else None

    if not user or not database:
        raise SystemExit("Config error: db.user and db.database are required")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUTPUT_DIR / f"db_{db_type}_{_now_ts()}.sql"

    ssh_conn, _use_sudo, known_hosts = _ssh_from_cfg(cfg)
    with SSHClient(ssh_conn, known_hosts=known_hosts or None) as ssh:
        if db_type == "mysql":
            env = {}
            if password is not None:
                env["MYSQL_PWD"] = password
            cmd = (
                "mysqldump --single-transaction --routines --triggers --events "
                f"-h {shlex.quote(host)} -P {shlex.quote(str(port))} -u {shlex.quote(user)} "
                f"{shlex.quote(database)}"
            )
            ssh.stream_to_local_file(cmd, out, desc="export(mysql)", env=env)
        elif db_type in ("postgres", "postgresql", "pg"):
            env = {}
            if password is not None:
                env["PGPASSWORD"] = password
            cmd = (
                "pg_dump --format=plain --no-owner --no-privileges "
                f"-h {shlex.quote(host)} -p {shlex.quote(str(port))} -U {shlex.quote(user)} "
                f"{shlex.quote(database)}"
            )
            ssh.stream_to_local_file(cmd, out, desc="export(pg)", env=env)
        else:
            raise SystemExit(f"Unsupported db.type: {db_type} (use mysql or postgres)")

    return out


def db_import(cfg: Dict[str, Any], sql_path: Path) -> None:
    db_cfg = cfg.get("db") or {}
    if not isinstance(db_cfg, dict):
        raise SystemExit("Config error: db must be a mapping")

    db_type = str(db_cfg.get("type", "mysql")).strip().lower()
    host = str(db_cfg.get("host", "127.0.0.1")).strip()
    port = int(db_cfg.get("port", 3306 if db_type == "mysql" else 5432))
    user = str(db_cfg.get("user", "")).strip()
    database = str(db_cfg.get("database", "")).strip()
    password_env = db_cfg.get("password_env")
    password = os.environ.get(str(password_env)) if password_env else None

    if not user or not database:
        raise SystemExit("Config error: db.user and db.database are required")
    _require_file(sql_path, "Provide --sql path/to/file.sql")

    ssh_conn, _use_sudo, known_hosts = _ssh_from_cfg(cfg)
    with SSHClient(ssh_conn, known_hosts=known_hosts or None) as ssh:
        remote_tmp_dir = str((cfg.get("db") or {}).get("remote_tmp_dir", "/tmp/fjbms-deploy")).strip()
        _remote_mkdir(ssh, False, remote_tmp_dir)
        remote_sql = f"{remote_tmp_dir.rstrip('/')}/{sql_path.name}.{_now_ts()}"
        ssh.upload_file(sql_path, remote_sql, desc="upload(sql)")

        if db_type == "mysql":
            env = {}
            if password is not None:
                env["MYSQL_PWD"] = password
            cmd = (
                f"mysql -h {shlex.quote(host)} -P {shlex.quote(str(port))} -u {shlex.quote(user)} "
                f"{shlex.quote(database)} < {shlex.quote(remote_sql)}"
            )
            ssh.run(cmd, env=env)
        elif db_type in ("postgres", "postgresql", "pg"):
            env = {}
            if password is not None:
                env["PGPASSWORD"] = password
            cmd = (
                f"psql -h {shlex.quote(host)} -p {shlex.quote(str(port))} -U {shlex.quote(user)} "
                f"-d {shlex.quote(database)} -f {shlex.quote(remote_sql)}"
            )
            ssh.run(cmd, env=env)
        else:
            raise SystemExit(f"Unsupported db.type: {db_type} (use mysql or postgres)")

        ssh.run(f"rm -f {shlex.quote(remote_sql)}", check=False)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="devops.py")
    parser.add_argument("--config", help="Override config path (yaml)")
    parser.add_argument("--quiet", action="store_true", help="Reduce console output")

    sub = parser.add_subparsers(dest="cmd", required=True)

    p_build = sub.add_parser("build", help="Build artifacts locally")
    build_sub = p_build.add_subparsers(dest="target", required=True)
    p_bf = build_sub.add_parser("frontend", help="Build frontend")
    p_bf.add_argument("--service-env", choices=["test", "prod"], default="prod")
    p_bb = build_sub.add_parser("backend", help="Build backend")
    p_bb.add_argument("--goos", default=os.environ.get("GOOS", "linux"))
    p_bb.add_argument("--goarch", default=os.environ.get("GOARCH", "amd64"))

    p_deploy = sub.add_parser("deploy", help="Deploy to remote via SSH")
    p_deploy.add_argument("--env", choices=["test", "prod"], required=True)
    deploy_sub = p_deploy.add_subparsers(dest="target", required=True)
    p_df = deploy_sub.add_parser("frontend")
    p_df.add_argument("--service-env", choices=["test", "prod"], default="test")
    p_df.add_argument("--skip-build", action="store_true", help="Skip local build step")
    p_db = deploy_sub.add_parser("backend")
    p_db.add_argument("--goos", default=os.environ.get("GOOS", "linux"))
    p_db.add_argument("--goarch", default=os.environ.get("GOARCH", "amd64"))
    p_db.add_argument("--skip-build", action="store_true", help="Skip local build step")

    p_dbroot = sub.add_parser("db", help="DB export/import via SSH")
    p_dbroot.add_argument("--env", choices=["test", "prod"], required=True)
    db_sub = p_dbroot.add_subparsers(dest="action", required=True)
    p_dbe = db_sub.add_parser("export")
    p_dbi = db_sub.add_parser("import")
    p_dbi.add_argument("--sql", required=True)

    p_update = sub.add_parser("update", help="Lightweight update to remote via SSH")
    p_update.add_argument("--env", choices=["test", "prod"], required=True)
    update_sub = p_update.add_subparsers(dest="target", required=True)
    p_uf = update_sub.add_parser("frontend")
    p_uf.add_argument("--service-env", choices=["test", "prod"], default="test")
    p_uf.add_argument("--skip-build", action="store_true", help="Skip local build step")
    p_ub = update_sub.add_parser("backend")
    p_ub.add_argument("--goos", default=os.environ.get("GOOS", "linux"))
    p_ub.add_argument("--goarch", default=os.environ.get("GOARCH", "amd64"))
    p_ub.add_argument("--skip-build", action="store_true", help="Skip local build step")
    p_ub.add_argument("--with-config", action="store_true", help="Also upload backend config file")

    args = parser.parse_args(argv)
    global QUIET
    QUIET = bool(args.quiet)

    if args.cmd == "build":
        if args.target == "frontend":
            build_frontend(args.service_env)
            return 0
        if args.target == "backend":
            build_backend(args.goos, args.goarch)
            return 0
        raise SystemExit("unknown build target")

    if args.cmd == "deploy":
        cfg = _cfg_for_env(args.env, args.config)
        if args.target == "frontend":
            deploy_frontend(cfg, args.service_env, skip_build=bool(args.skip_build))
            return 0
        if args.target == "backend":
            deploy_backend(cfg, args.env, args.goos, args.goarch, skip_build=bool(args.skip_build))
            return 0
        raise SystemExit("unknown deploy target")

    if args.cmd == "update":
        cfg = _cfg_for_env(args.env, args.config)
        if args.target == "frontend":
            update_frontend(cfg, args.service_env, skip_build=bool(args.skip_build))
            return 0
        if args.target == "backend":
            update_backend(
                cfg,
                args.env,
                args.goos,
                args.goarch,
                skip_build=bool(args.skip_build),
                with_config=bool(args.with_config),
            )
            return 0
        raise SystemExit("unknown update target")

    if args.cmd == "db":
        cfg = _cfg_for_env(args.env, args.config)
        if args.action == "export":
            out = db_export(cfg)
            print(str(out))
            return 0
        if args.action == "import":
            db_import(cfg, Path(args.sql))
            return 0
        raise SystemExit("unknown db action")

    raise SystemExit("unknown command")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
