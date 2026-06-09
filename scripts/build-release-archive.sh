#!/usr/bin/env bash
# Build a macOS release tarball for one lib/darwin/<arch> layout.
# Usage: build-release-archive.sh <version> <os> <arch>
# Example: build-release-archive.sh 1.2.3 darwin arm64
set -euo pipefail

VERSION="${1:?version required}"
OS="${2:?os required (darwin)}"
ARCH="${3:?arch required (arm64|x86_64)}"

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIST="${ROOT}/dist"
STAGING="$(mktemp -d)"
ARCHIVE_NAME="aklog-${VERSION}-${OS}-${ARCH}"
ARCHIVE_PATH="${DIST}/${ARCHIVE_NAME}.tar.gz"
LIB_SRC="${ROOT}/lib/${OS}/${ARCH}"

cleanup() {
  rm -rf "${STAGING}"
}
trap cleanup EXIT

mkdir -p "${DIST}"
mkdir -p "${STAGING}/lib/${OS}/${ARCH}"

if [ -e "${ROOT}/aklog" ]; then
  cp "${ROOT}/aklog" "${STAGING}/aklog"
fi
if [ -d "${ROOT}/src" ]; then
  rsync -a \
    --exclude='*.egg-info' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    "${ROOT}/src/" "${STAGING}/src/"
fi
for item in pyproject.toml README.md; do
  if [ -e "${ROOT}/${item}" ]; then
    cp "${ROOT}/${item}" "${STAGING}/${item}"
  fi
done
if [ -d "${ROOT}/contrib" ]; then
  rsync -a "${ROOT}/contrib/" "${STAGING}/contrib/"
fi
if [ -f "${ROOT}/lib/README.md" ]; then
  mkdir -p "${STAGING}/lib"
  cp "${ROOT}/lib/README.md" "${STAGING}/lib/README.md"
fi

if [ -d "${LIB_SRC}" ]; then
  shopt -s dotglob nullglob
  for f in "${LIB_SRC}"/*; do
    base="$(basename "$f")"
    [ "$base" = ".gitkeep" ] && continue
    cp -R "$f" "${STAGING}/lib/${OS}/${ARCH}/"
  done
  shopt -u dotglob nullglob
  tool_count="$(find "${STAGING}/lib/${OS}/${ARCH}" -type f ! -name '.gitkeep' | wc -l | tr -d ' ')"
  if [ "${tool_count}" -eq 0 ]; then
    echo "warning: no bundled tools in lib/${OS}/${ARCH}/ (only .gitkeep?)" >&2
  fi
else
  echo "warning: missing lib/${OS}/${ARCH}/" >&2
fi

tar -czf "${ARCHIVE_PATH}" -C "${STAGING}" .
SHA256="$(shasum -a 256 "${ARCHIVE_PATH}" | awk '{print $1}')"
echo "${SHA256}" > "${DIST}/${ARCHIVE_NAME}.sha256"
echo "built ${ARCHIVE_PATH} sha256=${SHA256}"
