<p align="center">
  <img src="assets/skillshelf-banner.png" alt="Skillshelf — Claude Code Skill Inventory" width="100%" />
</p>

<h1 align="center">Skillshelf</h1>

<p align="center">
  <strong>See everything you have. Find what you need.</strong>
</p>

<p align="center">
  Claude Code skill that gives you a complete, interactive inventory of every skill, plugin, agent, and command installed in your environment — with smart niche filtering, GitHub stats, and AI-powered skill recommendations.
</p>

<p align="center">
  <a href="https://github.com/muteebmrj/skillshelf"><img src="https://img.shields.io/github/stars/muteebmrj/skillshelf?style=flat&color=D97757" alt="Stars" /></a>
  <a href="https://github.com/muteebmrj/skillshelf/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License" /></a>
  <a href="https://github.com/muteebmrj/skillshelf"><img src="https://img.shields.io/badge/Claude_Code-skill-orange.svg" alt="Claude Code Skill" /></a>
</p>

---

## Features

### Interactive HTML Dashboard
A Notion-inspired, self-contained HTML report with:
- **Liquid Glass UI** — Apple-style frosted glass pills, stat cards, and filter buttons
- **Light / Dark mode** toggle (auto-detects system preference)
- **Search** — instant client-side filtering across all fields
- **Sort** — click any column header to sort ascending/descending
- **Type filters** — All, Skills, Plugins, Agents, Commands
- **Niche filters** — 12 auto-detected categories: Design, Development, Marketing, Sales, DevOps, Security, Data, AI & ML, Productivity, Content Creation, Gaming, Other
- **Description popovers** — hover the "i" icon to read full descriptions
- **Fully responsive** — works on desktop, tablet, and mobile
- **Zero dependencies** — single self-contained HTML file, no CDN, no external fonts

### Smart Skill Recommendations
Don't know which skill to use? Just ask:
- *"Which skill can help me design a carousel?"*
- *"What skill should I use to write a cold email?"*
- *"Find me a skill for building an API"*

Skillshelf matches your intent against niche tags and descriptions, then recommends the top 3-5 relevant skills with instructions on how to invoke them.

### Smart Caching
- **First run**: ~5 seconds (full filesystem scan)
- **Repeat runs**: ~100ms (fingerprint-based cache hit)
- **GitHub stats**: cached with 24h TTL, auto-refreshes expired entries only

### What It Scans

| Location | What's there |
|----------|-------------|
| `~/.claude/skills/` | Custom & installed skills |
| `~/.claude/plugins/marketplaces/` | Official + community marketplace plugins |
| `~/.claude/plugins/*/external_plugins/` | MCP server integrations (Slack, Asana, etc.) |
| `~/.claude/agents/` | Agent personalities (engineering, design, sales...) |
| `$CWD/.claude/skills/` | Project-level skills |

### Data Per Entry

- **Name** and **full description**
- **Type**: skill, plugin, agent, or command
- **Source**: Custom, Official, Community, External, Installed, Linked, Agents Repo, Project
- **Niche tags**: auto-detected from name + description (Design, Development, Marketing, etc.)
- **Category**, **Version**, **Author**
- **GitHub repo** with star count
- **MCP indicator** and **sub-skill count** for plugins

---

## Install

```bash
claude install-skill https://github.com/muteebmrj/skillshelf
```

Or manually:

```bash
git clone https://github.com/muteebmrj/skillshelf.git ~/.claude/skills/skillshelf
```

---

## Usage

### List your skills

Just say any of these in Claude Code:

```
list my skills
what skills do I have
skillshelf
show all plugins
```

**Quick mode** — markdown table right in the conversation:
```
Found 291 installed capabilities: 3 skills, 126 plugins, 162 agents
```

### Detailed view with GitHub stars

```
full skill inventory
show everything with stars
```

### Export interactive HTML report

```
export skill inventory
generate skill report
html report
```

Generates a self-contained HTML file at `~/.claude/cache/skill-inventory-report.html` and opens it in your browser.

### Get skill recommendations

```
which skill can help me design a carousel?
what skill should I use to write cold emails?
find me a skill for API development
recommend a skill for SEO
```

Returns the top matching skills with descriptions and invocation instructions.

### Force refresh

```
refresh skill inventory
```

Bypasses cache and does a full re-scan.

---

## Prompt Examples

| What you say | What happens |
|-------------|-------------|
| *"list my skills"* | Quick markdown table of everything installed |
| *"full skill inventory"* | Detailed table with GitHub stars, versions, authors |
| *"export skill report"* | Generates the interactive HTML dashboard |
| *"which skill can help me design a logo?"* | Recommends design-related skills |
| *"find me a skill for writing outbound emails"* | Recommends sales/marketing skills |
| *"what skill should I use to deploy to AWS?"* | Recommends DevOps/infrastructure skills |
| *"refresh my skills"* | Full re-scan ignoring cache |

---

## HTML Dashboard Screenshots

### Light Mode
- Notion-inspired clean design
- Liquid Glass stat cards and filter pills
- Niche filter pills with color-coded categories

### Dark Mode
- Smoky translucent glass effects
- Specular rim highlights on pills
- Full dark Notion color palette

---

## Project Structure

```
.claude-plugin/
  plugin.json                    # Plugin metadata for marketplace installation
skills/
  skillshelf/
    SKILL.md                     # Skill definition — Claude reads this
    scripts/
      scan.py                    # Python scanner engine (stdlib only, zero deps)
      track-usage.py             # Usage tracking CLI
      inventory.sh               # Bash wrapper for the scanner
    assets/
      template.html              # Notion-styled interactive HTML report
    hooks/
      hooks.json                 # Auto-tracks skill usage via PostToolUse hook
```

---

## Requirements

- **Python 3.6+** (included on macOS and most Linux distributions)
- **`gh` CLI** (optional) — for authenticated GitHub API access at 5000 req/hr instead of 60/hr
- Works on **macOS** and **Linux**. Windows users need WSL.

---

## How It Works

1. **Scanning** — `scan.py` walks all 5 skill source directories, parses YAML frontmatter from SKILL.md files, reads plugin.json manifests, and extracts metadata from marketplace.json catalogs
2. **Niche tagging** — Each entry is auto-tagged with relevant niches using keyword matching against 12 categories (120+ keywords)
3. **Caching** — Results are cached with a SHA-256 fingerprint of all source directories. If nothing changed, the cache is served in ~100ms
4. **GitHub stats** — Fetched via `gh api` (if authenticated) or `curl`, cached per-repo with 24h TTL
5. **HTML generation** — The scan JSON is injected into the template HTML, producing a self-contained interactive report
6. **Recommendations** — When you ask "which skill can help me X?", Claude matches your intent against niche tags and descriptions using dual scoring

---

## Author

Created by **muteebmrj**

<p>
  <a href="https://github.com/muteebmrj"><img src="https://img.shields.io/badge/GitHub-muteebmrj-181717?style=flat&logo=github" alt="GitHub" /></a>
  <a href="https://www.linkedin.com/in/muteebmrj"><img src="https://img.shields.io/badge/LinkedIn-muteebmrj-0A66C2?style=flat&logo=linkedin" alt="LinkedIn" /></a>
  <a href="https://instagram.com/muteebmehraj"><img src="https://img.shields.io/badge/Instagram-@muteebmehraj-E4405F?style=flat&logo=instagram&logoColor=white" alt="Instagram" /></a>
</p>

---

If you find this useful, give it a star and share it with someone who uses Claude Code.

## License

MIT
