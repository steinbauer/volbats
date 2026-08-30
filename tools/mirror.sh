#!/usr/bin/env bash
# Stáhne statickou kopii https://volbats.cz/ do adresáře site/.
# Zdroj je malý web (cca 5 sekcí + detaily kandidátů a priorit), takže bereme celý.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="${1:-$ROOT/site}"
SRC="${MIRROR_URL:-https://volbats.cz/}"

rm -rf "$OUT"
mkdir -p "$OUT"

# --restrict-file-names=windows převede '?' v názvech na '@', aby šly soubory
# servírovat ze statického hostingu; odkazy si wget přepíše sám.
wget \
  --recursive --level=inf \
  --page-requisites \
  --convert-links \
  --adjust-extension \
  --restrict-file-names=windows \
  --domains=volbats.cz \
  --no-host-directories \
  --directory-prefix="$OUT" \
  --wait=0.2 --random-wait --tries=3 --timeout=30 \
  --user-agent='Mozilla/5.0 (X11; Linux x86_64) volbats-mirror' \
  "$SRC" || true

# GitHub Pages jinak přeskočí adresáře začínající podtržítkem a pouští Jekyll
touch "$OUT/.nojekyll"


# --- Úklid po wgetu -------------------------------------------------------
# wget uloží URL s query stringem pod názvem typu `style.css@v=0.3.7.css`
# a v HTML nechá dvojitě zakódovaný odkaz. Přejmenujeme na čistá jména
# a přepíšeme odkazy, ať se s tím pak nemusíme prát při úpravách.
normalize() {
  local from="$1" to="$2" from_enc
  [ -f "$OUT/$from" ] || return 0
  mv "$OUT/$from" "$OUT/$to"
  from_enc="${from//%/%25}"
  find "$OUT" -name '*.html' -type f -exec \
    sed -i -e "s|${from//|/\\|}|${to}|g" -e "s|${from_enc//|/\\|}|${to}|g" {} +
}

normalize 'theme/volbats2022/style.css@v=0.3.7.css' 'theme/volbats2022/style.css'
normalize 'assets/fonts/index.html@family=roboto%3A300,400,700.css' 'assets/fonts/roboto.css'

# Fonty visí na cdn.polyweb.cz — stáhneme je k sobě, ať je kopie soběstačná.
FONTS="$OUT/assets/fonts"
if [ -f "$FONTS/roboto.css" ]; then
  mkdir -p "$FONTS/files"
  grep -oE "https://cdn\.polyweb\.cz/[^')?]*" "$FONTS/roboto.css" | sort -u | \
  while read -r url; do
    wget -q -O "$FONTS/files/$(basename "$url")" "$url" || true
  done
  sed -i "s|https://cdn\.polyweb\.cz/asset/fonts/|files/|g" "$FONTS/roboto.css"
fi

echo "Po úklidu: $(find "$OUT" -type f | wc -l) souborů, $(du -sh "$OUT" | cut -f1)"
