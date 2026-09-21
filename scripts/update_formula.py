#!/usr/bin/env python3
"""Update the macOS formula from a stable upstream GitHub release."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import urllib.request

API = "https://api.github.com/repos/bendlang/bend/releases/latest"
RELEASES = "https://github.com/bendlang/bend/releases/download"
FORMULA = Path(__file__).resolve().parents[1] / "Formula" / "bend.rb"


def latest_release():
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "kitevi-homebrew-bend"}
    if os.environ.get("GH_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GH_TOKEN"]
    request = urllib.request.Request(API, headers=headers)
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def download_digest(url):
    # Do not forward the API credential to release downloads or redirects.
    request = urllib.request.Request(url, headers={"User-Agent": "kitevi-homebrew-bend"})
    digest = hashlib.sha256()
    with urllib.request.urlopen(request, timeout=120) as response:
        for chunk in iter(lambda: response.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def update(source, release, digest_for=download_digest, verify_current=False):
    tag = release.get("tag_name", "")
    if release.get("draft") or release.get("prerelease") or not re.fullmatch(r"v2\.\d+\.\d+", tag):
        raise ValueError("Expected a stable Bend 2 release; review major-version changes manually")
    version = tag[1:]
    matches = re.findall(r'url "https://github\.com/bendlang/bend/releases/download/v(\d+\.\d+\.\d+)/bend-[^"\n]+-darwin-arm64\.tar\.gz"', source)
    if len(matches) != 1:
        raise ValueError("Expected exactly one formula version")
    current = matches[0]
    if tuple(map(int, version.split("."))) < tuple(map(int, current.split("."))):
        raise ValueError("Refusing to downgrade the formula")
    if version == current and not verify_current:
        return source

    result = source
    for arch in ("arm64", "x64"):
        name = f"bend-{version}-darwin-{arch}.tar.gz"
        assets = [asset for asset in release.get("assets", []) if asset.get("name") == name]
        if len(assets) != 1:
            raise ValueError(f"Expected exactly one asset: {name}")
        asset = assets[0]
        url = f"{RELEASES}/{tag}/{name}"
        if asset.get("browser_download_url") != url:
            raise ValueError(f"Unexpected download URL for {name}")
        expected = asset.get("digest") or ""
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", expected):
            raise ValueError(f"Missing GitHub SHA-256 digest for {name}; review manually")
        actual = digest_for(url)
        if "sha256:" + actual != expected:
            raise ValueError(f"Checksum mismatch for {name}")
        old_url = f"{RELEASES}/v{current}/bend-{current}-darwin-{arch}.tar.gz"
        pattern = rf'(?m)^(      url )"{re.escape(old_url)}"\n(      sha256 )"[0-9a-f]{{64}}"$'
        result, count = re.subn(pattern, lambda m: f'{m[1]}"{url}"\n{m[2]}"{actual}"', result)
        if count != 1:
            raise ValueError(f"Expected exactly one formula URL/checksum pair for {arch}")

    if version == current and result != source:
        raise ValueError("Published assets changed for the installed version; review manually")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-current", action="store_true", help="Also download and verify an unchanged release")
    args = parser.parse_args()
    source = FORMULA.read_text()
    result = update(source, latest_release(), verify_current=args.verify_current)
    if result == source:
        print("Formula is current.")
    else:
        # Both downloads and all validations must succeed before modifying the file.
        FORMULA.write_text(result)
        print("Updated Formula/bend.rb; review and run formula tests before merging.")


if __name__ == "__main__":
    main()
