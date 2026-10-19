#!/usr/bin/env python3
"""
Live bridge to a RUNNING FreeCAD GUI via its built-in Web workbench server.

In FreeCAD's Python console (View -> Panels -> Python console), run once:

    import Web; Web.startServer("127.0.0.1", 54880)

Then from a shell:

    python3 tools/fc_live.py ping
    python3 tools/fc_live.py import   # load the probe STEP into the live doc
    python3 tools/fc_live.py shot     # save a viewport screenshot
    python3 tools/fc_live.py exec "print(App.listDocuments())"

Haven, 2026-10-19. Local-only (127.0.0.1). Executes Python in the GUI thread,
so documents/viewport update in front of you.
"""
import socket, sys, os, time

HOST, PORT = "127.0.0.1", 54880
STEP = "/home/filip/sub-mission/cad/cq/probe_assembly.step"


def send(code: str, timeout: float = 60.0) -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((HOST, PORT))
    except ConnectionRefusedError:
        return ("ERR: no FreeCAD server on %s:%d. In FreeCAD's Python console run:\n"
                "  import Web; Web.startServer(\"127.0.0.1\", %d)" % (HOST, PORT, PORT))
    try:
        s.sendall(code.encode())
        chunks = []
        while True:
            try:
                d = s.recv(65536)
            except socket.timeout:
                break
            if not d:
                break
            chunks.append(d)
            if len(d) < 65536:
                break
        return b"".join(chunks).decode(errors="replace")
    finally:
        s.close()


def cmd_ping():
    return send("print('PONG', App.Version()[0]+'.'+App.Version()[1])")


def cmd_import():
    # import STEP into whatever document is active, or a new one
    code = f'''
import FreeCAD as App, Import
doc = App.activeDocument()
if doc is None:
    doc = App.newDocument("probe")
Import.insert("{STEP}", doc.Name)
doc.recompute()
Gui.activeDocument().activeView().viewAxometric()
Gui.activeDocument().activeView().fitAll()
print("imported into", doc.Name, "objects:", len(doc.Objects))
'''
    return send(code, timeout=180)


def cmd_shot(path="/tmp/freecad_live.png"):
    code = f'''
import FreeCADGui as Gui
v = Gui.activeDocument().activeView()
v.saveImage("{path}", 1600, 1000, "White")
print("saved {path}")
'''
    return send(code)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    cmd = sys.argv[1]
    if cmd == "ping":
        print(cmd_ping())
    elif cmd == "import":
        print(cmd_import())
    elif cmd == "shot":
        out = sys.argv[2] if len(sys.argv) > 2 else "/tmp/freecad_live.png"
        print(cmd_shot(out))
    elif cmd == "exec":
        print(send(sys.argv[2], timeout=120))
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
