# Paste this ONE line-pair into the FreeCAD Python console ON THE OPTIPLEX:
#
#   import Web
#   Web.startServer("100.124.11.55", 54880)
#
# That exposes a Python-exec socket to the Tailscale network only.
# Haven (nzxt) then connects with: python3 tools/fc_live.py ping
#
# To stop it: restart FreeCAD (there is no clean stopServer in 1.1).
