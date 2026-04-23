# Data Extraction — Common Pipeline

All profiling systems share this pipeline. Run the extraction script, then hand off the metrics JSON to the specific profiling skill.

## Quick Start

```bash
python3 scripts/extract-metrics.py > /tmp/lucida-metrics.json
```

The script auto-detects data sources, applies filters, computes all Phase 1–2 metrics, and outputs JSON to stdout. Source detection and progress go to stderr.

After getting the metrics JSON, the AI skill should:
1. Use the JSON for scoring (Phase 3) — all numbers are pre-computed
2. Go back to raw data for **content sampling and deep dives** (Phase 4) — read actual messages for writing style, behavioral patterns, and qualitative insights that stats alone can't capture
3. If any metric looks off, the AI can query raw data directly to verify

**Language adaptation**: Before extracting keyword-based metrics, sample 20–30 user messages to detect the user's primary language. All keyword matching below must use the user's actual language — the examples given are illustrative, not exhaustive. Adapt patterns to the detected language(s).

## Phase 1: Data Source Detection

Detect available sources. Use the richest available; if multiple exist, prefer session-db (multi-tool, structured), otherwise merge Claude JSONL + Codex.

1. **Memex session-db** (richest, multi-tool): `~/.vimo/db/ai-cli-session.db`
   - Check: `sqlite3 ~/.vimo/db/ai-cli-session.db "SELECT COUNT(*) FROM messages WHERE type='user'"`
   - Covers: Claude, Codex, Gemini, OpenCode — all in one DB
   - Provides session metadata, project paths, source attribution
   - **Requires filtering** — see "User Message Filter" below

2. **Claude JSONL** (universal, clean): `~/.claude/projects/*/`
   - Check: `find ~/.claude/projects -name "*.jsonl" -not -path "*/subagents/*" | head -5`
   - Parse JSONL: entries with `"type":"user"` where `message.content` is a string (not a `tool_result` array)
   - Exclude subagent files (`*/subagents/*.jsonl`) unless you want agent-delegated turns
   - Metadata available per entry: `timestamp`, `cwd`, `sessionId`, `gitBranch`, `version`

3. **Codex** (OpenAI CLI, clean): `~/.codex/`
   - Check: `test -f ~/.codex/history.jsonl && wc -l ~/.codex/history.jsonl`
   - `~/.codex/history.jsonl` — one line per user message: `{"session_id":"…","ts":unix_sec,"text":"…"}` (no noise, ready to use)
   - `~/.codex/state_5.sqlite` — `threads` table with session metadata (cwd, model, source, git_branch, created_at, updated_at)
   - `~/.codex/sessions/{YYYY}/{MM}/{DD}/rollout-*.jsonl` — full session transcripts (session_meta, response_item, event_msg, turn_context)

If no source is available, inform the user that data is insufficient.

Report each data source and its **filtered** message count; let the user confirm before proceeding.

### User Message Filter (session-db)

Session-db stores all JSONL entries with `type='user'` — including **tool results** and **system-injected messages** that are not real human input. Raw counts can be 5-10x inflated. Apply this filter:

```sql
-- Real user messages only
SELECT * FROM messages
WHERE type = 'user'
  AND content_text != ''                                        -- tool_result entries have empty content_text
  AND content_full NOT LIKE '[Result]%'                         -- tool execution results
  AND content_full NOT LIKE '[Result Error]%'                   -- tool error results
  AND content_text != 'Warmup'                                  -- heartbeat/warmup probes
  AND content_text NOT LIKE '[Request interrupted by user%'     -- interrupt signals (includes "for tool use" variant)
  AND content_text NOT LIKE '[SUGGESTION MODE%'                 -- suggestion prompt injection
  AND content_text NOT LIKE '<local-command%'                   -- local command output wrappers
  AND content_text NOT LIKE '<command-name>%'                   -- slash command invocations
  AND content_text NOT LIKE '<command-message>%'                -- slash command bodies
  AND content_text NOT LIKE 'Caveat: The messages below%'       -- local command caveats
  AND content_text NOT LIKE 'Your task is to create a detailed summary%'  -- compact/summary prompts
  AND content_text NOT LIKE '<local-command-stdout>%'           -- local command stdout wrappers
  AND content_text NOT LIKE '<permissions instructions>%'       -- Codex permission injection
  AND content_text NOT LIKE '<environment_context>%'            -- Codex environment injection
  AND content_text NOT LIKE '<collaboration_mode>%'             -- collaboration mode injection
  AND content_text NOT LIKE '<turn_aborted>%'                   -- turn abort signals
  AND content_text NOT LIKE 'This session is being continued from%'  -- continuation prompts
  AND content_text NOT LIKE '# AGENTS.md instructions%'         -- Codex AGENTS.md injection
  AND content_text NOT LIKE '%<INSTRUCTIONS>%'                  -- instruction block injection
  AND content_text NOT LIKE 'Base directory for this skill:%'   -- skill body injection
  AND content_text NOT LIKE '## Context%'                       -- skill context injection
  AND content_text NOT LIKE 'Tool loaded%'                      -- tool loading notifications
  AND content_text NOT LIKE 'CRITICAL: Respond with TEXT ONLY%'  -- compact prompt variant
```

**Why this matters**: without filtering, tool_result entries (content_text='', content_full='[Result]...') inflate message counts ~5x and push short-message ratio from ~38% to ~85%, completely distorting the profile.

### User Message Filter (Claude JSONL)

Claude JSONL entries with `"type":"user"` include both human messages and tool results. Distinguish by `message.content`:
- **String** → real user message
- **Array of `{"type":"tool_result",...}`** → tool return, skip

```python
if obj.get('type') == 'user' and 'message' in obj:
    content = obj['message'].get('content', '')
    if isinstance(content, str) and len(content) > 0:
        # Real user message
```

## Phase 2: Behavioral Metric Extraction

### 2.1 Basic Stats

All queries below assume the user message filter is applied. For brevity, session-db examples use a `clean_user_msgs` alias — define it as a CTE or view using the filter above.

```sql
-- Session-db
SELECT COUNT(*) as total_user_msgs FROM clean_user_msgs;
SELECT COUNT(DISTINCT session_id) as total_sessions FROM clean_user_msgs;
SELECT COUNT(DISTINCT date(timestamp/1000, 'unixepoch', 'localtime')) as active_days FROM clean_user_msgs;
-- Source breakdown
SELECT source, COUNT(*) FROM clean_user_msgs GROUP BY source;
```

```bash
# Codex (native, no filter needed)
wc -l ~/.codex/history.jsonl
sqlite3 ~/.codex/state_5.sqlite "SELECT COUNT(*) FROM threads"
sqlite3 ~/.codex/state_5.sqlite "SELECT COUNT(DISTINCT date(created_at, 'unixepoch', 'localtime')) FROM threads"
```

When merging native sources (Claude JSONL + Codex), deduplicate by timestamp + content hash to avoid double-counting.

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
| Reference projects | Projects with paths containing github/reference/demo | session-db / Codex |
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
| Project count | Number of distinct project paths | session-db / Codex |
| Project switching | Avg daily project switches | session-db / Codex |
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

**Note**: Metrics in 2.8 and some in 2.4 are richest with session-db (multi-source, has project paths) or Codex's `state_5.sqlite` (provides `cwd` per thread). Claude JSONL also carries `cwd` per entry. When a metric is unavailable from the data source, skip it — not all dimensions need to score. Profiling systems should handle incomplete data gracefully.

**Data quality check**: After filtering, verify that message length stats are reasonable — avg length ~280-320 chars, short message ratio (≤20 chars) ~35-40%. If short message ratio exceeds 60%, the filter is likely incomplete.
