#!/usr/bin/env python3
"""Skill Inventory Scanner — scans all Claude Code skill sources, outputs unified JSON."""

import json
import os
import re
import subprocess
import sys
import hashlib
import time
from datetime import datetime
from pathlib import Path

CLAUDE_DIR = Path.home() / ".claude"
CACHE_DIR = CLAUDE_DIR / "cache"
CACHE_FILE = CACHE_DIR / "skillshelf-cache.json"
GITHUB_CACHE = CACHE_DIR / "skillshelf-github-cache.json"
GITHUB_TTL = 86400  # 24 hours
USAGE_LOG = CACHE_DIR / "skillshelf-usage.json"

# --- Niche tagging engine ---
NICHE_KEYWORDS = {
    "Design": [
        "design", "ui", "ux", "visual", "brand", "mockup", "wireframe", "figma",
        "accessibility", "a11y", "wcag", "color", "typography", "layout", "interface",
        "prototype", "icon", "illustration", "aesthetic", "responsive", "css",
        "component", "pixel", "handoff", "critique",
    ],
    "Development": [
        "code", "build", "engineer", "debug", "backend", "frontend", "fullstack",
        "api", "sdk", "framework", "react", "vue", "angular", "laravel", "django",
        "node", "typescript", "javascript", "python", "rust", "go", "java", "swift",
        "compiler", "lsp", "linter", "refactor", "architecture", "microservice",
    ],
    "Marketing": [
        "marketing", "seo", "content", "campaign", "social media", "email sequence",
        "brand voice", "copywriting", "newsletter", "landing page", "growth",
        "conversion", "funnel", "audience", "engagement", "influencer", "ads",
        "advertising", "ppc", "sem", "organic", "douyin", "xiaohongshu", "bilibili",
        "tiktok", "instagram", "linkedin", "twitter", "youtube", "podcast",
    ],
    "Sales": [
        "sales", "pipeline", "outreach", "forecast", "deal", "prospect", "crm",
        "lead", "cold email", "discovery", "demo", "negotiation", "account",
        "revenue", "quota", "battlecard", "competitive intel", "apollo",
    ],
    "DevOps": [
        "devops", "ci/cd", "deploy", "infrastructure", "docker", "kubernetes",
        "terraform", "aws", "cloud", "monitoring", "sre", "incident", "pipeline",
        "automation", "helm", "ansible",
    ],
    "Security": [
        "security", "vulnerability", "threat", "audit", "sast", "penetration",
        "encryption", "authentication", "authorization", "owasp", "compliance",
        "firewall", "breach", "malware",
    ],
    "Data": [
        "data", "analytics", "database", "sql", "etl", "warehouse", "pipeline",
        "tableau", "dashboard", "metrics", "visualization", "reporting", "bi",
        "spreadsheet", "csv", "excel",
    ],
    "AI & ML": [
        "ai", "machine learning", "model", "prompt", "llm", "agent", "neural",
        "training", "inference", "embedding", "vector", "rag", "fine-tune",
        "anthropic", "openai", "claude", "gpt", "mcp server",
    ],
    "Productivity": [
        "productivity", "task", "workflow", "automation", "schedule", "calendar",
        "notion", "project management", "template", "document", "pdf", "pptx",
        "docx", "spreadsheet", "organize",
    ],
    "Content Creation": [
        "writing", "blog", "article", "copy", "creative", "story", "narrative",
        "video", "audio", "podcast", "editing", "publishing", "press release",
        "case study", "documentation", "technical writing",
    ],
    "Gaming": [
        "game", "unity", "unreal", "godot", "roblox", "shader", "vfx", "level",
        "multiplayer", "narrative design", "blender", "3d", "rendering",
    ],
}


def compute_niches(name, description, category):
    """Auto-tag an entry with relevant niches based on name + description + category."""
    text = f"{name} {description} {category}".lower()
    tags = []
    for niche, keywords in NICHE_KEYWORDS.items():
        score = 0
        for kw in keywords:
            if kw in text:
                score += 1
        # Require at least 2 keyword hits for confidence, or 1 strong hit in name
        name_lower = name.lower()
        name_hits = sum(1 for kw in keywords if kw in name_lower)
        if score >= 2 or name_hits >= 1:
            tags.append(niche)
    # Fallback: if no tags, use "Other"
    return tags if tags else ["Other"]

# --- Argument parsing ---
include_github = "--include-github" in sys.argv
force_refresh = "--refresh" in sys.argv

if "--cache-dir" in sys.argv:
    idx = sys.argv.index("--cache-dir")
    if idx + 1 < len(sys.argv):
        CACHE_DIR = Path(sys.argv[idx + 1])
        CACHE_FILE = CACHE_DIR / "skillshelf-cache.json"
        GITHUB_CACHE = CACHE_DIR / "skillshelf-github-cache.json"

CACHE_DIR.mkdir(parents=True, exist_ok=True)


def parse_yaml_frontmatter(filepath):
    """Extract YAML-like frontmatter from a markdown file."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except Exception:
        return {}

    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}

    fm = {}
    for line in match.group(1).split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        idx = line.find(":")
        if idx > 0:
            key = line[:idx].strip()
            val = line[idx + 1 :].strip()
            # Strip surrounding quotes
            if len(val) >= 2 and val[0] in ('"', "'") and val[-1] == val[0]:
                val = val[1:-1]
            fm[key] = val
    return fm


def compute_fingerprint():
    """Hash directory listings to detect changes."""
    dirs = [
        CLAUDE_DIR / "skills",
        CLAUDE_DIR / "plugins" / "marketplaces",
        CLAUDE_DIR / "agents",
    ]
    hasher = hashlib.sha256()
    for d in dirs:
        if d.is_dir():
            try:
                for p in sorted(d.rglob("*")):
                    if p.suffix in (".md", ".json") and p.is_file():
                        stat = p.stat()
                        hasher.update(f"{p}:{stat.st_mtime}:{stat.st_size}\n".encode())
            except Exception:
                pass
    return hasher.hexdigest()


def check_cache():
    """Return cached data if fingerprint matches."""
    if force_refresh or not CACHE_FILE.exists():
        return None
    try:
        with open(CACHE_FILE) as f:
            cached = json.load(f)
        cached_fp = cached.get("fingerprint", "")
        current_fp = compute_fingerprint()
        if cached_fp and cached_fp == current_fp:
            return cached
    except Exception:
        pass
    return None


def get_last_modified(path):
    """Get the most recent modification time for a skill directory or file."""
    p = Path(path)
    try:
        if p.is_file():
            return datetime.fromtimestamp(p.stat().st_mtime).isoformat()
        elif p.is_dir():
            # Find the most recently modified .md or .py file
            latest = 0
            for f in p.rglob("*"):
                if f.is_file() and f.suffix in (".md", ".py", ".json", ".html", ".sh"):
                    mt = f.stat().st_mtime
                    if mt > latest:
                        latest = mt
            if latest > 0:
                return datetime.fromtimestamp(latest).isoformat()
    except Exception:
        pass
    return None


def load_usage_data():
    """Load usage tracking data from the log file."""
    if USAGE_LOG.is_file():
        try:
            with open(USAGE_LOG) as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def make_entry(
    name, description="", entry_type="skill", source="custom", category="",
    version="", author="", github_repo="", homepage="", path="",
    has_mcp=False, sub_skill_count=0,
):
    niches = compute_niches(name, description, category)
    last_mod = get_last_modified(path)

    return {
        "name": name,
        "description": (description or "")[:500],
        "type": entry_type,
        "source": source,
        "category": category,
        "niches": niches,
        "version": version,
        "author": author,
        "github_repo": github_repo,
        "github_stars": None,
        "homepage": homepage,
        "path": str(path),
        "has_mcp": has_mcp,
        "sub_skill_count": sub_skill_count,
        "last_modified": last_mod,
    }


# --- Source scanners ---

def scan_custom_skills():
    """Source 1: ~/.claude/skills/"""
    entries = []
    skills_dir = CLAUDE_DIR / "skills"
    if not skills_dir.is_dir():
        return entries

    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        name = skill_dir.name

        # Skip ourselves
        if name in ("skill-inventory", "skillshelf"):
            continue

        skill_md = skill_dir / "SKILL.md"
        skillfish = skill_dir / ".skillfish.json"
        source_type = "custom"
        github_repo = ""
        description = ""
        version = ""

        if skill_md.is_file():
            fm = parse_yaml_frontmatter(skill_md)
            name = fm.get("name", name)
            description = fm.get("description", "")
            version = fm.get("version", "")

        if skillfish.is_file():
            source_type = "skillfish-installed"
            try:
                with open(skillfish) as f:
                    sf = json.load(f)
                owner = sf.get("owner", "")
                repo = sf.get("repo", "")
                if owner and repo:
                    github_repo = f"{owner}/{repo}"
            except Exception:
                pass
        elif skill_dir.is_symlink():
            source_type = "linked"

        entries.append(make_entry(
            name=name, description=description, entry_type="skill",
            source=source_type, version=version, github_repo=github_repo,
            path=skill_dir,
        ))

    return entries


def scan_marketplace_plugins():
    """Source 2+3: ~/.claude/plugins/marketplaces/"""
    entries = []
    mp_base = CLAUDE_DIR / "plugins" / "marketplaces"
    if not mp_base.is_dir():
        return entries

    for mp_dir in sorted(mp_base.iterdir()):
        if not mp_dir.is_dir():
            continue

        mp_json = mp_dir / ".claude-plugin" / "marketplace.json"
        if not mp_json.is_file():
            continue

        try:
            with open(mp_json) as f:
                data = json.load(f)
        except Exception:
            continue

        for p in data.get("plugins", []):
            name = p.get("name", "")
            desc = p.get("description", "")
            category = p.get("category", "")
            homepage = p.get("homepage", "")

            # Author
            author_obj = p.get("author", {})
            author = ""
            if isinstance(author_obj, dict):
                author = author_obj.get("name", "")
            elif isinstance(author_obj, str):
                author = author_obj

            # Source type and GitHub repo
            source_info = p.get("source", "")
            source_type = "marketplace-community"
            github_repo = ""

            if isinstance(source_info, str):
                if source_info.startswith("./plugins/"):
                    source_type = "marketplace-official"
                elif source_info.startswith("./external_plugins/"):
                    source_type = "marketplace-external"
            elif isinstance(source_info, dict):
                src = source_info.get("source", "")
                url = source_info.get("url", "")
                if src == "url" and url:
                    clean = url.replace(".git", "")
                    if "github.com/" in clean:
                        parts = clean.split("github.com/")[-1].split("/")
                        if len(parts) >= 2:
                            github_repo = f"{parts[0]}/{parts[1]}"
                elif src == "git-subdir" and url:
                    github_repo = url  # Already owner/repo format

            # Fallback: extract from homepage
            if not github_repo and homepage and "github.com/" in homepage:
                hp = homepage.replace("https://github.com/", "").replace("http://github.com/", "")
                parts = hp.split("/")
                if len(parts) >= 2:
                    github_repo = f"{parts[0]}/{parts[1]}"

            # Resolve plugin directory
            if isinstance(source_info, str):
                plugin_path = mp_dir / source_info.lstrip("./")
            else:
                plugin_path = mp_dir / "plugins" / name

            # Read plugin.json for version
            version = ""
            pj = plugin_path / ".claude-plugin" / "plugin.json"
            if pj.is_file():
                try:
                    with open(pj) as f:
                        pdata = json.load(f)
                    version = pdata.get("version", "")
                    if not author:
                        a = pdata.get("author", {})
                        if isinstance(a, dict):
                            author = a.get("name", "")
                except Exception:
                    pass

            # Count sub-skills
            sub_skill_count = 0
            skills_subdir = plugin_path / "skills"
            if skills_subdir.is_dir():
                for sd in skills_subdir.iterdir():
                    if sd.is_dir() and (sd / "SKILL.md").is_file():
                        sub_skill_count += 1

            # Check MCP
            has_mcp = (plugin_path / ".mcp.json").is_file()

            entries.append(make_entry(
                name=name, description=desc, entry_type="plugin",
                source=source_type, category=category, version=version,
                author=author, github_repo=github_repo, homepage=homepage,
                path=plugin_path, has_mcp=has_mcp, sub_skill_count=sub_skill_count,
            ))

    return entries


def scan_agents():
    """Source 4: ~/.claude/agents/"""
    entries = []
    agents_dir = CLAUDE_DIR / "agents"
    if not agents_dir.is_dir():
        return entries

    skip_files = {"README.md", "CONTRIBUTING.md", "CONTRIBUTING_zh-CN.md", "LICENSE", ".gitignore"}
    skip_dirs = {"scripts", "examples", ".git"}

    for root, dirs, files in os.walk(agents_dir):
        dirs[:] = [d for d in dirs if d not in skip_dirs and not d.startswith(".")]

        for fname in sorted(files):
            if fname in skip_files or not fname.endswith(".md"):
                continue

            fpath = Path(root) / fname
            rel = Path(root).relative_to(agents_dir)
            category = str(rel) if str(rel) != "." else ""

            fm = parse_yaml_frontmatter(fpath)
            if not fm:
                continue

            name = fm.get("name", fname.replace(".md", ""))
            desc = fm.get("description", "")

            entries.append(make_entry(
                name=name, description=desc, entry_type="agent",
                source="agents-repo", category=category, author="Anthropic",
                github_repo="anthropics/claude-agents",
                homepage="https://github.com/anthropics/claude-agents",
                path=fpath,
            ))

    return entries


def scan_project_skills():
    """Source 5: $CWD/.claude/skills/ and commands/"""
    entries = []
    cwd = Path.cwd()
    project_claude = cwd / ".claude"
    if not project_claude.is_dir():
        return entries

    # Skills
    skills_dir = project_claude / "skills"
    if skills_dir.is_dir():
        for skill_dir in sorted(skills_dir.iterdir()):
            if not skill_dir.is_dir():
                continue
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.is_file():
                continue

            fm = parse_yaml_frontmatter(skill_md)
            entries.append(make_entry(
                name=fm.get("name", skill_dir.name),
                description=fm.get("description", ""),
                entry_type="skill", source="project-local",
                version=fm.get("version", ""), path=skill_dir,
            ))

    # Legacy commands
    cmds_dir = project_claude / "commands"
    if cmds_dir.is_dir():
        for cmd_file in sorted(cmds_dir.glob("*.md")):
            fm = parse_yaml_frontmatter(cmd_file)
            entries.append(make_entry(
                name=fm.get("name", cmd_file.stem),
                description=fm.get("description", ""),
                entry_type="command", source="project-local",
                path=cmd_file,
            ))

    return entries


# --- GitHub stats ---

def fetch_github_stats(entries):
    """Fetch GitHub stars for entries with repos."""
    # Load cache
    gh_cache = {}
    if GITHUB_CACHE.is_file():
        try:
            with open(GITHUB_CACHE) as f:
                gh_cache = json.load(f)
        except Exception:
            pass

    # Detect auth
    auth_method = None
    try:
        result = subprocess.run(
            ["gh", "auth", "status"], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            auth_method = "gh-cli"
    except Exception:
        pass

    if not auth_method and os.environ.get("GITHUB_TOKEN"):
        auth_method = "token"

    now = int(time.time())
    repos_to_fetch = set()

    for e in entries:
        repo = e.get("github_repo", "")
        if not repo or "/" not in repo:
            continue
        cached = gh_cache.get(repo, {})
        if now - cached.get("fetched_at", 0) > GITHUB_TTL:
            repos_to_fetch.add(repo)

    # Fetch missing repos
    for repo in sorted(repos_to_fetch):
        try:
            if auth_method == "gh-cli":
                result = subprocess.run(
                    ["gh", "api", f"repos/{repo}", "--jq",
                     "{stargazers_count,forks_count,open_issues_count}"],
                    capture_output=True, text=True, timeout=10,
                )
                if result.returncode == 0 and result.stdout.strip():
                    data = json.loads(result.stdout)
                    gh_cache[repo] = {
                        "stars": data.get("stargazers_count", 0),
                        "forks": data.get("forks_count", 0),
                        "fetched_at": now,
                    }
            elif auth_method == "token":
                token = os.environ["GITHUB_TOKEN"]
                result = subprocess.run(
                    ["curl", "-s", "-H", f"Authorization: Bearer {token}",
                     f"https://api.github.com/repos/{repo}"],
                    capture_output=True, text=True, timeout=10,
                )
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    if "stargazers_count" in data:
                        gh_cache[repo] = {
                            "stars": data["stargazers_count"],
                            "forks": data.get("forks_count", 0),
                            "fetched_at": now,
                        }
            else:
                result = subprocess.run(
                    ["curl", "-s", f"https://api.github.com/repos/{repo}"],
                    capture_output=True, text=True, timeout=10,
                )
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    if "stargazers_count" in data:
                        gh_cache[repo] = {
                            "stars": data["stargazers_count"],
                            "forks": data.get("forks_count", 0),
                            "fetched_at": now,
                        }
        except Exception:
            pass

    # Save updated cache
    try:
        with open(GITHUB_CACHE, "w") as f:
            json.dump(gh_cache, f, indent=2)
    except Exception:
        pass

    # Merge stars into entries
    for e in entries:
        repo = e.get("github_repo", "")
        if repo in gh_cache:
            e["github_stars"] = gh_cache[repo].get("stars")
            e["github_forks"] = gh_cache[repo].get("forks", 0)

    return entries


# --- Main ---

def main():
    # Check cache first
    cached = check_cache()
    if cached:
        print(json.dumps(cached))
        return

    # Scan all sources
    entries = []
    entries.extend(scan_custom_skills())
    entries.extend(scan_marketplace_plugins())
    entries.extend(scan_agents())
    entries.extend(scan_project_skills())

    # Deduplicate by (name, type)
    seen = set()
    deduped = []
    for e in entries:
        key = (e["name"], e["type"])
        if key not in seen:
            seen.add(key)
            deduped.append(e)

    # Sort: skills first, then plugins, then agents
    type_order = {"skill": 0, "plugin": 1, "command": 2, "agent": 3}
    deduped.sort(key=lambda x: (type_order.get(x["type"], 9), x["name"]))

    # GitHub stats
    if include_github:
        deduped = fetch_github_stats(deduped)

    # Merge usage data
    usage_data = load_usage_data()
    for e in deduped:
        key = e["name"]
        usage = usage_data.get(key, {})
        e["usage_count"] = usage.get("count", 0)
        e["last_used"] = usage.get("last_used", None)

    # Compute counts
    counts = {}
    for e in deduped:
        t = e["type"]
        counts[t] = counts.get(t, 0) + 1
    counts["total"] = len(deduped)

    # Compute niche counts
    niche_counts = {}
    for e in deduped:
        for n in e.get("niches", []):
            niche_counts[n] = niche_counts.get(n, 0) + 1

    # Build output
    fingerprint = compute_fingerprint()
    output = {
        "fingerprint": fingerprint,
        "scanned_at": datetime.now().isoformat(),
        "counts": counts,
        "niche_counts": niche_counts,
        "entries": deduped,
    }

    # Save cache
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(output, f, indent=2)
    except Exception:
        pass

    # Output to stdout
    print(json.dumps(output))


if __name__ == "__main__":
    main()
