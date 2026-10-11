#!/usr/bin/env bash
set -euo pipefail
rm -rf dist
bash build.sh >/dev/null 2>&1 || { echo "build.sh 执行失败"; exit 1; }
exp="lines=$(grep -c '[^[:space:]]' data.tsv)"
got="$(cat dist/output.txt)"
if [ "$got" != "$exp" ]; then
  echo "output 不一致: got=$got exp=$exp"
  exit 1
fi
echo "ops-01 verified"
