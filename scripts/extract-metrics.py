#!/usr/bin/env python3
"""
Lucida — Behavioral Metrics Extraction

Detects available AI conversation data sources, extracts user messages,
computes behavioral metrics, and outputs structured JSON to stdout.

Data sources (checked in order):
  1. Memex session-db  (~/.vimo/db/ai-cli-session.db) — richest, multi-tool
  2. Claude JSONL       (~/.claude/projects/*/)         — universal
  3. Codex              (~/.codex/)                     — OpenAI CLI

When session-db is available, it's used as the primary source (already aggregates
all tools). Otherwise, native sources are merged.

Output: JSON to stdout. AI skills consume this for scoring/profiling,
then go back to raw data for content sampling and deep dives.
"""

import json
import os
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

HOME = Path.home()

# ---------------------------------------------------------------------------
# Data source detection
# ---------------------------------------------------------------------------

def detect_sources():
    sources = {}

    session_db = HOME / ".vimo" / "db" / "ai-cli-session.db"
    if session_db.exists():
        try:
            conn = sqlite3.connect(str(session_db))
            count = conn.execute("SELECT COUNT(*) FROM messages WHERE type='user'").fetchone()[0]
            conn.close()
            if count > 0:
                sources["session_db"] = {"path": str(session_db), "raw_count": count}
        except Exception:
            pass

    claude_dir = HOME / ".claude" / "projects"
    if claude_dir.exists():
        jsonl_files = list(claude_dir.rglob("*.jsonl"))
        main_files = [f for f in jsonl_files if "/subagents/" not in str(f)]
        if main_files:
            sources["claude"] = {"path": str(claude_dir), "files": len(main_files), "subagent_files": len(jsonl_files) - len(main_files)}

    codex_history = HOME / ".codex" / "history.jsonl"
    if codex_history.exists():
        try:
            line_count = sum(1 for _ in open(codex_history))
            if line_count > 0:
                sources["codex"] = {"path": str(codex_history), "entries": line_count}
        except Exception:
            pass

    codex_db = HOME / ".codex" / "state_5.sqlite"
    if codex_db.exists():
        try:
            conn = sqlite3.connect(str(codex_db))
            threads = conn.execute("SELECT COUNT(*) FROM threads").fetchone()[0]
            conn.close()
            if "codex" not in sources:
                sources["codex"] = {}
            sources["codex"]["threads_db"] = str(codex_db)
            sources["codex"]["threads"] = threads
        except Exception:
            pass

    return sources

# ---------------------------------------------------------------------------
# Message extraction — session-db
# ---------------------------------------------------------------------------

SESSION_DB_FILTER = """
    type = 'user'
    AND content_text != ''
    AND content_full NOT LIKE '[Result]%'
    AND content_full NOT LIKE '[Result Error]%'
    AND content_text != 'Warmup'
    AND content_text NOT LIKE '[Request interrupted by user%'
    AND content_text NOT LIKE '[SUGGESTION MODE%'
    AND content_text NOT LIKE '<local-command%'
    AND content_text NOT LIKE '<command-name>%'
    AND content_text NOT LIKE '<command-message>%'
    AND content_text NOT LIKE 'Caveat: The messages below%'
    AND content_text NOT LIKE '%Your task is to create a detailed summary%'
    AND content_text NOT LIKE '<local-command-stdout>%'
    AND content_text NOT LIKE '<permissions instructions>%'
    AND content_text NOT LIKE '<environment_context>%'
    AND content_text NOT LIKE '<collaboration_mode>%'
    AND content_text NOT LIKE '<turn_aborted>%'
    AND content_text NOT LIKE 'This session is being continued from%'
    AND content_text NOT LIKE '# AGENTS.md instructions%'
    AND content_text NOT LIKE '%<INSTRUCTIONS>%'
    AND content_text NOT LIKE 'Base directory for this skill:%'
    AND content_text NOT LIKE '## Context%'
    AND content_text NOT LIKE 'Tool loaded%'
    AND content_text NOT LIKE 'CRITICAL: Respond with TEXT ONLY%'
"""

def extract_from_session_db(db_path):
    conn = sqlite3.connect(db_path)
    rows = conn.execute(f"""
        SELECT session_id, content_text, timestamp, source
        FROM messages WHERE {SESSION_DB_FILTER}
        ORDER BY timestamp
    """).fetchall()
    conn.close()

    messages = []
    for session_id, text, ts, source in rows:
        messages.append({
            "session_id": session_id,
            "text": text,
            "ts": ts / 1000.0,
            "source": source or "claude",
        })
    return messages

# ---------------------------------------------------------------------------
# Message extraction — Claude JSONL
# ---------------------------------------------------------------------------

def extract_from_claude_jsonl(projects_dir):
    messages = []
    projects_path = Path(projects_dir)

    for jsonl_file in projects_path.rglob("*.jsonl"):
        if "/subagents/" in str(jsonl_file):
            continue
        try:
            with open(jsonl_file) as f:
                for line in f:
                    try:
                        obj = json.loads(line.strip())
                        if obj.get("type") != "user" or "message" not in obj:
                            continue
                        content = obj["message"].get("content", "")
                        if not isinstance(content, str) or len(content) == 0:
                            continue
                        ts_str = obj.get("timestamp", "")
                        try:
                            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00")).timestamp()
                        except Exception:
                            ts = 0
                        messages.append({
                            "session_id": obj.get("sessionId", jsonl_file.stem),
                            "text": content,
                            "ts": ts,
                            "source": "claude",
                        })
                    except json.JSONDecodeError:
                        continue
        except Exception:
            continue

    return messages

# ---------------------------------------------------------------------------
# Message extraction — Codex
# ---------------------------------------------------------------------------

def extract_from_codex(history_path):
    messages = []
    try:
        with open(history_path) as f:
            for line in f:
                try:
                    obj = json.loads(line.strip())
                    text = obj.get("text", "")
                    if not text:
                        continue
                    messages.append({
                        "session_id": obj.get("session_id", ""),
                        "text": text,
                        "ts": float(obj.get("ts", 0)),
                        "source": "codex",
                    })
                except json.JSONDecodeError:
                    continue
    except Exception:
        pass
    return messages

# ---------------------------------------------------------------------------
# Metrics computation
# ---------------------------------------------------------------------------

# Keyword patterns (multi-language)
DELEGATION_RE = re.compile(r"帮我|直接|搞一下|你来|处理一下|fix |just do|handle |搞个|弄一下", re.IGNORECASE)
NEGATION_RE = re.compile(r"不对|不是这|错了|wrong|你误解|不要这|no[, ]|isn't|不行", re.IGNORECASE)
SOLUTION_RE = re.compile(r"我觉得|我想要?|我打算|方案|我认为|I think|my approach", re.IGNORECASE)
REWRITE_RE = re.compile(r"重写|重构|rewrite|from scratch|重新写|重新来", re.IGNORECASE)
SCOPE_RE = re.compile(r"所有|全部|整个|complete|entire|all of|每一个", re.IGNORECASE)
ADDITIVE_RE = re.compile(r"还有|另外|顺便|also|by the way|再加|one more|补充", re.IGNORECASE)
EMOTION_RE = re.compile(r"崩溃|wtf|离谱|服了|卧槽|我去|天哪|ugh|damn|shit|艹|mmp", re.IGNORECASE)
REDO_RE = re.compile(r"撤销|回退|revert|undo|算了|还原|回滚", re.IGNORECASE)
URL_RE = re.compile(r"https?://|github\.com|stackoverflow", re.IGNORECASE)
LEARNING_RE = re.compile(r"怎么[^样]|为什么|how does|why does|了解一下|学一下|explain", re.IGNORECASE)
REF_RE = re.compile(r"参考|reference|像.{1,10}一样|similar to|look at", re.IGNORECASE)
CLONE_RE = re.compile(r"\bclone\b|\bfork\b", re.IGNORECASE)
SOURCE_READ_RE = re.compile(r"看[看下].*(?:代码|源码|实现)|read the source|how.+implemented", re.IGNORECASE)
QUESTION_RE = re.compile(r"[？?]")
POLITE_RE = re.compile(r"请|please|麻烦|thank|谢|sorry|抱歉", re.IGNORECASE)
PASTE_RE = re.compile(r"```|Traceback|stacktrace|Error:|error:", re.IGNORECASE)
MULTI_DEMAND_RE = re.compile(r"(?:^|\n)\s*1[.、].+(?:^|\n)\s*2[.、]", re.MULTILINE)
STRUCTURED_RE = re.compile(r"(?:\w+/\w+\.\w+|:\d+|\.(?:ts|js|py|rs|go|vue|tsx|jsx|css|html|json|yaml|toml|md)\b)", re.IGNORECASE)
PRECISE_ACTION_RE = re.compile(r"改成|换成|替换|rename|replace .+ with|change .+ to|移到|删掉|加上|改为", re.IGNORECASE)


def compute_metrics(messages):
    if not messages:
        return {"error": "no messages"}

    total = len(messages)
    texts = [m["text"] for m in messages]
    lengths = [len(t) for t in texts]
    sessions = set(m["session_id"] for m in messages)
    sources = Counter(m["source"] for m in messages)

    timestamps = [m["ts"] for m in messages if m["ts"] > 0]
    dates = set()
    hours = []
    monthly = defaultdict(int)
    for ts in timestamps:
        dt = datetime.fromtimestamp(ts)
        dates.add(dt.date())
        hours.append(dt.hour)
        monthly[dt.strftime("%Y-%m")] += 1

    active_days = len(dates) or 1
    date_range = {}
    if dates:
        date_range = {"start": str(min(dates)), "end": str(max(dates))}

    # Session-level stats
    session_msgs = defaultdict(list)
    for m in messages:
        session_msgs[m["session_id"]].append(m["ts"])

    session_sizes = {sid: len(tss) for sid, tss in session_msgs.items()}
    short_sessions = sum(1 for c in session_sizes.values() if c < 5)

    # Time blocks
    hour_counts = Counter(hours)
    block_0_5 = sum(hour_counts.get(h, 0) for h in range(0, 6))
    block_6_11 = sum(hour_counts.get(h, 0) for h in range(6, 12))
    block_12_17 = sum(hour_counts.get(h, 0) for h in range(12, 18))
    block_18_23 = sum(hour_counts.get(h, 0) for h in range(18, 24))
    ts_total = len(hours) or 1

    # Daily volume distribution
    daily_counts = Counter()
    for ts in timestamps:
        daily_counts[datetime.fromtimestamp(ts).date()] += 1
    daily_values = list(daily_counts.values()) if daily_counts else [0]
    high_days = sum(1 for v in daily_values if v > 200)

    # Consecutive active days
    consecutive_days = 1
    if dates:
        sorted_dates = sorted(dates)
        cur_streak = 1
        for i in range(1, len(sorted_dates)):
            if (sorted_dates[i] - sorted_dates[i - 1]).days == 1:
                cur_streak += 1
                consecutive_days = max(consecutive_days, cur_streak)
            else:
                cur_streak = 1

    # Marathon sessions (>100 messages)
    marathon_count = sum(1 for c in session_sizes.values() if c > 100)
    total_sessions = max(len(session_sizes), 1)

    # Growth ratio (last 3 months avg / first 3 months avg)
    sorted_months = sorted(monthly.keys())
    growth_ratio = 1.0
    if len(sorted_months) >= 2:
        n = max(len(sorted_months) // 3, 1)
        early = [monthly[m] for m in sorted_months[:n]]
        late = [monthly[m] for m in sorted_months[-n:]]
        early_avg = sum(early) / len(early)
        if early_avg > 0:
            growth_ratio = round(sum(late) / len(late) / early_avg, 2)

    # Sessions per day
    sessions_per_day = round(len(sessions) / active_days, 2)

    # Substantive messages (>50 chars)
    sub_texts = [t for t in texts if len(t) > 50]
    sub_total = max(len(sub_texts), 1)

    def sub_pct(regex):
        return round(100.0 * sum(1 for t in sub_texts if regex.search(t)) / sub_total, 1)

    sub_lengths = [len(t) for t in sub_texts]

    # Keyword matching
    def pct(regex):
        return round(100.0 * sum(1 for t in texts if regex.search(t)) / total, 1)

    # Message characteristics
    top_messages = Counter(texts).most_common(15)

    # Build result
    result = {
        "data_quality": {
            "avg_len": round(sum(lengths) / total, 1),
            "short_5_pct": round(100.0 * sum(1 for l in lengths if l <= 5) / total, 1),
            "short_20_pct": round(100.0 * sum(1 for l in lengths if l <= 20) / total, 1),
            "gt_500_pct": round(100.0 * sum(1 for l in lengths if l > 500) / total, 1),
            "check": "OK" if round(100.0 * sum(1 for l in lengths if l <= 20) / total, 1) < 60 else "WARN: short_20_pct > 60%, filter may be incomplete",
        },
        "sources": dict(sources),
        "date_range": date_range,
        "basic": {
            "total_msgs": total,
            "sessions": len(sessions),
            "active_days": active_days,
            "daily_volume": round(total / active_days, 1),
        },
        "message": {
            "avg_len": round(sum(lengths) / total, 1),
            "median_len": sorted(lengths)[total // 2],
            "short_5_pct": round(100.0 * sum(1 for l in lengths if l <= 5) / total, 1),
            "short_20_pct": round(100.0 * sum(1 for l in lengths if l <= 20) / total, 1),
            "gt_500_pct": round(100.0 * sum(1 for l in lengths if l > 500) / total, 1),
            "delegation_pct": pct(DELEGATION_RE),
            "paste_pct": round(100.0 * sum(1 for t in texts if PASTE_RE.search(t) or len(t) > 1000) / total, 1),
            "top_messages": [[t, c] for t, c in top_messages],
        },
        "communication": {
            "contextless_pct": round(100.0 * sum(1 for t in texts if len(t) < 30 and "因为" not in t and "because" not in t.lower() and "背景" not in t) / total, 1),
            "imperative_pct": round(100.0 * sum(1 for t in texts if not QUESTION_RE.search(t) and not POLITE_RE.search(t)) / total, 1),
            "negation_pct": pct(NEGATION_RE),
            "solution_driven_pct": pct(SOLUTION_RE),
        },
        "activity": {
            "daily_volume": round(total / active_days, 1),
            "session_density": round(total / max(len(sessions), 1), 1),
            "late_night_pct": round(100.0 * block_0_5 / ts_total, 1),
            "time_blocks": {
                "0-5": round(100.0 * block_0_5 / ts_total, 1),
                "6-11": round(100.0 * block_6_11 / ts_total, 1),
                "12-17": round(100.0 * block_12_17 / ts_total, 1),
                "18-23": round(100.0 * block_18_23 / ts_total, 1),
            },
            "high_intensity_days_pct": round(100.0 * high_days / active_days, 1),
            "max_daily_msgs": max(daily_values),
            "short_sessions_pct": round(100.0 * short_sessions / max(len(session_sizes), 1), 1),
            "sessions_per_day": sessions_per_day,
            "consecutive_days": consecutive_days,
            "marathon_pct": round(100.0 * marathon_count / total_sessions, 1),
            "growth_ratio": growth_ratio,
            "monthly": dict(sorted(monthly.items())),
        },
        "scope": {
            "rewrite_pct": pct(REWRITE_RE),
            "scope_words_pct": pct(SCOPE_RE),
            "additive_pct": pct(ADDITIVE_RE),
            "multi_demand_pct": round(100.0 * sum(1 for t in texts if MULTI_DEMAND_RE.search(t)) / total, 1),
        },
        "refs": {
            "source_reading_pct": pct(SOURCE_READ_RE),
            "clone_fork_pct": pct(CLONE_RE),
            "url_pct": pct(URL_RE),
            "ref_comparison_pct": pct(REF_RE),
            "learning_pct": pct(LEARNING_RE),
            "question_pct": round(100.0 * sum(1 for t in texts if QUESTION_RE.search(t)) / total, 1),
        },
        "frustration": {
            "emotion_pct": pct(EMOTION_RE),
            "redo_pct": pct(REDO_RE),
        },
        "substantive": {
            "count": len(sub_texts),
            "avg_len": round(sum(sub_lengths) / sub_total, 1) if sub_lengths else 0,
            "structured_pct": sub_pct(STRUCTURED_RE),
            "precise_action_pct": sub_pct(PRECISE_ACTION_RE),
            "scope_pct": sub_pct(SCOPE_RE),
            "additive_pct": sub_pct(ADDITIVE_RE),
            "rewrite_pct": sub_pct(REWRITE_RE),
        },
        "diversity": {
            "source_count": len(sources),
            "session_count": len(sessions),
        },
    }

    return result


# ---------------------------------------------------------------------------
# Interrupt count (separate from clean messages)
# ---------------------------------------------------------------------------

def count_interrupts_session_db(db_path):
    try:
        conn = sqlite3.connect(db_path)
        count = conn.execute(
            "SELECT COUNT(*) FROM messages WHERE type='user' AND content_text LIKE '[Request interrupted by user]'"
        ).fetchone()[0]
        conn.close()
        return count
    except Exception:
        return 0


def get_project_diversity_session_db(db_path):
    try:
        conn = sqlite3.connect(db_path)
        project_count = conn.execute(
            "SELECT COUNT(DISTINCT cwd) FROM sessions WHERE cwd IS NOT NULL"
        ).fetchone()[0]
        rows = conn.execute("""
            SELECT DATE(m.timestamp/1000, 'unixepoch') as day, COUNT(DISTINCT s.cwd) as projects
            FROM messages m JOIN sessions s ON m.session_id = s.session_id
            WHERE m.type='user' AND s.cwd IS NOT NULL
            GROUP BY day
        """).fetchall()
        daily_switches = [r[1] for r in rows] if rows else [0]
        conn.close()
        return {
            "project_count": project_count,
            "daily_project_switches": round(sum(daily_switches) / max(len(daily_switches), 1), 1),
        }
    except Exception:
        return {"project_count": 0, "daily_project_switches": 0}


def count_interrupts_claude_jsonl(projects_dir):
    count = 0
    for jsonl_file in Path(projects_dir).rglob("*.jsonl"):
        try:
            with open(jsonl_file) as f:
                for line in f:
                    if '"[Request interrupted by user]"' in line:
                        count += 1
        except Exception:
            continue
    return count


# ---------------------------------------------------------------------------
# Project count from Codex threads db
# ---------------------------------------------------------------------------

def get_codex_projects(db_path):
    try:
        conn = sqlite3.connect(db_path)
        count = conn.execute("SELECT COUNT(DISTINCT cwd) FROM threads").fetchone()[0]
        conn.close()
        return count
    except Exception:
        return 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    sources = detect_sources()

    if not sources:
        print(json.dumps({"error": "No data sources found. Need ~/.claude, ~/.codex, or ~/.vimo/db/ai-cli-session.db"}, indent=2))
        sys.exit(1)

    # Print source detection to stderr for user visibility
    print("Detected sources:", file=sys.stderr)
    for name, info in sources.items():
        print(f"  {name}: {json.dumps(info)}", file=sys.stderr)

    # Extract messages
    messages = []
    used_source = None

    if "session_db" in sources:
        used_source = "session_db"
        print("Using session-db (richest, multi-tool)...", file=sys.stderr)
        messages = extract_from_session_db(sources["session_db"]["path"])
    else:
        used_source = "native"
        if "claude" in sources:
            print("Extracting from Claude JSONL...", file=sys.stderr)
            messages.extend(extract_from_claude_jsonl(sources["claude"]["path"]))
        if "codex" in sources:
            print("Extracting from Codex history...", file=sys.stderr)
            messages.extend(extract_from_codex(sources["codex"]["path"]))
        messages.sort(key=lambda m: m["ts"])

    print(f"Extracted {len(messages)} clean user messages", file=sys.stderr)

    # Compute metrics
    metrics = compute_metrics(messages)
    metrics["_meta"] = {
        "extracted_at": datetime.now().isoformat(),
        "used_source": used_source,
        "available_sources": list(sources.keys()),
    }

    # Add interrupt count
    if "session_db" in sources:
        metrics["frustration"]["interrupt_count"] = count_interrupts_session_db(sources["session_db"]["path"])
    elif "claude" in sources:
        metrics["frustration"]["interrupt_count"] = count_interrupts_claude_jsonl(sources["claude"]["path"])

    metrics["frustration"]["interrupt_rate"] = round(
        100.0 * metrics["frustration"].get("interrupt_count", 0) / max(metrics["basic"]["total_msgs"], 1), 2
    )

    # Add project diversity
    if "session_db" in sources:
        proj = get_project_diversity_session_db(sources["session_db"]["path"])
        metrics["diversity"]["project_count"] = proj["project_count"]
        metrics["diversity"]["daily_project_switches"] = proj["daily_project_switches"]
    if "codex" in sources and "threads_db" in sources["codex"]:
        metrics["diversity"]["codex_projects"] = get_codex_projects(sources["codex"]["threads_db"])

    # Output
    print(json.dumps(metrics, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
