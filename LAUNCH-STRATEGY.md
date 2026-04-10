# Skillshelf Launch Strategy

## Screenshots You Need

Take these from your browser (the report is already open):

1. **Hero shot** — Dark mode, full dashboard, all 291 entries visible (for LinkedIn banner)
2. **Light mode** — Clean Notion aesthetic, stat cards prominent (for contrast)
3. **Niche filter active** — Click "Design" pill, showing 55 filtered results (shows the feature)
4. **Mobile view** — Resize browser narrow, shows responsive layout (shows polish)
5. **Terminal screenshot** — Run `/skillshelf list my skills` in Claude Code, screenshot the markdown output (shows it works in CLI too)

---

## Phase 1: Launch Day — LinkedIn Post

### The Post

---

I built a free tool that every Claude Code user needs.

Here's the problem:

If you use Claude Code, you probably have 100+ skills, plugins, and agents installed.
But there's no way to see them all in one place.
No way to filter by niche.
No way to know which ones are relevant to what you're working on.

So I built Skillshelf.

One command. Full inventory. Interactive dashboard.

Here's what it does:

1. Scans every skill, plugin, agent, and command on your system
2. Auto-tags each one into niches (Design, Development, Marketing, Sales, Security, AI & ML...)
3. Generates a Notion-styled interactive HTML dashboard with:
   - Apple Liquid Glass filter pills
   - Search, sort, and niche filtering
   - Light/dark mode toggle
   - Full responsive design
4. Smart skill recommendations — ask "which skill can help me design a carousel?" and it tells you exactly which of your installed skills to use

The numbers from my setup:
- 291 total capabilities found
- 126 plugins
- 162 agents
- 12 niches auto-detected
- Cache hit on repeat runs: 94ms

It's open source. Install it in 5 seconds:

claude install-skill https://github.com/muteebmrj/skillshelf

Try it. Type "/skillshelf" in Claude Code. That's it.

GitHub: https://github.com/muteebmrj/skillshelf

#ClaudeCode #AI #DeveloperTools #OpenSource #Anthropic

---

### Post Instructions

- **Attach 3-4 images**: Dark mode hero, light mode, niche filter active, mobile view
- **Post timing**: Tuesday-Thursday, 8-10 AM your timezone (peak LinkedIn engagement)
- **First comment**: Post the install command again as a comment immediately after publishing:
  "Install command: `claude install-skill https://github.com/muteebmrj/skillshelf`"
- **Tag**: Tag @Anthropic and @Claude if possible

---

## Phase 2: Days 2-5 — Follow-up Content

### Day 2: Short "How I Built It" Post

---

I built Skillshelf in one session using Claude Code itself.

The irony? I used Claude to build a tool that helps you find skills... for Claude.

Here's what's inside:

- A Python scanner (stdlib only, zero dependencies)
- Notion-styled HTML template with liquid glass UI
- Smart niche tagging engine (12 categories, 120+ keywords)
- Fingerprint-based caching (repeat runs take 94ms)
- A skill recommendation engine

Total: 8 files. ~3,000 lines. Ships as a single self-contained HTML report.

The hardest part? Making the Apple Liquid Glass filter pills look right.

Link in first comment.

#BuildInPublic #ClaudeCode #AI

---

### Day 3-4: Feature Highlight Post

---

"Which skill can help me write a cold email?"

That's a real prompt you can type in Claude Code with Skillshelf installed.

It scans your 291 installed capabilities, matches your intent against niche tags and descriptions, and returns the top 3-5 relevant skills.

No more guessing. No more scrolling through menus.

Just ask what you want to do. Skillshelf tells you which tool to use.

Works for:
- "design a carousel" → social-media-manager, superdesign
- "build an API" → backend-architect, senior-developer
- "review my code" → code-reviewer, security-engineer
- "optimize SEO" → searchfit-seo, seo-specialist

Free: github.com/muteebmrj/skillshelf

#ClaudeCode #AI #ProductivityHack

---

## Phase 3: Community Seeding

### Where to share (in order of impact):

1. **LinkedIn** (primary — you're already there)
2. **X/Twitter** — Short version: "Built a free skill inventory dashboard for Claude Code. 291 capabilities in one view. Apple Liquid Glass UI. github.com/muteebmrj/skillshelf"
3. **Reddit** — r/ClaudeAI, r/MachineLearning, r/artificial — title: "I built a free Claude Code skill that shows you everything you have installed"
4. **Anthropic Discord** — Share in the #claude-code channel
5. **Hacker News** — "Show HN: Skillshelf – Interactive skill inventory for Claude Code" (only if you want maximum exposure)

### Community engagement tactics:

- **Reply to everyone** who comments on your LinkedIn post within the first 2 hours (LinkedIn algorithm rewards early engagement)
- **Ask a question** in the post or comments: "How many skills do YOU have installed? Drop your number below after running it"
- **Star your own repo** — it shows 1 star immediately which looks better than 0
- **Add a demo GIF** to the GitHub README later (screen recording of using the dashboard)

---

## Quick Wins

- [ ] Take the 4-5 screenshots listed above
- [ ] Post the LinkedIn post (copy from above, attach images)
- [ ] Immediately comment with the install command
- [ ] Star your own repo
- [ ] Share the LinkedIn post URL on X/Twitter with a shorter hook
- [ ] Post in r/ClaudeAI on Reddit
- [ ] Share in Anthropic Discord #claude-code channel
