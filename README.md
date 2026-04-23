# Lucida

[中文](.github/docs/README-zh.md)

> Named after *Camera Lucida* — a 19th-century optical instrument for portrait drawing.

**Personality profiling from your AI conversation data.** A toy project that reads your chat history with AI coding assistants and generates shareable visual profile cards.

<div align="center">
  <img src=".github/assets/preview-en.png" alt="Seven Deadly Sins Profile Card" width="720">
</div>

## Profiling Systems

### Seven Deadly Sins ✅

Scores you across 7 dimensions — Sloth, Pride, Lust, Gluttony, Greed, Envy, Wrath — based on how you interact with AI. Matches you to one of 32 personality archetypes and renders a shareable HTML card.

### Jianghu Sects 🚧

*Coming soon.* Wuxia-themed profiling — Shaolin, Huashan, Xiaoyao, and more.

## Quick Start

Requires [Claude Code](https://claude.ai/claude-code).

```bash
# Clone and enter the project
git clone https://github.com/vimo-ai/lucida.git
cd lucida

# Run the skill in Claude Code
claude
# then type: /seven-sins
```

The skill is at `.claude/skills/seven-sins/SKILL.md` — Claude Code auto-detects it when you run Claude inside the project directory.

## Data Sources

| Priority | Path | Description |
|----------|------|-------------|
| 1 | `~/.claude/projects/` | Claude Code native JSONL (everyone has this) |
| 2 | `~/.vimo/db/ai-cli-session.db` | [Memex](https://github.com/vimo-ai/memex) session database (richer) |

### Why Memex?

Claude Code local data expires after 30 days by default (adjustable via `cleanupPeriodDays`). Even with retention extended, raw JSONL files are flat files on disk — no indexing, no search. [Memex](https://github.com/vimo-ai/memex) gives you:

- **Structured storage** — sessions and messages in SQLite with full schema
- **Full-text + semantic search** — FTS5 and vector search, find anything instantly
- **Multi-CLI unified** — Claude Code, Codex, OpenCode, Gemini in one database

More data = richer profiles. A month of chats gives you a sketch; a year gives you a portrait.

## How It Works

The profiling pipeline has a shared foundation and swappable "lenses":

```
shared/data-extraction.md    → common: data source detection + behavioral metric extraction
.claude/skills/seven-sins/   → lens: sin scoring + 32 archetype matching + HTML card
.claude/skills/jianghu/      → lens: (coming soon)
```

1. **Scan** — detect and read available data sources
2. **Extract** — compute behavioral metrics (message patterns, activity rhythms, communication style, etc.)
3. **Score** — map metrics to the chosen profiling system's dimensions
4. **Match** — find the closest archetype via weighted Euclidean distance
5. **Render** — fill a data-driven HTML template into a shareable card

## Project Structure

```
lucida/
├── .claude/skills/seven-sins/
│   ├── SKILL.md              # Seven Sins profiling skill
│   └── personality-types.md  # 32 archetype definitions
├── shared/
│   └── data-extraction.md    # Common data pipeline
├── templates/
│   └── seven-sins.html       # Report template (data-driven)
├── output/                   # Generated reports (gitignored)
└── README.md
```

## License

MIT

---

[vimo-ai](https://github.com/vimo-ai)
