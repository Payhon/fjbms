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


def _now_ts() -> str:
    return time.strftime("%Y%m%d_%H%M%S", time.localtime())


def _eprint(msg: str) -> None:
    print(msg, file=sys.stderr)


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
        key_filename = None
        passphrase = None
        if self._conn.key_path:
            key_filename = _expand_path(self._conn.key_path)
            passphrase = os.environ.get("SSH_KEY_PASSPHRASE")

        self._client.connect(
            hostname=self._conn.host,
            port=self._conn.port,
            username=self._conn.username,
            password=self._conn.password,
            key_filename=key_filename,
            passphrase=passphrase,
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
    key_path = ssh_cfg.get("key_path")
    password = None
    password_env = ssh_cfg.get("password_env")
    if password_env:
        password = os.environ.get(str(password_env))
        if password is None:
            raise SystemExit(f"Missing env var for ssh.password_env: {password_env}")

    use_sudo = bool(ssh_cfg.get("use_sudo", False))
    known_hosts = str(ssh_cfg.get("known_hosts", "")).strip() or None
    return SSHConn(host=host, port=port, username=user, key_path=key_path, password=password), use_sudo, known_hosts or ""


def _sudo_prefix(use_sudo: bool) -> str:
    return "sudo -n " if use_sudo else ""


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
    ssh.exec(f"{_sudo_prefix(use_sudo)}mkdir -p {shlex.quote(path)}")


def deploy_frontend(cfg: Dict[str, Any], service_env: str) -> None:
    frontend_cfg = cfg.get("frontend") or {}
    if not isinstance(frontend_cfg, dict):
        raise SystemExit("Config error: frontend must be a mapping")

    remote_target_dir = str(frontend_cfg.get("remote_target_dir", "")).strip()
    remote_tmp_dir = str(frontend_cfg.get("remote_tmp_dir", "/tmp/fjbms-deploy")).strip()
    remote_backup_dir = str(frontend_cfg.get("backup_dir", "")).strip()
    if not remote_target_dir or not remote_backup_dir:
        raise SystemExit("Config error: frontend.remote_target_dir and frontend.backup_dir are required")

    ts = _now_ts()
    build_frontend(service_env)
    dist_dir = REPO_ROOT / "frontend" / "dist"
    _require_file(dist_dir, "Frontend build output missing; did the build succeed?")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    bundle = OUTPUT_DIR / f"frontend_{service_env}_{ts}.tar.gz"
    with tarfile.open(bundle, "w:gz") as tf:
        tf.add(dist_dir, arcname=".")

    ssh_conn, use_sudo, known_hosts = _ssh_from_cfg(cfg)
    with SSHClient(ssh_conn, known_hosts=known_hosts or None) as ssh:
        _remote_mkdir(ssh, use_sudo, remote_tmp_dir)
        _remote_mkdir(ssh, use_sudo, remote_backup_dir)

        # Backup current
        backup_file = f"{remote_backup_dir.rstrip('/')}/frontend_{ts}.tar.gz"
        ssh.exec(
            f"{_sudo_prefix(use_sudo)}if [ -d {shlex.quote(remote_target_dir)} ]; then "
            f"tar -czf {shlex.quote(backup_file)} -C {shlex.quote(remote_target_dir)} .; "
            f"fi"
        )

        remote_bundle = f"{remote_tmp_dir.rstrip('/')}/{bundle.name}"
        ssh.upload_file(bundle, remote_bundle, desc="upload(frontend)")

        extract_dir = f"{remote_tmp_dir.rstrip('/')}/frontend_extract_{ts}"
        new_dir = f"{remote_target_dir}.__new__{ts}"
        old_dir = f"{remote_target_dir}.__old__{ts}"

        ssh.exec(f"{_sudo_prefix(use_sudo)}rm -rf {shlex.quote(extract_dir)} {shlex.quote(new_dir)} {shlex.quote(old_dir)}")
        ssh.exec(f"{_sudo_prefix(use_sudo)}mkdir -p {shlex.quote(extract_dir)} {shlex.quote(new_dir)}")
        ssh.exec(f"{_sudo_prefix(use_sudo)}tar -xzf {shlex.quote(remote_bundle)} -C {shlex.quote(extract_dir)}")
        ssh.exec(f"{_sudo_prefix(use_sudo)}cp -a {shlex.quote(extract_dir)}/. {shlex.quote(new_dir)}/")

        ssh.exec(
            f"{_sudo_prefix(use_sudo)}if [ -d {shlex.quote(remote_target_dir)} ]; then "
            f"mv {shlex.quote(remote_target_dir)} {shlex.quote(old_dir)}; fi"
        )
        ssh.exec(f"{_sudo_prefix(use_sudo)}mv {shlex.quote(new_dir)} {shlex.quote(remote_target_dir)}")
        ssh.exec(f"{_sudo_prefix(use_sudo)}rm -rf {shlex.quote(old_dir)} {shlex.quote(extract_dir)} {shlex.quote(remote_bundle)}")


def deploy_backend(cfg: Dict[str, Any], goos: str, goarch: str) -> None:
    backend_cfg = cfg.get("backend") or {}
    if not isinstance(backend_cfg, dict):
        raise SystemExit("Config error: backend must be a mapping")

    remote_binary_path = str(backend_cfg.get("remote_binary_path", "")).strip()
    remote_tmp_dir = str(backend_cfg.get("remote_tmp_dir", "/tmp/fjbms-deploy")).strip()
    remote_backup_dir = str(backend_cfg.get("backup_dir", "")).strip()
    restart_command = str(backend_cfg.get("restart_command", "")).strip()
    if not remote_binary_path or not remote_backup_dir:
        raise SystemExit("Config error: backend.remote_binary_path and backend.backup_dir are required")

    ts = _now_ts()
    local_bin = build_backend(goos, goarch)

    ssh_conn, use_sudo, known_hosts = _ssh_from_cfg(cfg)
    with SSHClient(ssh_conn, known_hosts=known_hosts or None) as ssh:
        _remote_mkdir(ssh, use_sudo, remote_tmp_dir)
        _remote_mkdir(ssh, use_sudo, remote_backup_dir)

        # Backup current binary
        backup_file = f"{remote_backup_dir.rstrip('/')}/backend_{ts}.bin"
        ssh.exec(
            f"{_sudo_prefix(use_sudo)}if [ -f {shlex.quote(remote_binary_path)} ]; then "
            f"cp -a {shlex.quote(remote_binary_path)} {shlex.quote(backup_file)}; "
            f"fi"
        )

        remote_upload = f"{remote_tmp_dir.rstrip('/')}/{local_bin.name}.{ts}"
        ssh.upload_file(local_bin, remote_upload, desc="upload(backend)")

        # Replace atomically in same filesystem when possible
        remote_dir = shlex.quote(str(Path(remote_binary_path).parent))
        ssh.exec(f"{_sudo_prefix(use_sudo)}mkdir -p {remote_dir}")
        ssh.exec(f"{_sudo_prefix(use_sudo)}install -m 0755 {shlex.quote(remote_upload)} {shlex.quote(remote_binary_path)}")
        ssh.exec(f"{_sudo_prefix(use_sudo)}rm -f {shlex.quote(remote_upload)}")

        if restart_command:
            ssh.exec(f"{_sudo_prefix(use_sudo)}{_quote(restart_command)}", get_pty=False)


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
            ssh.exec(cmd, env=env)
        elif db_type in ("postgres", "postgresql", "pg"):
            env = {}
            if password is not None:
                env["PGPASSWORD"] = password
            cmd = (
                f"psql -h {shlex.quote(host)} -p {shlex.quote(str(port))} -U {shlex.quote(user)} "
                f"-d {shlex.quote(database)} -f {shlex.quote(remote_sql)}"
            )
            ssh.exec(cmd, env=env)
        else:
            raise SystemExit(f"Unsupported db.type: {db_type} (use mysql or postgres)")

        ssh.exec(f"rm -f {shlex.quote(remote_sql)}", check=False)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="devops.py")
    parser.add_argument("--config", help="Override config path (yaml)")

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
    p_db = deploy_sub.add_parser("backend")
    p_db.add_argument("--goos", default=os.environ.get("GOOS", "linux"))
    p_db.add_argument("--goarch", default=os.environ.get("GOARCH", "amd64"))

    p_dbroot = sub.add_parser("db", help="DB export/import via SSH")
    p_dbroot.add_argument("--env", choices=["test", "prod"], required=True)
    db_sub = p_dbroot.add_subparsers(dest="action", required=True)
    p_dbe = db_sub.add_parser("export")
    p_dbi = db_sub.add_parser("import")
    p_dbi.add_argument("--sql", required=True)

    args = parser.parse_args(argv)

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
            deploy_frontend(cfg, args.service_env)
            return 0
        if args.target == "backend":
            deploy_backend(cfg, args.goos, args.goarch)
            return 0
        raise SystemExit("unknown deploy target")

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
