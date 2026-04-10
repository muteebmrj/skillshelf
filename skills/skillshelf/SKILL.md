---
name: skillshelf
description: "List all installed Claude Code skills, plugins, agents, and commands with metadata, source info, and GitHub stats. Also recommends which skills to use for a given task. Use when the user asks to 'list skills', 'show installed plugins', 'what skills do I have', 'skill inventory', 'skillshelf', 'skill report', 'list my capabilities', 'show all plugins', 'which skill can', 'what skill should I use', 'find me a skill for', 'recommend a skill', or wants to see all available capabilities."
version: 1.0.0
---

# Skillshelf

List all installed Claude Code capabilities with metadata, source classification, and optional GitHub stats. Supports three output modes and smart caching for token efficiency.

## Invocation Modes

Parse the user's request to determine which mode to use:

| User says | Mode | What to do |
|-----------|------|------------|
| "list skills", "what skills do I have", "skill inventory" | **Quick** | Markdown table in conversation |
| "full skill inventory", "detailed skill list", "show everything" | **Full** | Detailed markdown with GitHub stars |
| "export skill inventory", "generate skill report", "html report" | **Export** | Generate interactive HTML file |
| "refresh skills", "update inventory" | **Refresh** | Force re-scan ignoring cache |
| "which skill can help me...", "what skill for...", "find me a skill for...", "recommend a skill for..." | **Recommend** | Smart skill recommendation |

## Execution Steps

### Step 1: Run the scanner

Determine the skill's own install path by checking where this SKILL.md lives. The scanner script is at `scripts/inventory.sh` relative to this SKILL.md.

The scanner is a Python script that works cross-platform (macOS, Linux, Windows with WSL). Locate it relative to this SKILL.md file.

```bash
# Locate the skill directory — works whether installed as a skill or plugin
# Check common install locations in order
for DIR in \
  "${HOME}/.claude/skills/skillshelf" \
  "$(find "${HOME}/.claude/plugins" -path "*/skillshelf/SKILL.md" -exec dirname {} \; 2>/dev/null | head -1)"; do
  if [ -f "${DIR}/scripts/scan.py" ]; then
    SKILL_DIR="$DIR"
    break
  fi
done

# Quick mode (no GitHub stats)
python3 "${SKILL_DIR}/scripts/scan.py"

# Full/Export mode (with GitHub stats)
python3 "${SKILL_DIR}/scripts/scan.py" --include-github

# Force refresh (bypass cache)
python3 "${SKILL_DIR}/scripts/scan.py" --refresh
# Or with GitHub:
python3 "${SKILL_DIR}/scripts/scan.py" --refresh --include-github
```

The script outputs a JSON object to stdout with this structure:
```json
{
  "fingerprint": "abc123...",
  "scanned_at": "2025-01-15T10:30:00",
  "counts": { "skill": 5, "plugin": 33, "agent": 157, "command": 2, "total": 197 },
  "entries": [
    {
      "name": "skill-name",
      "description": "What it does...",
      "type": "skill|plugin|agent|command",
      "source": "custom|marketplace-official|marketplace-community|marketplace-external|agents-repo|skillfish-installed|project-local|linked",
      "category": "development|engineering|design|...",
      "version": "1.0.0",
      "author": "Author Name",
      "github_repo": "owner/repo",
      "github_stars": 42,
      "homepage": "https://...",
      "path": "/absolute/path/to/skill",
      "has_mcp": true,
      "sub_skill_count": 3
    }
  ]
}
```

### Step 2: Format output

#### Quick Mode — Markdown table

Present a summary line, then grouped tables:

```
Found {total} installed capabilities: {skill} skills, {plugin} plugins, {agent} agents

## Skills & Plugins ({skill + plugin} total)

| Name | Type | Source | Category | Description |
|------|------|--------|----------|-------------|
| ... | skill | Custom | dev | ... |

## Agents ({agent} total)

| Name | Category | Description |
|------|----------|-------------|
| ... | engineering | ... |
```

Source display mapping:
- `custom` → "Custom"
- `marketplace-official` → "Official"
- `marketplace-community` → "Community"
- `marketplace-external` → "External"
- `agents-repo` → "Agents Repo"
- `skillfish-installed` → "Installed"
- `project-local` → "Project"
- `linked` → "Linked"

Truncate descriptions to 80 characters in the table. For agents, group by category if there are more than 20.

#### Full Mode — Detailed markdown

Same as quick mode but add columns:
- **Stars** (GitHub stars, show number or "-" if unavailable)
- **Version**
- **Author**
- **GitHub** (owner/repo as a link)

Include an "MCP" indicator for plugins that have MCP servers.

#### Export Mode — Interactive HTML report

1. Read the scanner JSON output
2. Read the HTML template from `assets/template.html` relative to this SKILL.md
3. Replace the placeholder `__INVENTORY_DATA__` in the template with the actual JSON data
4. Write the resulting HTML to `~/.claude/cache/skillshelf-report.html`
5. Tell the user the file path and suggest opening it in a browser
6. On macOS, optionally run `open ~/.claude/cache/skillshelf-report.html`

Use the same SKILL_DIR detected in Step 1 to locate the template:
```bash
TEMPLATE="${SKILL_DIR}/assets/template.html"
OUTPUT="${HOME}/.claude/cache/skillshelf-report.html"
```

Use python3 to do the replacement:
```python
import json, sys
template = open(sys.argv[1]).read()
data = json.loads(sys.argv[2])
html = template.replace('__INVENTORY_DATA__', json.dumps(data))
with open(sys.argv[3], 'w') as f:
    f.write(html)
```

### Step 3: Cache behavior

The scanner handles caching automatically:
- **First run**: Full scan, saves to `~/.claude/cache/skillshelf-cache.json`
- **Subsequent runs**: Compares filesystem fingerprint. If unchanged, serves cached JSON instantly
- **GitHub stats**: Cached separately with 24h TTL in `~/.claude/cache/skillshelf-github-cache.json`
- **`--refresh` flag**: Bypasses all caches

When presenting cached results, note: "Showing cached results (last scanned: {scanned_at}). Use --refresh for a fresh scan."

## Recommend Mode — Smart Skill Finder

When the user asks something like "which skill can help me design a carousel?" or "what skill should I use to write a cold email?", use this mode.

### How it works

1. Run the scanner to get the cached inventory (quick — usually a cache hit)
2. Extract the user's **intent** from their message (what they want to accomplish)
3. Match their intent against the inventory using TWO scoring methods:

**Method A — Niche matching**: Map the user's intent to niches. "design a carousel" maps to Design + Content Creation. Filter entries that have those niches.

**Method B — Keyword matching**: Extract keywords from the user's intent and search against each entry's `name` + `description` fields. Score by number of keyword hits.

4. Combine scores: entries that match BOTH niche AND keywords rank highest
5. Present the top 3-5 matches in this format:

```
## Recommended Skills for: "design a carousel"

### Best Match
**social-media-manager** (skill)
> Senior Social Media Manager that produces post-ready content packages across Instagram, LinkedIn, TikTok...
Niche: Marketing, Content Creation | Source: Marketplace Official
Use: `/social-media-manager`

### Also Relevant
**superdesign** (skill)
> Design agent specialized in frontend UI/UX design...
Niche: Design | Source: Linked
Use: `/superdesign`

**visual-storyteller** (agent)
> Transforms complex information into visual narratives...
Niche: Design, Content Creation | Source: Agents Repo

---
*3 skills matched out of 291 installed. Try different keywords for more results.*
```

### Matching examples

| User says | Intent keywords | Matched niches | Top results |
|-----------|----------------|----------------|-------------|
| "design a carousel" | carousel, design, social | Design, Marketing | social-media-manager, superdesign, visual-storyteller |
| "do some research" | research, investigate | Data, AI & ML | researcher, data-engineer |
| "write a cold email" | cold, email, outreach | Sales, Marketing | draft-outreach, email-sequence, brand-voice-enforcement |
| "build an API" | api, build, backend | Development, DevOps | backend-architect, senior-developer, software-architect |
| "review my code" | review, code, quality | Development | code-reviewer, security |

### Important for Recommend mode
- Always run the scanner first (cache hit is fast)
- Show the skill name, type, description snippet, niches, and how to invoke it
- If no good matches, say so and suggest browsing by niche using the HTML report
- Prioritize skills and plugins over agents (they're more actionable)

## Important Notes

- The scanner requires `python3` (available on macOS and modern Linux by default)
- GitHub stats require either `gh` CLI (authenticated) or `curl`. Without auth, rate-limited to 60 requests/hour
- If `gh auth status` succeeds, GitHub API rate limit is 5000/hour
- The scanner skips its own directory (skillshelf) in the results
- Agent entries always have `github_repo: "anthropics/claude-agents"` since they come from that repo
- Marketplace entries extract GitHub repos from source URLs in marketplace.json
