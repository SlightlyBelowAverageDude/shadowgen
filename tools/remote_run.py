"""Run an experiment on a remote box and bring the outputs back.

Nothing of the project is kept on the remote. Each run ships a snapshot of the
working tree (uncommitted edits included), runs one command there detached,
and `fetch` copies every file the run created or changed into
remote_runs/<run-id>/ here, then deletes the remote copy. Original result files
in this checkout are never touched.

Each run records what it shipped next to run_meta.json: the hash of every file,
the diff against HEAD, and the untracked files themselves. A run id names one
directory under ~/runs; commands refuse anything else, and `fetch` deletes only
a directory that carries the ship marker of that run.

Text files are shipped with the line endings git stores (LF), so the remote tree
equals a Linux checkout plus the local edits.

The remote keeps only uv, uv-managed CPython builds, and virtualenvs under
~/envs. Each remote env mirrors a local venv (env/ by default, the one the
benchmark scripts name): same Python version, same package versions from its
freeze, minus Windows-only packages. A changed local venv gives a new env.
uv itself must be present on the remote (~/.local/bin/uv); the script does not
install it.

Usage (from the repo root, with the project's Python):
  python tools/remote_run.py [--host H] run [--label NAME] [--data D1,D3 | --no-data]
                                           [--include PATH ...] [--env K=V ...]
                                           [--venv env|.venv] -- CMD ...
  python tools/remote_run.py [--host H] status [RUN_ID]
  python tools/remote_run.py [--host H] log RUN_ID [-n LINES]
  python tools/remote_run.py [--host H] fetch RUN_ID [--keep]
  python tools/remote_run.py [--host H] kill RUN_ID [--force]

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
SSH = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=15", "-o", "ServerAliveInterval=30"]

# Shipped on every run, relative to the repo root.
BASE_INCLUDE = ["HybridGen", "benchmark", "shadowgen.py", "pyproject.toml", "uv.lock", ".python-version"]
SKIP_DIRS = {"__pycache__", ".ipynb_checkpoints", ".git", ".venv"}
# Top-level directories that are never shipped, whatever --include says.
TOP_SKIP = {".git", ".venv", "env", "remote_runs"}
SKIP_SUFFIXES = {".pyc", ".pyo"}
# Line endings: a tracked file is shipped as git stores it. An untracked file with one of these
# suffixes is treated as text (CRLF -> LF), which is what git would store once it is added.
TEXT_SUFFIXES = {".sh", ".py", ".json", ".md", ".txt", ".toml", ".cfg", ".csv", ".yml", ".yaml"}
LFS_HEAD = b"version https://git-lfs.github.com/spec/"

UV = "$HOME/.local/bin/uv"
META_DIR = ".remote_run"
# Left out of the remote env (no Linux build, or the installer itself).
WIN_ONLY = {"pywin32", "pywinpty", "pywin32-ctypes", "winpty", "wmi", "comtypes", "pip"}
# A run id is one path component, <date>-<time>-<label>. Every command that takes one checks it,
# so no other remote path can be read, signalled or deleted through a run id.
RUN_ID_RE = re.compile(r"\d{8}-\d{6}-[A-Za-z0-9_.-]+")
ENV_KEY_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
# Untracked shipped files up to this size are copied next to run_meta.json; larger ones are hashed only.
UNTRACKED_COPY_LIMIT = 5 * 2**20

# Shell functions shared by status, kill and fetch. Every process of a run inherits
# REMOTE_RUN_ID=<run id>, so the run's processes are found by that variable. A pid alone is
# never trusted: the system may have given it to another process.
LIVE_SH = r"""
env_ids() {
  for e in /proc/[0-9]*/environ; do
    { tr '\0' '\n' < "$e"; } 2>/dev/null | sed -n 's/^REMOTE_RUN_ID=//p'
  done | sort -u
}
run_pids() {
  for e in /proc/[0-9]*/environ; do
    if { tr '\0' '\n' < "$e"; } 2>/dev/null | grep -qxF "REMOTE_RUN_ID=$1"; then
      e=${e#/proc/}; echo "${e%/environ}"
    fi
  done
}
"""


# ---------------------------------------------------------------- helpers

def ssh(host: str, script: str, *, check: bool = True, capture: bool = True) -> subprocess.CompletedProcess:
    proc = subprocess.run(
        [*SSH, host, "bash -s"],
        input=script.encode(), stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )
    if check and proc.returncode != 0:
        err = (proc.stderr or b"").decode(errors="replace")
        out = (proc.stdout or b"").decode(errors="replace")
        sys.exit(f"remote command failed (exit {proc.returncode}):\n{out}{err}")
    return proc


def check_run_id(run_id: str) -> str:
    if not RUN_ID_RE.fullmatch(run_id or ""):
        sys.exit(f"not a run id: {run_id!r} (expected YYYYMMDD-HHMMSS-label)")
    return run_id


def remove_remote(host: str, run_id: str, *, need_marker: bool) -> bool:
    """Delete ~/runs/<run_id> on the remote. With need_marker only a directory with the ship marker. True if gone."""
    check_run_id(run_id)
    guard = f'test -f "$d/{META_DIR}/shipped" && ' if need_marker else ""
    proc = ssh(host, f'd="$HOME/runs/{run_id}"; {guard}rm -rf "$d"; test ! -e "$d"', check=False)
    return proc.returncode == 0


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
        line = line.strip()
        name = re.split(r"[=<>@ ;]", line, maxsplit=1)[0].lower().replace("_", "-")
        if not name or name in WIN_ONLY or line.startswith("-e "):
            continue
        if " @ file:" in line:
            sys.exit(f"{venv}/ holds a package installed from a local path, which the remote env cannot mirror:\n  {line}")
        keep.append(line)
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


def git_eol() -> tuple[set, set]:
    """(tracked paths, tracked paths that git stores with LF while the checkout holds CRLF)."""
    out = subprocess.run(["git", "ls-files", "--eol", "-z"], cwd=REPO, capture_output=True).stdout
    tracked, crlf = set(), set()
    for rec in out.decode("utf-8", "replace").split("\0"):
        info, tab, path = rec.partition("\t")
        if not tab:
            continue
        tracked.add(path)
        f = info.split()
        if len(f) >= 2 and f[0] == "i/lf" and f[1] in ("w/crlf", "w/mixed") and "-text" not in "".join(f[2:]):
            crlf.add(path)
    return tracked, crlf


def shipped_bytes(fp: Path, arc: str, eol: tuple[set, set]) -> bytes:
    """Content of a file as it is shipped (line endings as git stores them)."""
    data = fp.read_bytes()
    tracked, crlf = eol
    if arc in tracked:
        return data.replace(b"\r\n", b"\n") if arc in crlf else data
    if fp.suffix.lower() in TEXT_SUFFIXES and b"\0" not in data[:8000]:
        return data.replace(b"\r\n", b"\n")
    return data


def collect_files(include: list[str]) -> list[tuple[Path, str]]:
    """All files to ship as (path, archive name). Checks every include path before anything is sent."""
    files, seen, pointers = [], set(), []
    for rel in include:
        p = (REPO / rel).resolve()
        if p != REPO and REPO not in p.parents:
            sys.exit(f"include path is outside the repository: {rel}")
        if not p.exists():
            sys.exit(f"include path not found: {rel}")
        top = p.relative_to(REPO).parts[:1]
        if top and top[0] in TOP_SKIP:
            sys.exit(f"include path is never shipped: {rel}")
        if p.is_file():
            found = [p]
        else:
            found = []
            for root, dirs, names in os.walk(p):
                at_top = Path(root) == REPO
                dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not (at_top and d in TOP_SKIP)]
                found += [Path(root) / f for f in names]
        for fp in found:
            if fp.suffix in SKIP_SUFFIXES or fp in seen:
                continue
            seen.add(fp)
            if fp.stat().st_size < 1024:
                with open(fp, "rb") as fh:
                    if fh.read(len(LFS_HEAD)) == LFS_HEAD:
                        pointers.append(fp.relative_to(REPO).as_posix())
            files.append((fp, fp.relative_to(REPO).as_posix()))
    if pointers:
        sys.exit("these files are Git LFS pointers, the data is not checked out (git lfs pull):\n  " + "\n  ".join(pointers[:20]))
    return files


def write_snapshot(stream, files, eol) -> tuple[int, int, dict]:
    """Stream the files as tar.gz. Returns count, bytes, and {path: sha256 and size of the shipped bytes}."""
    n = size = 0
    manifest = {}
    with gzip.GzipFile(fileobj=stream, mode="wb", compresslevel=1) as gz:
        with tarfile.open(fileobj=gz, mode="w|", format=tarfile.PAX_FORMAT) as tar:
            for fp, arc in files:
                st = fp.stat()
                data = shipped_bytes(fp, arc, eol)
                ti = tarfile.TarInfo(arc)
                ti.size = len(data)
                ti.mtime = int(st.st_mtime)
                ti.mode = 0o755 if fp.suffix == ".sh" else 0o644
                tar.addfile(ti, io.BytesIO(data))
                manifest[arc] = {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
                n += 1
                size += len(data)
    return n, size, manifest


def save_provenance(dest: Path, include: list[str], manifest: dict, eol) -> dict:
    """Record what was shipped, so a result can be traced to its code without the remote copy.

    shipped_manifest.json   sha256 and size of every shipped file (bytes as shipped, text files with LF)
    shipped_changes.patch   git diff of the shipped paths against HEAD (tracked files with edits)
    shipped_untracked/      the untracked shipped files themselves (up to UNTRACKED_COPY_LIMIT each)
    Files ignored by git (run logs, cached models) are in the manifest only.
    """
    (dest / "shipped_manifest.json").write_text(json.dumps(manifest, indent=1, sort_keys=True), encoding="utf-8")
    diff = subprocess.run(["git", "diff", "HEAD", "--binary", "--", *include], cwd=REPO, capture_output=True).stdout
    if diff:
        (dest / "shipped_changes.patch").write_bytes(diff)
    listed = subprocess.run(["git", "ls-files", "--others", "--exclude-standard", "-z", "--", *include],
                            cwd=REPO, capture_output=True).stdout.decode("utf-8", "replace").split("\0")
    copied, hashed_only, changed = [], [], []
    for rel in filter(None, listed):
        if rel not in manifest:
            continue
        src = REPO / rel
        if not src.exists() or src.stat().st_size > UNTRACKED_COPY_LIMIT:
            hashed_only.append(rel)
            continue
        if hashlib.sha256(shipped_bytes(src, rel, eol)).hexdigest() != manifest[rel]["sha256"]:
            changed.append(rel)
        out = dest / "shipped_untracked" / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(src.read_bytes())
        copied.append(rel)
    return {"shipped_manifest": "shipped_manifest.json",
            "shipped_changes": "shipped_changes.patch" if diff else None,
            "untracked_copied": sorted(copied), "untracked_hashed_only": sorted(hashed_only),
            "untracked_changed_since_ship": sorted(changed)}


def write_meta(local: Path, meta: dict) -> None:
    (local / "run_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")


# ---------------------------------------------------------------- commands

def cmd_run(a) -> None:
    py, freeze, ekey = venv_spec(a.venv)
    ename = f"py{py}-{ekey}"
    label = re.sub(r"[^A-Za-z0-9_.-]+", "-", a.label or "run").strip("-") or "run"
    run_id = check_run_id(f"{dt.datetime.now():%Y%m%d-%H%M%S}-{label}")
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
        k, eq, v = kv.partition("=")
        if not eq or not ENV_KEY_RE.fullmatch(k):
            sys.exit(f"--env expects KEY=VALUE with a plain variable name, got {kv!r}")
        envs[k] = v

    # 0. everything that can fail locally fails before the remote is touched
    files = collect_files(include)
    eol = git_eol()

    # 1. create the run directory (never reuse one), check the one remote prerequisite
    prep = f"""
if [ ! -x "{UV}" ]; then echo NO_UV; exit 0; fi
mkdir -p "$HOME/runs"
if ! mkdir "{rdir}" 2>/dev/null; then echo EXISTS; exit 0; fi
mkdir "{rdir}/{META_DIR}" && echo OK
"""
    answer = ssh(a.host, prep).stdout.decode().strip()
    if answer == "NO_UV":
        sys.exit(f"uv is missing on {a.host} (~/.local/bin/uv). Install it there once:\n"
                 f"  curl -LsSf https://astral.sh/uv/install.sh | sh")
    if answer == "EXISTS":
        sys.exit(f"{run_id} already exists on {a.host}; start again (the id carries the second of the launch)")
    if answer != "OK":
        sys.exit(f"could not create the run directory on {a.host}: {answer!r}")

    # 2. ship the snapshot; a failed or interrupted ship leaves nothing behind
    print(f"[{run_id}] shipping to {a.host} ...", flush=True)
    t0 = dt.datetime.now()
    proc = None
    try:
        proc = subprocess.Popen(
            [*SSH, a.host, f'tar -xzf - -C {rdir} && touch {rdir}/{META_DIR}/shipped'],
            stdin=subprocess.PIPE,
        )
        try:
            n, size, manifest = write_snapshot(proc.stdin, files, eol)
        finally:
            try:
                proc.stdin.close()
            except OSError:
                pass
        if proc.wait() != 0:
            raise RuntimeError("the remote side could not unpack the snapshot")
    except BaseException as e:
        if proc is not None and proc.poll() is None:
            proc.kill()
        gone = remove_remote(a.host, run_id, need_marker=False)
        what = "interrupted" if isinstance(e, KeyboardInterrupt) else f"failed ({type(e).__name__}: {e})"
        sys.exit(f"shipping {what}; remote copy {'removed' if gone else f'NOT removed, see ~/runs/{run_id}'}")
    secs = (dt.datetime.now() - t0).total_seconds()
    print(f"[{run_id}] shipped {n} files, {size / 2**20:.1f} MB in {secs:.1f} s", flush=True)

    # 3. local record, written before the start so a failed start is on file too
    local = LOCAL_RUNS / run_id
    local.mkdir(parents=True, exist_ok=True)
    dirty = git("status", "--porcelain")
    meta = {
        "run_id": run_id, "host": a.host, "command": command, "env": envs,
        "datasets": datasets or ("none" if a.no_data else "all"), "include": include,
        "shipped_files": n, "shipped_bytes": size, "launched_local": t0.isoformat(timespec="seconds"),
        "git_head": git("rev-parse", "HEAD"), "git_dirty": bool(dirty),
        "git_status": dirty.splitlines(), "python": py, "local_venv": a.venv, "remote_env": ename,
        "state": "shipped",
    }
    meta.update(save_provenance(local, include, manifest, eol))
    write_meta(local, meta)

    # 4. make sure the environment exists, 5. start detached
    exports = "\n".join(f"export {k}={shlex.quote(v)}" for k, v in envs.items())
    run_sh = f"""#!/usr/bin/env bash
cd "{rdir}" || exit 1
export REMOTE_RUN_ID={run_id}
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
    if {UV} venv -q --python {py} "$E" \\
       && {UV} pip install -q --python "$E/bin/python" -r {META_DIR}/requirements.txt \\
       && cp {META_DIR}/requirements.txt "$E/requirements.txt" && touch "$E/.complete"; then :
    else
      echo "env build failed; the partial env is removed"
      rm -rf "$E"
      rm -f "$HOME/envs/{ename}.lock"
      exit 1
    fi
  fi
  if [ ! -f "$E/installed.txt" ]; then
    {UV} pip freeze -q --python "$E/bin/python" > "$E/installed.txt.tmp"
    mv "$E/installed.txt.tmp" "$E/installed.txt"
  fi
) 9>"$HOME/envs/{ename}.lock"
cp "$E/installed.txt" {META_DIR}/installed.txt
{{ echo "host=$(hostname)"; echo "nproc=$(nproc)"; lscpu | sed -n 's/^Model name: *//p' | sed 's/^/cpu=/'; free -g | awk '/^Mem:/{{print "mem_gib=" $2}}'; echo "python=$("$E/bin/python" -V 2>&1)"; }} > {META_DIR}/host
REMOTE_RUN_ID={run_id} setsid nohup bash {META_DIR}/run.sh > {META_DIR}/run.log 2>&1 < /dev/null &
echo $! > {META_DIR}/pid
"""
    print(f"[{run_id}] checking env {ename} (mirrors local {a.venv}/) and starting ...", flush=True)
    started = ssh(a.host, remote, check=False, capture=False)
    if started.returncode != 0:
        gone = remove_remote(a.host, run_id, need_marker=True)
        meta["state"] = "start_failed"
        meta["start_exit"] = started.returncode
        write_meta(local, meta)
        sys.exit(f"[{run_id}] the start failed (exit {started.returncode}, output above); nothing ran. "
                 f"Remote copy {'removed' if gone else 'NOT removed'}; record in remote_runs/{run_id}/run_meta.json")
    meta["state"] = "started"
    write_meta(local, meta)
    print(f"[{run_id}] running. Check with: python tools/remote_run.py status {run_id}")
    print(run_id)


STATUS_SH = LIVE_SH + r"""
LIVE=$(env_ids)
show() {
  d="$1"; id=$(basename "$d"); m="$d/.remote_run"
  if printf '%s\n' "$LIVE" | grep -qxF "$id"; then live=1; else live=0; fi
  if [ -f "$m/exit" ]; then
    st="done exit=$(cat "$m/exit")"; [ "$live" = 1 ] && st="$st, processes still alive"
  elif [ "$live" = 1 ]; then st="running"
  elif [ -f "$m/killed" ]; then st="killed"
  elif [ -f "$m/pid" ]; then st="died (no exit marker)"
  elif [ -f "$m/shipped" ]; then st="shipped, not started"
  else st="incomplete ship"; fi
  start=$(cat "$m/started" 2>/dev/null); end=$(cat "$m/finished" 2>/dev/null)
  printf '%s  %s  started=%s finished=%s\n' "$id" "$st" "${start:--}" "${end:--}"
}
"""


def cmd_status(a) -> None:
    if a.run_id:
        check_run_id(a.run_id)
        script = STATUS_SH + (f'test -d "$HOME/runs/{a.run_id}/{META_DIR}" || {{ echo "{a.run_id} does not exist on the remote"; exit 0; }}; '
                              f'show "$HOME/runs/{a.run_id}"; echo "--- last log lines"; tail -n 5 "$HOME/runs/{a.run_id}/{META_DIR}/run.log"')
    else:
        script = STATUS_SH + 'for d in "$HOME"/runs/*/; do [ -d "$d" ] && show "${d%/}"; done; ls "$HOME"/runs 2>/dev/null | grep -q . || echo "no runs on remote"'
    print(ssh(a.host, script).stdout.decode(errors="replace"), end="")


def cmd_log(a) -> None:
    check_run_id(a.run_id)
    out = ssh(a.host, f'tail -n {int(a.n)} "$HOME/runs/{a.run_id}/{META_DIR}/run.log"').stdout
    print(out.decode(errors="replace"), end="")


def cmd_kill(a) -> None:
    check_run_id(a.run_id)
    sig = "KILL" if a.force else "TERM"
    script = LIVE_SH + f"""
id="{a.run_id}"; m="$HOME/runs/$id/{META_DIR}"
if [ ! -d "$m" ]; then echo "$id does not exist on the remote"; exit 0; fi
pids=$(run_pids "$id")
if [ -z "$pids" ]; then
  if [ -f "$m/exit" ]; then echo "already finished (exit $(cat "$m/exit")), no process left, nothing to kill"
  else echo "no live process of this run (it died or the host restarted), nothing to kill"; fi
  exit 0
fi
[ -f "$m/exit" ] || date -Is > "$m/killed"
kill -{sig} $pids 2>/dev/null
echo "sent {sig} to $(echo "$pids" | wc -w) process(es) of $id"
for i in 1 2 3 4 5 6; do [ -z "$(run_pids "$id")" ] && break; sleep 0.5; done
left=$(run_pids "$id" | wc -w)
if [ "$left" -gt 0 ]; then echo "$left process(es) still alive; repeat with --force to send KILL"
else echo "all processes of the run are gone"; fi
"""
    print(ssh(a.host, script).stdout.decode(errors="replace"), end="")


def cmd_fetch(a) -> None:
    check_run_id(a.run_id)
    rdir = f"$HOME/runs/{a.run_id}"
    # A run exists only with its ship marker; everything below (listing, copying, deleting) relies on it.
    state = ssh(a.host, LIVE_SH + f"""
d="{rdir}"; m="$d/{META_DIR}"
test -f "$m/shipped" || {{ echo missing; exit 0; }}
if [ -n "$(run_pids "{a.run_id}")" ]; then echo running
elif [ -f "$m/exit" ]; then echo done
elif [ -f "$m/killed" ]; then echo killed
elif [ -f "$m/pid" ]; then echo died
else echo unstarted; fi
""").stdout.decode().strip()
    if state == "missing":
        sys.exit(f"{a.run_id} does not exist on {a.host} (no ship marker)")
    if state not in ("done", "running", "killed", "died", "unstarted"):
        sys.exit(f"unexpected remote state {state!r}; nothing fetched, nothing deleted")
    if state == "running" and not a.keep:
        sys.exit(f"{a.run_id} still has live processes; wait, kill it, or fetch a partial copy with --keep")

    # The list is made once and both the count and the archive come from it. A file counts as
    # output if its inode changed after the ship marker was set (ctime, remote clock only: it
    # cannot be set by a program, so copies that keep an old modification time are found too).
    # pipefail: a failing find must fail the whole listing, never read as "0 files".
    listing = (f'set -o pipefail; cd "{rdir}" && find . -type f -cnewer {META_DIR}/shipped '
               f'! -path "./{META_DIR}/shipped" ! -path "./{META_DIR}/fetch_list" ! -path "*/__pycache__/*" -print0 '
               f"> {META_DIR}/fetch_list && tr -cd '\\0' < {META_DIR}/fetch_list | wc -c")
    count = int(ssh(a.host, listing).stdout.decode().strip())

    dest = LOCAL_RUNS / a.run_id
    dest.mkdir(parents=True, exist_ok=True)
    proc = subprocess.Popen(
        [*SSH, a.host, "bash -s"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
    )
    proc.stdin.write(f'cd "{rdir}" && tar --null -czf - -T {META_DIR}/fetch_list\n'.encode())
    proc.stdin.close()
    got = []
    try:
        with tarfile.open(fileobj=proc.stdout, mode="r|gz") as tar:
            for member in tar:
                tar.extract(member, dest, filter="data")
                if member.isfile():
                    name = member.name
                    got.append(name[2:] if name.startswith("./") else name)
    except (tarfile.TarError, OSError) as e:
        proc.kill()
        proc.wait()
        sys.exit(f"fetch failed after {len(got)} of {count} files ({type(e).__name__}: {e}); remote copy kept")
    rc = proc.wait()
    # tar exits 1 when a file changed while it was read: expected for a run that is still writing.
    if not (rc == 0 or (rc == 1 and state == "running")) or len(got) != count:
        sys.exit(f"fetch incomplete: expected {count} files, got {len(got)} (tar exit {rc}); remote copy kept")
    # Two remote names that differ only in case are one file on Windows: the second overwrote the first.
    clash = len({g.lower() for g in got}) != len(got) and os.name == "nt"

    host_info = (dest / META_DIR / "host")
    meta_path = dest / "run_meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {"run_id": a.run_id}
    for name in ("started", "finished", "exit", "killed"):
        f = dest / META_DIR / name
        meta[f"remote_{name}"] = f.read_text().strip() if f.exists() else None
    if host_info.exists():
        meta["remote_host"] = dict(l.split("=", 1) for l in host_info.read_text().splitlines() if "=" in l)
    meta["state_at_fetch"] = state
    meta["state"] = "partial copy" if state == "running" else "fetched"
    meta["fetched_files"] = sorted(got)
    meta["fetched_local"] = dt.datetime.now().isoformat(timespec="seconds")
    write_meta(dest, meta)

    outputs = [g for g in got if not g.startswith(f"{META_DIR}/")]
    print(f"fetched {len(got)} files ({len(outputs)} outputs) into {dest.relative_to(REPO).as_posix()}/")
    for g in sorted(outputs)[:40]:
        print("  " + g)
    if len(outputs) > 40:
        print(f"  ... {len(outputs) - 40} more, full list in run_meta.json")
    print(f"exit code: {meta.get('remote_exit')}" + (" (killed)" if state == "killed" else ""))

    if clash:
        print(f"remote file names differ only in case, so one overwrote the other here; remote copy kept at ~/runs/{a.run_id}")
    elif a.keep or state == "running":
        print(f"remote copy kept at ~/runs/{a.run_id}")
    elif remove_remote(a.host, a.run_id, need_marker=True):
        print("remote copy deleted")
    else:
        print(f"remote copy NOT deleted (check ~/runs/{a.run_id} on {a.host})")


def main() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")  # remote logs may hold characters the console cannot show
        except (AttributeError, ValueError):
            pass
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
    k = sub.add_parser("kill"); k.add_argument("run_id"); k.add_argument("--force", action="store_true", help="send KILL instead of TERM")

    a = ap.parse_args()
    if a.sub == "run" and a.cmd and a.cmd[0] == "--":
        a.cmd = a.cmd[1:]
    {"run": cmd_run, "status": cmd_status, "log": cmd_log, "fetch": cmd_fetch, "kill": cmd_kill}[a.sub](a)


if __name__ == "__main__":
    main()
