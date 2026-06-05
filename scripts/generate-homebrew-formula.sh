#!/usr/bin/env bash
# Generate Formula/aklog.rb from template and release manifest.
# Usage: generate-homebrew-formula.sh <tag> <repo> <manifest.json>
# Env: RELEASE_DARWIN_ARM64, RELEASE_DARWIN_X86_64 (true|false)
set -euo pipefail

TAG="${1:?tag required (e.g. v1.2.3)}"
REPO="${2:?repo required (e.g. wswenyue/aklog)}"
MANIFEST="${3:?manifest path required}"

VERSION="${TAG#v}"
TEMPLATE="$(cd "$(dirname "$0")/.." && pwd)/.github/data/aklog.rb"
OUT="${4:-formula.rb}"

RELEASE_DARWIN_ARM64="${RELEASE_DARWIN_ARM64:-true}"
RELEASE_DARWIN_X86_64="${RELEASE_DARWIN_X86_64:-false}"

archive_url="https://github.com/${REPO}/archive/${TAG}.tar.gz"
archive_sha256=""

download_sha256() {
  local url="$1"
  local tmp
  tmp="$(mktemp)"
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL -o "${tmp}" "${url}"
  elif command -v wget >/dev/null 2>&1; then
    wget -q -O "${tmp}" "${url}"
  else
    echo "error: need curl or wget to fetch ${url}" >&2
    rm -f "${tmp}"
    return 1
  fi
  shasum -a 256 "${tmp}" | awk '{print $1}'
  rm -f "${tmp}"
}

url_arm64="" sha_arm64=""
url_x86="" sha_x86=""

if [ -f "${MANIFEST}" ]; then
  while IFS= read -r line; do
    arch="$(echo "$line" | jq -r '.arch')"
    url="$(echo "$line" | jq -r '.url')"
    sha256="$(echo "$line" | jq -r '.sha256')"
    case "${arch}" in
      arm64) url_arm64="$url"; sha_arm64="$sha256" ;;
      x86_64) url_x86="$url"; sha_x86="$sha256" ;;
    esac
  done < <(jq -c '.packages[]' "${MANIFEST}")
fi

if [ "${RELEASE_DARWIN_ARM64}" = "true" ]; then
  if [ -z "${url_arm64}" ] || [ -z "${sha_arm64}" ]; then
    echo "error: RELEASE_DARWIN_ARM64=true but manifest missing arm64 package" >&2
    exit 1
  fi
else
  url_arm64="${archive_url}"
  archive_sha256="${archive_sha256:-$(download_sha256 "${archive_url}")}"
  sha_arm64="${archive_sha256}"
fi

if [ "${RELEASE_DARWIN_X86_64}" = "true" ]; then
  if [ -z "${url_x86}" ] || [ -z "${sha_x86}" ]; then
    echo "error: RELEASE_DARWIN_X86_64=true but manifest missing x86_64 package" >&2
    exit 1
  fi
else
  archive_sha256="${archive_sha256:-$(download_sha256 "${archive_url}")}"
  url_x86="${archive_url}"
  sha_x86="${archive_sha256}"
fi

escape_sed() {
  printf '%s' "$1" | sed 's/[\/&]/\\&/g'
}

e_url_arm64="$(escape_sed "${url_arm64}")"
e_sha_arm64="$(escape_sed "${sha_arm64}")"
e_url_x86="$(escape_sed "${url_x86}")"
e_sha_x86="$(escape_sed "${sha_x86}")"

sed \
  -e "s/#_version_#/${VERSION}/g" \
  -e "s|#_url_darwin_arm64_#|${e_url_arm64}|g" \
  -e "s/#_sha256_darwin_arm64_#/${e_sha_arm64}/g" \
  -e "s|#_url_darwin_x86_64_#|${e_url_x86}|g" \
  -e "s/#_sha256_darwin_x86_64_#/${e_sha_x86}/g" \
  "${TEMPLATE}" > "${OUT}"

echo "wrote ${OUT}"
