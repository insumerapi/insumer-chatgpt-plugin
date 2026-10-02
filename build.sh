#!/usr/bin/env bash
# Build the plugin ZIP for the ChatGPT / Codex plugin directory.
#
#   ./build.sh            # vendors the skills, scans, writes dist/insumer-plugin-<version>.zip
#
# The five REST skills are vendored from ../insumer-agent-skills (the same
# source as the Grok plugin); SKILLS_SOURCE records the commit. The ZIP is
# refused if anything in it looks like a secret, an internal hostname, or a
# vendor name that never appears in public material.
set -euo pipefail
cd "$(dirname "$0")"

SKILLS_REPO="${SKILLS_REPO:-../insumer-agent-skills}"
VERSION="$(python3 -c 'import json;print(json.load(open("plugin.json"))["version"])')"
OUT="dist/insumer-plugin-${VERSION}.zip"

# 1. Vendor the skills (SKILL.md, references, scripts; no caches).
for s in insumer-auth insumer-attest insumer-trust insumer-trust-batch insumer-jwks-verify; do
  rm -rf "skills/$s"
  rsync -a --exclude '__pycache__' --exclude '*.pyc' "$SKILLS_REPO/skills/$s/" "skills/$s/"
done
git -C "$SKILLS_REPO" rev-parse HEAD > SKILLS_SOURCE
echo "skills vendored from insumer-agent-skills@$(cut -c1-7 SKILLS_SOURCE)"

# 2. Validate the manifests.
python3 - <<'EOF'
import json
p = json.load(open("plugin.json")); m = json.load(open("mcp.json"))
i = p["extensions"]["com.openai"]["interface"]
assert len(i["displayName"]) <= 30, "displayName > 30"
assert len(i["shortDescription"]) <= 30, "shortDescription > 30"
assert len(i["longDescription"]) <= 4000, "longDescription > 4000"
assert len(i["developerName"]) <= 80, "developerName > 80"
assert m["mcpServers"]["insumer"]["url"] == "https://api.insumermodel.com/mcp"
import re
for f in ("plugin.json", "mcp.json", "skills/insumer-hosted-tools/SKILL.md"):
    t = open(f, encoding="utf-8").read()
    assert "—" not in t, f"em dash in {f}"
print("manifests ok")
EOF

# 3. Leak scan over everything that will ship.
PATTERN='insr_live_[0-9a-f]{12,}|BEGIN [A-Z ]*PRIVATE KEY|cloudfunctions\.net|firebaseio|[Aa]lchemy|[Cc]ovalent|[Gg]old[Rr]ush|[Hh]elius|[Aa]nkr|publicnode|TronGrid|NowNodes|serviceAccount|npm_[A-Za-z0-9]{30,}'
if grep -rEn "$PATTERN" plugin.json mcp.json skills assets README.md LICENSE 2>/dev/null; then
  echo "REFUSED: the lines above must not ship." >&2
  exit 1
fi
# 64-hex strings are allowed only as the documented public EAS schema IDs.
if grep -rEn '0x[0-9a-fA-F]{64}' skills plugin.json mcp.json | grep -v 'schemaId' ; then
  echo "REFUSED: unexplained 64-hex value above (private key shaped)." >&2
  exit 1
fi
echo "leak scan clean"

# 4. Zip with the plugin root at the top level.
mkdir -p dist
rm -f "$OUT"
zip -q -r "$OUT" plugin.json mcp.json skills assets README.md LICENSE SKILLS_SOURCE -x '*/__pycache__/*' -x '*.pyc' -x '.DS_Store'
echo "wrote $OUT ($(du -h "$OUT" | cut -f1))"
unzip -l "$OUT" | tail -1
