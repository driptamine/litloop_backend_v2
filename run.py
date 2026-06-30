import os
import signal
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
VENV_BIN = os.path.join(HERE, "venv_3.9", "bin")


def env_with_venv():
    env = os.environ.copy()
    env["PATH"] = f"{VENV_BIN}:{env.get('PATH', '')}"
    env.setdefault("DJANGO_SETTINGS_MODULE", "litloop_project.settings.dev")
    return env


def main():
    env = env_with_venv()
    processes = []
    shutdown_requested = False

    def cleanup():
        nonlocal shutdown_requested
        if shutdown_requested:
            return
        shutdown_requested = True
        print("\nShutting down...")
        for proc in processes:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            except ProcessLookupError:
                pass
        time.sleep(3)
        for proc in processes:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except ProcessLookupError:
                pass
        for proc in processes:
            proc.wait()
        sys.exit(0)

    signal.signal(signal.SIGTERM, lambda s, f: cleanup())

    cmds = [
        [
            "gunicorn",
            "litloop_project.wsgi:application",
            "-b",
            "0.0.0.0:8001",
            "--reload",
        ],
        ["daphne", "-p", "8000", "litloop_project.asgi:application"],
        ["redis-server"],
        ["celery", "-A", "litloop_project", "worker", "-B", "-l", "info"],
    ]

    for cmd in cmds:
        proc = subprocess.Popen(cmd, env=env, preexec_fn=os.setpgrp)
        processes.append(proc)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        cleanup()


if __name__ == "__main__":
    main()
