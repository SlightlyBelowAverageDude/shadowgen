"""Run an experiment on a remote box and bring the outputs back.

Nothing of the project is kept on the remote. Each run ships a snapshot of the
working tree (uncommitted edits included), runs one command there detached,
and `fetch` copies every file the run created or changed into
remote_runs/<run-id>/ here, then deletes the remote copy. Original result files
in this checkout are never touched.

The remote keeps only uv, uv-managed CPython builds, and virtualenvs under
~/envs. Each remote env mirrors a local venv (env/ by default, the one the
benchmark scripts name): same Python version, same package versions from its
freeze, minus Windows-only packages. A changed local venv gives a new env.

Usage (from the repo root, with the project's Python):
  python tools/remote_run.py run [--label NAME] [--data D1,D3 | --no-data]
                                 [--include PATH ...] [--env K=V ...]
                                 [--venv env|.venv] -- CMD ...
  python tools/remote_run.py status [RUN_ID]
  python tools/remote_run.py log RUN_ID [-n LINES]
  python tools/remote_run.py fetch RUN_ID [--keep]
  python tools/remote_run.py kill RUN_ID

CMD given as several arguments is quoted word by word. CMD given as one
argument is passed to bash as is, so pipes and && work:
  ... run -- "python a.py --x 1 && python b.py"

PYTHONHASHSEED=0 is exported by default (benchmark protocol); --env overrides it.
The host defaults to the ssh alias in REMOTE_RUN_HOST, else "bro-box".
"""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import io
import json
import os
import re
import shlex
import subprocess
import sys
import tarfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LOCAL_RUNS = REPO / "remote_runs"
DEFAULT_HOST = os.environ.get("REMOTE_RUN_HOST", "bro-box")

# Shipped on every run, relative to the repo root.
BASE_INCLUDE = ["HybridGen", "benchmark", "shadowgen.py", "pyproject.toml", "uv.lock", ".python-version"]
SKIP_DIRS = {"__pycache__", ".ipynb_checkpoints", ".git", ".venv"}
SKIP_SUFFIXES = {".pyc", ".pyo"}
# Converted CRLF -> LF on the way out (the Windows checkout uses autocrlf).
TEXT_SUFFIXES = {".sh", ".py"}

UV = "$HOME/.local/bin/uv"
META_DIR = ".remote_run"
# Left out of the remote env (no Linux build, or the installer itself).
WIN_ONLY = {"pywin32", "pywinpty", "pywin32-ctypes", "winpty", "wmi", "comtypes", "pip"}


# ---------------------------------------------------------------- helpers

def ssh(host: str, script: str, *, check: bool = True, capture: bool = True, stdin=None) -> subprocess.CompletedProcess:
    proc = subprocess.run(
        ["ssh", "-o", "BatchMode=yes", host, "bash -s"],
        input=script.encode(), stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )
    if check and proc.returncode != 0:
        err = (proc.stderr or b"").decode(errors="replace")
        out = (proc.stdout or b"").decode(errors="replace")
        sys.exit(f"remote command failed (exit {proc.returncode}):\n{out}{err}")
    return proc


def venv_spec(venv: str) -> tuple[str, str, str]:
    """(python version, filtered freeze, key) of a local venv."""
    root = REPO / venv
    cfg = root / "pyvenv.cfg"
    if not cfg.exists():
        sys.exit(f"no venv at {root}")
    fields = dict(l.split("=", 1) for l in cfg.read_text().splitlines() if "=" in l)
    fields = {k.strip(): v.strip() for k, v in fields.items()}
    py = fields.get("version_info") or fields.get("version")
    if not py:
        sys.exit(f"cannot read the Python version from {cfg}")
    py = ".".join(py.split(".")[:3])
    exe = root / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    proc = subprocess.run(["uv", "pip", "freeze", "--python", str(exe)], capture_output=True, text=True)
    if proc.returncode != 0:
        proc = subprocess.run([str(exe), "-m", "pip", "freeze"], capture_output=True, text=True)
    if proc.returncode != 0:
        sys.exit(f"cannot freeze {root}:\n{proc.stderr}")
    keep = []
    for line in proc.stdout.splitlines():
        name = re.split(r"[=<>@ ;]", line.strip(), maxsplit=1)[0].lower().replace("_", "-")
        if name and name not in WIN_ONLY and not line.startswith("-e "):
            keep.append(line.strip())
    freeze = "\n".join(sorted(keep, key=str.lower)) + "\n"
    key = hashlib.sha256(f"{py}\n{freeze}".encode()).hexdigest()[:12]
    return py, freeze, key


def dataset_paths(ids: list[str]) -> list[str]:
    src = (REPO / "benchmark" / "datasets.py").read_text(encoding="utf-8")
    table = dict(re.findall(r'"(D\w+)"\s*:\s*\{[^}]*?"log_path"\s*:\s*"([^"]+)"', src, flags=re.S))
    missing = [i for i in ids if i not in table]
    if missing:
        sys.exit(f"unknown dataset id(s) {missing}; known: {sorted(table)}")
    return [table[i] for i in ids]


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True).stdout.strip()


def iter_files(rel_paths: list[str]):
    for rel in rel_paths:
        p = REPO / rel
        if not p.exists():
            sys.exit(f"include path not found: {rel}")
        if p.is_file():
            yield p
            continue
        for root, dirs, files in os.walk(p):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for f in files:
                fp = Path(root) / f
                if fp.suffix not in SKIP_SUFFIXES:
                    yield fp


def write_snapshot(stream, files) -> tuple[int, int]:
    n = size = 0
    with gzip.GzipFile(fileobj=stream, mode="wb", compresslevel=1) as gz:
        with tarfile.open(fileobj=gz, mode="w|", format=tarfile.PAX_FORMAT) as tar:
            for fp in files:
                arc = fp.relative_to(REPO).as_posix()
                st = fp.stat()
                data = fp.read_bytes()
                if fp.suffix in TEXT_SUFFIXES:
                    data = data.replace(b"\r\n", b"\n")
                ti = tarfile.TarInfo(arc)
                ti.size = len(data)
                ti.mtime = int(st.st_mtime)
                ti.mode = 0o755 if fp.suffix == ".sh" else 0o644
                tar.addfile(ti, io.BytesIO(data))
                n += 1
                size += len(data)
    return n, size


# ---------------------------------------------------------------- commands

def cmd_run(a) -> None:
    py, freeze, ekey = venv_spec(a.venv)
    ename = f"py{py}-{ekey}"
    label = re.sub(r"[^A-Za-z0-9_.-]+", "-", a.label or "run").strip("-") or "run"
    run_id = f"{dt.datetime.now():%Y%m%d-%H%M%S}-{label}"
    rdir = f"$HOME/runs/{run_id}"

    include = list(BASE_INCLUDE)
    datasets = []
    if not a.no_data:
        if a.data:
            datasets = [d.strip() for d in a.data.split(",") if d.strip()]
            include += dataset_paths(datasets)
        else:
            include.append("data")
    include += a.include or []

    if not a.cmd:
        sys.exit("no command given (put it after --)")
    command = a.cmd[0] if len(a.cmd) == 1 else shlex.join(a.cmd)

    envs = {"PYTHONHASHSEED": "0"}
    for kv in a.env or []:
        k, _, v = kv.partition("=")
        envs[k] = v

    # 1. ship the snapshot
    print(f"[{run_id}] shipping to {a.host} ...", flush=True)
    t0 = dt.datetime.now()
    proc = subprocess.Popen(
        ["ssh", "-o", "BatchMode=yes", a.host,
         f'mkdir -p {rdir}/{META_DIR} && tar -xzf - -C {rdir} && touch {rdir}/{META_DIR}/shipped'],
        stdin=subprocess.PIPE,
    )
    n, size = write_snapshot(proc.stdin, iter_files(include))
    proc.stdin.close()
    if proc.wait() != 0:
        sys.exit("shipping failed")
    secs = (dt.datetime.now() - t0).total_seconds()
    print(f"[{run_id}] shipped {n} files, {size / 2**20:.1f} MB in {secs:.1f} s", flush=True)

    # 2. make sure the environment exists, 3. start detached
    exports = "\n".join(f"export {k}={shlex.quote(v)}" for k, v in envs.items())
    run_sh = f"""#!/usr/bin/env bash
cd "{rdir}"
export VIRTUAL_ENV="$HOME/envs/{ename}"
export PATH="$VIRTUAL_ENV/bin:$HOME/.local/bin:$PATH"
{exports}
date -Is > {META_DIR}/started
bash -c {shlex.quote(command)}
echo $? > {META_DIR}/exit
date -Is > {META_DIR}/finished
"""
    remote = f"""set -e
cd "{rdir}"
cat > {META_DIR}/run.sh <<'__RUN_SH__'
{run_sh}__RUN_SH__
printf '%s\\n' {shlex.quote(command)} > {META_DIR}/command
E="$HOME/envs/{ename}"
mkdir -p "$HOME/envs"
cat > {META_DIR}/requirements.txt <<'__REQ__'
{freeze}__REQ__
(
  flock 9
  if [ ! -f "$E/.complete" ]; then
    echo "building env {ename} (first use of this package set) ..."
    rm -rf "$E"
    {UV} venv -q --python {py} "$E"
    {UV} pip install -q --python "$E/bin/python" -r {META_DIR}/requirements.txt
    cp {META_DIR}/requirements.txt "$E/requirements.txt"
    touch "$E/.complete"
  fi
) 9>"$HOME/envs/{ename}.lock"
{{ echo "host=$(hostname)"; echo "nproc=$(nproc)"; lscpu | sed -n 's/^Model name: *//p' | sed 's/^/cpu=/'; free -g | awk '/^Mem:/{{print "mem_gib=" $2}}'; echo "python=$("$E/bin/python" -V 2>&1)"; }} > {META_DIR}/host
setsid nohup bash {META_DIR}/run.sh > {META_DIR}/run.log 2>&1 < /dev/null &
echo $! > {META_DIR}/pid
"""
    print(f"[{run_id}] checking env {ename} (mirrors local {a.venv}/) and starting ...", flush=True)
    ssh(a.host, remote, capture=False)

    local = LOCAL_RUNS / run_id
    local.mkdir(parents=True, exist_ok=True)
    dirty = git("status", "--porcelain")
    meta = {
        "run_id": run_id, "host": a.host, "command": command, "env": envs,
        "datasets": datasets or ("none" if a.no_data else "all"), "include": include,
        "shipped_files": n, "shipped_bytes": size, "launched_local": t0.isoformat(timespec="seconds"),
        "git_head": git("rev-parse", "HEAD"), "git_dirty": bool(dirty),
        "git_status": dirty.splitlines(), "python": py, "local_venv": a.venv, "remote_env": ename,
    }
    (local / "run_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"[{run_id}] running. Check with: python tools/remote_run.py status {run_id}")
    print(run_id)


STATUS_SH = r"""
show() {
  d="$1"; id=$(basename "$d"); m="$d/.remote_run"
  if [ -f "$m/exit" ]; then st="done exit=$(cat "$m/exit")"
  elif [ -f "$m/pid" ] && kill -0 "$(cat "$m/pid")" 2>/dev/null; then st="running"
  elif [ -f "$m/pid" ]; then st="died (no exit marker)"
  else st="not started"; fi
  start=$(cat "$m/started" 2>/dev/null); end=$(cat "$m/finished" 2>/dev/null)
  printf '%s  %s  started=%s finished=%s\n' "$id" "$st" "${start:--}" "${end:--}"
}
"""


def cmd_status(a) -> None:
    if a.run_id:
        script = STATUS_SH + f'show "$HOME/runs/{a.run_id}"; echo "--- last log lines"; tail -n 5 "$HOME/runs/{a.run_id}/{META_DIR}/run.log"'
    else:
        script = STATUS_SH + 'for d in "$HOME"/runs/*/; do [ -d "$d" ] && show "${d%/}"; done; ls "$HOME"/runs 2>/dev/null | grep -q . || echo "no runs on remote"'
    print(ssh(a.host, script).stdout.decode(errors="replace"), end="")


def cmd_log(a) -> None:
    out = ssh(a.host, f'tail -n {int(a.n)} "$HOME/runs/{a.run_id}/{META_DIR}/run.log"').stdout
    print(out.decode(errors="replace"), end="")


def cmd_kill(a) -> None:
    script = f'p=$(cat "$HOME/runs/{a.run_id}/{META_DIR}/pid"); kill -TERM -- -"$p" && echo "sent TERM to process group $p"'
    print(ssh(a.host, script).stdout.decode(errors="replace"), end="")


def cmd_fetch(a) -> None:
    rdir = f"$HOME/runs/{a.run_id}"
    state = ssh(a.host, f'test -d "{rdir}" || {{ echo missing; exit 0; }}; '
                        f'if [ -f "{rdir}/{META_DIR}/exit" ]; then echo done; '
                        f'elif kill -0 "$(cat {rdir}/{META_DIR}/pid 2>/dev/null)" 2>/dev/null; then echo running; '
                        f'else echo died; fi').stdout.decode().strip()
    if state == "missing":
        sys.exit(f"{a.run_id} does not exist on {a.host}")
    if state == "running" and not a.keep:
        sys.exit(f"{a.run_id} is still running; wait, or fetch a partial copy with --keep")

    find = (f'cd "{rdir}" && find . -type f -newer {META_DIR}/shipped ! -path "./{META_DIR}/shipped" '
            f'! -path "*/__pycache__/*" -print0')
    count = int(ssh(a.host, find + " | tr -cd '\\0' | wc -c").stdout.decode().strip())

    dest = LOCAL_RUNS / a.run_id
    dest.mkdir(parents=True, exist_ok=True)
    proc = subprocess.Popen(
        ["ssh", "-o", "BatchMode=yes", a.host, "bash -s"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
    )
    proc.stdin.write((find + " | tar --null -czf - -T -\n").encode())
    proc.stdin.close()
    got = []
    with tarfile.open(fileobj=proc.stdout, mode="r|gz") as tar:
        for member in tar:
            tar.extract(member, dest, filter="data")
            if member.isfile():
                name = member.name
                got.append(name[2:] if name.startswith("./") else name)
    if proc.wait() != 0 or len(got) != count:
        sys.exit(f"fetch incomplete: expected {count} files, got {len(got)}; remote copy kept")

    host_info = (dest / META_DIR / "host")
    meta_path = dest / "run_meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {"run_id": a.run_id}
    for name in ("started", "finished", "exit"):
        f = dest / META_DIR / name
        meta[f"remote_{name}"] = f.read_text().strip() if f.exists() else None
    if host_info.exists():
        meta["remote_host"] = dict(l.split("=", 1) for l in host_info.read_text().splitlines() if "=" in l)
    meta["state_at_fetch"] = state
    meta["fetched_files"] = sorted(got)
    meta["fetched_local"] = dt.datetime.now().isoformat(timespec="seconds")
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    outputs = [g for g in got if not g.startswith(f"{META_DIR}/")]
    print(f"fetched {len(got)} files ({len(outputs)} outputs) into {dest.relative_to(REPO).as_posix()}/")
    for g in sorted(outputs)[:40]:
        print("  " + g)
    if len(outputs) > 40:
        print(f"  ... {len(outputs) - 40} more, full list in run_meta.json")
    print(f"exit code: {meta.get('remote_exit')}")

    if a.keep or state == "running":
        print(f"remote copy kept at ~/runs/{a.run_id}")
    else:
        ssh(a.host, f'rm -rf "{rdir}"')
        print("remote copy deleted")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", default=DEFAULT_HOST)
    sub = ap.add_subparsers(dest="sub", required=True)

    r = sub.add_parser("run")
    r.add_argument("--label")
    g = r.add_mutually_exclusive_group()
    g.add_argument("--data", help="comma-separated dataset ids from benchmark/datasets.py; default: all of data/")
    g.add_argument("--no-data", action="store_true")
    r.add_argument("--include", action="append", help="extra repo-relative path to ship (repeatable)")
    r.add_argument("--env", action="append", help="KEY=VALUE exported for the run (repeatable)")
    r.add_argument("--venv", default="env", help="local venv the remote env mirrors (default: env)")
    r.add_argument("cmd", nargs=argparse.REMAINDER)

    s = sub.add_parser("status"); s.add_argument("run_id", nargs="?")
    l = sub.add_parser("log"); l.add_argument("run_id"); l.add_argument("-n", default=40)
    f = sub.add_parser("fetch"); f.add_argument("run_id"); f.add_argument("--keep", action="store_true")
    k = sub.add_parser("kill"); k.add_argument("run_id")

    a = ap.parse_args()
    if a.sub == "run" and a.cmd and a.cmd[0] == "--":
        a.cmd = a.cmd[1:]
    {"run": cmd_run, "status": cmd_status, "log": cmd_log, "fetch": cmd_fetch, "kill": cmd_kill}[a.sub](a)


if __name__ == "__main__":
    main()
