#!/bin/sh
# Copy the latest generated meshes into the web viewer and reload the service.
set -e
cd "$(dirname "$0")/.."
mkdir -p web/parts
cp cad/cq/*.stl web/parts/
systemctl --user restart submission-web.service 2>/dev/null || true
echo "viewer synced: $(ls web/parts | wc -l) meshes"
