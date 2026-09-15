"""Pull GitHub releases (and commits if a repo has none).

The textbook itself is a snapshot. This command is how you un-snapshot it.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import urllib.error
import urllib.request
from datetime import datetime, timezone

REPOS = [
    ("1rgs/nanocode", "极简 · 几乎冻结"),
    ("SWE-agent/mini-swe-agent", "极简评测 scaffold"),
    ("earendil-works/pi", "生产级极简可扩展"),
    ("anomalyco/opencode", "开源 coding agent 顶梁柱"),
    ("openai/codex", "工业级官方 CLI"),
    ("deepseek-ai/deepseek-harness", "万物皆插件 / PTC"),
]


def _gh_api(path: str) -> Any | None:
    if not shutil.which("gh"):
        return None
    proc = subprocess.run(
        ["gh", "api", path],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if proc.returncode != 0:
        return None
    return json.loads(proc.stdout)


def _get(url: str) -> Any:
    path = url.removeprefix("https://api.github.com/")
    via_gh = _gh_api(path)
    if via_gh is not None:
        return via_gh
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    headers = {
        "User-Agent": "write-your-harness",
        "Accept": "application/vnd.github+json",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def _releases(repo: str, n: int = 8) -> list[dict[str, Any]]:
    data = _get(f"https://api.github.com/repos/{repo}/releases?per_page={n}")
    return data if isinstance(data, list) else []


def _commits(repo: str, n: int = 8) -> list[dict[str, Any]]:
    data = _get(f"https://api.github.com/repos/{repo}/commits?per_page={n}")
    return data if isinstance(data, list) else []


def snapshot(n: int = 8) -> dict[str, Any]:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    out: dict[str, Any] = {"fetched_at": now, "repos": []}
    for repo, note in REPOS:
        entry: dict[str, Any] = {"repo": repo, "note": note, "releases": [], "commits": []}
        try:
            rels = _releases(repo, n)
            entry["releases"] = [
                {
                    "tag": r.get("tag_name"),
                    "name": r.get("name"),
                    "published_at": r.get("published_at"),
                    "prerelease": r.get("prerelease"),
                    "url": r.get("html_url"),
                    "body_head": (r.get("body") or "").strip().splitlines()[:4],
                }
                for r in rels
            ]
            if not rels:
                commits = _commits(repo, n)
                entry["commits"] = [
                    {
                        "sha": c["sha"][:10],
                        "date": ((c.get("commit") or {}).get("committer") or {}).get("date"),
                        "message": ((c.get("commit") or {}).get("message") or "").splitlines()[0],
                        "url": c.get("html_url"),
                    }
                    for c in commits
                ]
        except urllib.error.HTTPError as err:
            entry["error"] = f"HTTP {err.code}"
        except Exception as err:  # noqa: BLE001
            entry["error"] = str(err)
        out["repos"].append(entry)
    return out


def render(data: dict[str, Any]) -> str:
    lines = [
        f"# Living map — fetched {data.get('fetched_at')}",
        "",
        "把这一页贴回第 15 章对照。版本号会过时；读法不会。",
        "",
    ]
    for repo in data.get("repos", []):
        lines.append(f"## {repo['repo']}")
        lines.append(f"_{repo.get('note', '')}_")
        if repo.get("error"):
            lines.append(f"- 拉取失败：{repo['error']}")
            lines.append("")
            continue
        if repo.get("releases"):
            for rel in repo["releases"]:
                flag = " (pre)" if rel.get("prerelease") else ""
                lines.append(f"- {rel.get('published_at', '')[:10]} `{rel.get('tag')}`{flag}  {rel.get('url')}")
                for head in rel.get("body_head") or []:
                    if head.strip():
                        lines.append(f"  {head[:120]}")
                        break
        elif repo.get("commits"):
            lines.append("- 没有 GitHub Release，改为最近 commit：")
            for c in repo["commits"]:
                lines.append(f"- {str(c.get('date') or '')[:10]} `{c['sha']}`  {c.get('message')}")
        else:
            lines.append("- （空）")
        lines.append("")
    return "\n".join(lines)
