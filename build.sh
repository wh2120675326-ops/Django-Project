#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

# Optional local helper. Render uses the PPT command directly:
# pip install -r requirements.txt
python -m pip install -r requirements.txt
