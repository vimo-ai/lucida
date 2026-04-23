# Data Extraction — Common Pipeline

All profiling systems share this pipeline. Run Phase 1–2, then hand off the extracted metrics to the specific profiling skill.

**Language adaptation**: Before extracting keyword-based metrics, sample 20–30 user messages to detect the user's primary language. All keyword matching below must use the user's actual language — the examples given are illustrative, not exhaustive. Adapt patterns to the detected language(s).

## Phase 1: Data Source Detection

Detect available sources in order. Use the first available; if both exist, prefer session-db for richer data.

1. **Claude JSONL** (universal): `~/.claude/projects/*/`
   - Check: `find ~/.claude/projects -name "*.jsonl" | head -5`
   - Parse JSONL to extract user messages
   - Available to all Claude Code users

2. **Memex session-db** (richest): `~/.vimo/db/ai-cli-session.db`
   - Check: `sqlite3 ~/.vimo/db/ai-cli-session.db "SELECT COUNT(*) FROM messages WHERE type='user'"`
   - Requirement: ≥ 1000 user messages for statistical significance
   - Provides project paths, multi-CLI data, structured metadata

If neither is available, inform the user that data is insufficient.

Report the data source and message count; let the user confirm before proceeding.

## Phase 2: Behavioral Metric Extraction

### 2.1 Basic Stats

```sql
-- Exclude automated messages like Warmup
SELECT COUNT(*) as total_user_msgs FROM messages WHERE type='user' AND content_text != 'Warmup';
SELECT COUNT(DISTINCT session_id) as total_sessions FROM messages;
SELECT COUNT(DISTINCT date(timestamp/1000, 'unixepoch', 'localtime')) as active_days FROM messages WHERE type='user';
```

### 2.2 Message Characteristics

| Metric | Description | Applicability |
|--------|-------------|---------------|
| Short message ratio | % of messages ≤5 chars, ≤20 chars | All |
| Top frequent messages | Top 10 messages + occurrence count | All |
| Delegation keywords | Words expressing "do it for me" / "just handle it" (e.g. EN: fix, just do; ZH: 帮我, 直接; JA: やって, お願い) | All |
| Input-output ratio | User avg message length vs assistant avg length | All |
| Paste ratio | % of messages containing code blocks / error logs / long pasted text | Developers |
| Long message density | % of messages >500 chars | All |

### 2.3 Communication Style

| Metric | Description | Applicability |
|--------|-------------|---------------|
| Context-less ratio | % of messages <30 chars without explanation words (e.g. EN: because, context; ZH: 因为; ES: porque) | All |
| Negation/correction | Words expressing "no / wrong / you misunderstood" in user's language | All |
| Solution-driven ratio | User proposing solutions vs asking AI for solutions | Experienced devs |
| Imperative ratio | % of command-style messages (no question marks, no politeness markers) | All |
| Self-built tendency | Frequency of mentioning own project/tool names | Wheel-reinventing devs |

### 2.4 Activity Patterns

| Metric | Description | Applicability |
|--------|-------------|---------------|
| Daily message volume | Total user messages / active days | All |
| Session density | Avg messages per session | All |
| Marathon ratio | % of sessions >3 hours | All |
| Longest session | Duration + message count of longest session | All |
| Late night ratio | % of messages during 0:00–5:00 | All |
| Monthly growth | Month-over-month message volume growth rate | Long-term users |
| Time distribution | % across 4 blocks: 0-5 / 6-11 / 12-17 / 18-23 | All |

### 2.5 Scope & Ambition

| Metric | Description | Applicability |
|--------|-------------|---------------|
| Rewrite impulse | Words expressing "rewrite / from scratch / start over" in user's language | Wheel-reinventing |
| Scope words | Words expressing "all / everything / complete / entire" in user's language | All |
| Additive demands | Words expressing "also / by the way / one more thing" in user's language | All |
| Multi-demand messages | % of messages containing numbered lists (1. 2. 3.) | All |
| High-intensity days | % of days with >2000 messages | Heavy users |

### 2.6 External References

| Metric | Description | Applicability |
|--------|-------------|---------------|
| Source reading | Words expressing "look at the code / read the source / how is it implemented" in user's language | Developers |
| Clone/fork | "clone/fork" frequency | Developers |
| URL references | % of messages containing http/github.com/stackoverflow | All |
| Competitor comparison | Patterns expressing "like XX / how do others do it / reference" in user's language | All |
| Reference projects | Projects with paths containing github/reference/demo | session-db users |
| Learning intent | Words expressing "how does / learn / understand" in user's language | All |

### 2.7 Control & Frustration

| Metric | Description | Applicability |
|--------|-------------|---------------|
| Interrupts | '[Request interrupted by user]' count and ratio | All |
| Emotion words | Frustration/exasperation expressions in user's language (e.g. EN: wtf, ugh; ZH: 崩溃, 天哪; JA: まじで) | All |
| Redo words | Words expressing "redo / revert / undo / forget it" in user's language | All |
| Consecutive negations | Frequency of 2+ consecutive negative messages in same session | All |
| Short-lived sessions | % of sessions ending within <5 messages | All |
| Repeated questions | Frequency of similar questions appearing 2+ times in same session | All |

### 2.8 Diversity

| Metric | Description | Applicability |
|--------|-------------|---------------|
| Project count | Number of distinct project paths | session-db users |
| Project switching | Avg daily project switches | session-db users |
| Language diversity | Number of programming languages mentioned | Developers |
| Topic diversity | Topic domain variety across sessions (inferred from paths/content) | All |
| Tech stack drift | Monthly variation in tech stack mentions | Long-term users |
| Tool diversity | Number of distinct AI sources (claude/codex/gemini etc.) | Multi-tool users |

### 2.9 Supplementary Data (for profile narrative)

- AI source distribution (claude/codex/gemini/opencode)
- Top 10 frequent short messages
- Top 20 project names (interest domains)
- Monthly activity curve
- User message sampling (10–15 medium-long messages for writing style)

**Note**: Metrics in 2.8 and some in 2.4 are richest with session-db. When using JSONL, skip unavailable metrics — not all dimensions need to score. Profiling systems should handle incomplete data gracefully.
