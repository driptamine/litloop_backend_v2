#!/bin/bash
# Concatenate all .credentials/*.env into a single .env file
set -e
cd "$(dirname "$0")/.."
output=".env"
echo "# Auto-generated from .credentials/*.env — do not edit directly" > "$output"
for f in .credentials/*.env; do
  [ -f "$f" ] || continue
  echo "# --- $(basename "$f") ---" >> "$output"
  cat "$f" >> "$output"
  echo "" >> "$output"
done
echo "Wrote $output ($(wc -l < "$output") lines)"
