#!/usr/bin/env python3
"""
Live bridge to a RUNNING FreeCAD GUI on optiplex-1 over Tailscale.

On the OptiPlex, in FreeCAD: View -> Panels -> Python console, run once:

    import Web
    Web.startServer("100.124.11.55", 54880)

Then from NZXT:

    python3 tools/fc_live.py ping
    python3 tools/fc_live.py docs
    python3 tools/fc_live.py import      # fresh document, no duplicates
    python3 tools/fc_live.py exec "code"

Rules learned the hard way:
  - the server handles ONE connection at a time; ALWAYS shut down cleanly
  - responses are capped ~1 KB, so never return big strings
  - App.listDocuments() is a DICT, not a list
  - never kill a client mid-send; it wedges the server
"""
import socket, sys, os

HOST = os.environ.get("FC_HOST", "100.124.11.55")
PORT = int(os.environ.get("FC_PORT", "54880"))
STEP = "/home/filip/sub-mission/cad/cq/probe_assembly.step"


def send(code: str, timeout: float = 25.0) -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((HOST, PORT))
    except OSError as e:
        return "ERR: cannot reach %s:%d (%s)" % (HOST, PORT, e)
    try:
        s.sendall(code.encode())
        chunks, total = [], 0
        while total < 1000:
            try:
                d = s.recv(4096)
            except socket.timeout:
                break
            if not d:
                break
            chunks.append(d)
            total += len(d)
        return b"".join(chunks).decode(errors="replace")
    finally:
        try:
            s.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        s.close()


def ping():
    return send("p = 1 + 1")


def docs():
    return send("import FreeCAD as App; "
                "r = '; '.join('%s:%d' % (d.Name, len(d.Objects)) "
                "for d in App.listDocuments().values()); r")


def fresh_import():
    code = (
        "import FreeCAD as App, Import, FreeCADGui as Gui\n"
        "name = 'probe_live'\n"
        "if name in App.listDocuments():\n"
        "    App.closeDocument(name)\n"
        "doc = App.newDocument(name)\n"
        "Import.insert('%s', doc.Name)\n"
        "doc.recompute()\n"
        "Gui.activeDocument().activeView().viewAxometric()\n"
        "Gui.SendMsgToActiveView('ViewFit')\n"
        "r = 'imported %%d objects' %% (len(doc.Objects),)\n" % STEP
    )
    return send(code, timeout=180)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    cmd = sys.argv[1]
    if cmd == "ping":
        print(repr(ping()))
    elif cmd == "docs":
        print(docs())
    elif cmd == "import":
        print(fresh_import())
    elif cmd == "exec":
        print(send(sys.argv[2], timeout=120))
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
