"""Per-worker XDG isolation for the end-to-end suite.

The ovoscope job runs pytest under xdist, so several MiniCroft instances boot
in parallel. Each loads this skill into ``$XDG_CONFIG_HOME/mycroft/skills`` and
its file-system dir; sharing one directory across workers races and one load
fails with ``FileExistsError``. Give every worker its own HOME/XDG tree so the
concurrent skill loads never collide.
"""
import os
import tempfile


def _isolate_xdg() -> None:
    worker = os.environ.get("PYTEST_XDIST_WORKER", "main")
    root = os.path.join(tempfile.gettempdir(), f"easter-eggs-e2e-{worker}")
    for sub, var in (
        ("home", "HOME"),
        ("config", "XDG_CONFIG_HOME"),
        ("data", "XDG_DATA_HOME"),
        ("cache", "XDG_CACHE_HOME"),
        ("state", "XDG_STATE_HOME"),
    ):
        path = os.path.join(root, sub)
        os.makedirs(path, exist_ok=True)
        os.environ[var] = path


_isolate_xdg()
