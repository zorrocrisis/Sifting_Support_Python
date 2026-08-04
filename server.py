"""
server.py
---------
Serves the dashboard on a free local port and shuts the process down
automatically once every browser session has disconnected (useful when
this script is launched as a child process by an external host, e.g. a
C# game client, that expects it to exit cleanly on its own).
"""

import os
import socket
import threading
import sys

import panel as pn

_session_count = 0
_lock = threading.Lock()
_shutdown_timer = None


def find_free_port(start_port=5006):
    """Find the first available TCP port starting at `start_port`."""
    port = start_port
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind(("127.0.0.1", port))
                return port
            except OSError:
                port += 1


def _cancel_pending_shutdown():
    global _shutdown_timer
    if _shutdown_timer is not None:
        _shutdown_timer.cancel()
        _shutdown_timer = None


def _on_session_created(session_context):
    global _session_count
    with _lock:
        _session_count += 1
        _cancel_pending_shutdown()


def _on_session_destroyed(session_context):
    global _session_count, _shutdown_timer
    with _lock:
        _session_count -= 1
        if _session_count <= 0:
            # Debounce in case this is just a page refresh reconnecting.
            _cancel_pending_shutdown()
            _shutdown_timer = threading.Timer(0.0, _maybe_exit)
            _shutdown_timer.daemon = True
            _shutdown_timer.start()


def _maybe_exit():
    with _lock:
        if _session_count <= 0:
            os._exit(0)  # hard exit; the tornado IOLoop won't shut down cleanly otherwise

def _watch_stdin_for_eof():
    """
    Runs on a background daemon thread for the lifetime of the process.

    The C# host (PythonBridge.StopAllPythonProcesses) now simply closes its
    end of stdin on shutdown, which is a standard OS-level EOF signal. 
    sys.stdin.readline() returns "" exactly once,
    when the pipe is closed -- at that point we know the parent is gone and
    it's safe to exit immediately.

    Not used at all when running standalone via `python main_demo.py` with a
    real terminal attached -- stdin simply never hits EOF in that case, so
    this thread just sits blocked on readline() harmlessly for the life of
    the process.
    """
    while True:
        line = sys.stdin.readline()
        if line == "":
            break
    os._exit(0)  # hard exit; consistent with _maybe_exit's shutdown path


def serve_dashboard(dashboard, title="Log Dendrogram Explorer"):
    """Serve `dashboard`, retrying on the next port if one is already in use."""
    pn.state.on_session_created(_on_session_created)
    pn.state.on_session_destroyed(_on_session_destroyed)

    stdin_watcher = threading.Thread(target=_watch_stdin_for_eof, daemon=True)
    stdin_watcher.start()

    for attempt in range(10):
        port = find_free_port(start_port=5006 + attempt)
        os.environ["BOKEH_ALLOW_WS_ORIGIN"] = f"127.0.0.1:{port},localhost:{port}"

        try:
            pn.serve(dashboard, title=title, port=port, host="127.0.0.1", show=True)
            return
        except OSError as exc:
            if getattr(exc, "winerror", None) != 10048:
                raise

    raise RuntimeError("Unable to start the dashboard because all available ports were busy.")
