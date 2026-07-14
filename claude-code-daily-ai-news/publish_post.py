#!/usr/bin/env python3
"""Publish a blog post to the Tsai-Cheng-Hung site.

Usage: python3 publish_post.py <payload.json>

Reads config.json (same directory) for endpoints and secrets, then:
  1. POST {api_base}/posts  (upsert by slug, Bearer admin_token)
  2. POST {frontend_base}/api/revalidate?secret=... (refresh ISR cache)

Payload JSON fields: slug, title_en, title_zh, excerpt_en, excerpt_zh,
body_en, body_zh, tags (list), reading_minutes, published (bool).
Uses stdlib only (urllib) — no pip installs needed.

Unlike the Cowork sandbox version, Claude Code runs directly on your machine
with normal internet access, so this script can be called directly — no
browser automation / base64 chunking workaround needed.
"""

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional, Tuple

HERE = Path(__file__).resolve().parent


def post_json(url: str, data: Optional[dict], headers: dict) -> Tuple[int, str]:
    body = json.dumps(data).encode("utf-8") if data is not None else b""
    req = urllib.request.Request(url, data=body, method="POST", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: publish_post.py <payload.json>", file=sys.stderr)
        return 2

    config = json.loads((HERE / "config.json").read_text(encoding="utf-8"))
    for key in ("api_base", "admin_token", "frontend_base", "revalidate_secret"):
        if not config.get(key) or "FILL_ME" in str(config.get(key, "")):
            print(f"ERROR: config.json field '{key}' is not set", file=sys.stderr)
            return 3

    payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))

    # 1. Upsert the post
    status, body = post_json(
        f"{config['api_base'].rstrip('/')}/posts",
        payload,
        {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config['admin_token']}",
        },
    )
    if status not in (200, 201):
        print(f"ERROR: POST /posts returned {status}: {body[:500]}", file=sys.stderr)
        return 4
    print(f"OK: post '{payload['slug']}' upserted (HTTP {status})")

    # 2. Revalidate the frontend cache
    status, body = post_json(
        f"{config['frontend_base'].rstrip('/')}/api/revalidate"
        f"?secret={config['revalidate_secret']}",
        None,
        {},
    )
    if status != 200:
        print(f"WARNING: revalidate returned {status}: {body[:300]} "
              "(post is saved; cache refreshes within 5 min anyway)", file=sys.stderr)
        return 0  # non-fatal: ISR picks it up within 300s
    print("OK: frontend cache revalidated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
