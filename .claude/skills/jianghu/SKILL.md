---
name: jianghu
description: Jianghu (martial arts world) personality profiling. Analyzes AI conversation history, scores 7 martial dimensions, matches to a sect + rank or a jianghu freelancer identity, and renders a shareable HTML card. Shared data pipeline in shared/data-extraction.md.
---

## Overview

Profile users across 7 martial dimensions (0–100), match to a sect with rank or a freelancer identity, generate a shareable HTML report.

**Prerequisites**: Run the shared data extraction pipeline first — see `shared/data-extraction.md` (Phase 1–2).

**Output**: Screenshot from Vite dev server (`templates/jianghu-dev/`)

## Execution Checklist

**MANDATORY**: Before doing ANY work, create a task list with ALL steps below. Complete and check off each step sequentially. Never skip ahead.

1. Extract metrics — run `scripts/extract-metrics.py`, verify output
2. Compute base scores — apply scoring formulas, present 7 dimension base scores
3. Message sampling — sample substantive messages from top projects + recent activity
4. Project depth assessment — read project structure and core code for top 3–5 projects
5. User alignment — present base scores + observations, ask user questions, wait for response (skip if all projects are shallow — see Step 3 trigger conditions)
6. Score correction — apply corrections based on user input (if asked) + content analysis
7. Identity matching Phase A — formula screening against sects.md
8. Identity matching Phase B — AI compatibility judgment on top candidates
9. Track decision + rank assignment — finalize sect/freelancer identity
10. Profile generation — tagline, data copy, summary, title, stamp text
11. Fill template — write `templates/jianghu-dev/src/data.ts`
12. Output — start Vite dev, screenshot, terminal summary
13. Cleanup — delete intermediate data (metrics JSON, temp files)

Each step must be marked complete before proceeding to the next. If a step reveals the need to revisit a prior step, note it explicitly.

## Phase 3: Scoring — Metrics → Martial Dimensions

Map extracted behavioral metrics to 7 martial dimensions. Each dimension draws from multiple metric categories.

### Dimension Definitions

**内力 (Inner Power) — Stamina & sustained output**
- Activity patterns: daily message volume, monthly growth trend, late night ratio
- Activity patterns: marathon ratio, consecutive active days
- Activity patterns: monthly volume trend — accelerating or decaying over time
- Key signal: not just "uses a lot" but "keeps going without fading"

**轻功 (Lightness) — Interaction pace & agility**
- Message characteristics: short message ratio, top frequent messages (confirmations like 好/ok/继续)
- Activity patterns: short-lived sessions ratio, messages per session variance
- Control & frustration: interrupt count (quick to cut off bad directions)
- Key signal: rapid-fire iteration rhythm, fast ACKs, quick pivots

**招式 (Technique) — Precision & information density**
- Measured on substantive messages only (>50 chars) to exclude confirmations
- Structured content ratio: file paths, line numbers, code extensions in user messages
- Precise action ratio: specific instructions ("改成X", "replace X with Y", "rename")
- Key signal: when they DO write, is it high-density or vague?
- Note: high short-message ratio does NOT lower this score — brevity in confirmations is 轻功, not low 招式

**杀气 (Killing Intent) — Aggression & control**
- Communication style: negation/correction ratio, imperative ratio
- Control & frustration: interrupts, emotion words, redo words, consecutive negations
- Key signal: distinguish precise correction (high negation + low emotion = 杀气 moderate) from emotional outburst (high negation + high emotion = 杀气 high)

**悟性 (Comprehension) — Curiosity depth + technical depth**
- External references: learning intent, source reading, URL references
- **Deep dive required**: sample messages from top projects (by session count) to assess technical depth
  1. Identify deep-engagement projects (high message count, spanning multiple days)
  2. Sample 15–20 substantive messages from these projects
  3. AI evaluates technical sophistication level — are they adjusting API params or reverse-engineering bytecode?
  4. Cross-reference project timeline to infer learning speed (new domain → competent usage timespan)
- Key signal: not "asks why often" but "what technical water level are they operating at"
- Keyword-based metrics only set a floor; content analysis can raise significantly

**野心 (Ambition) — Scope inflation**
- Scope keywords computed on substantive messages only (>50 chars) to avoid dilution by confirmations
- Scope & ambition: rewrite impulse, scope words, additive demands, multi-demand messages
- Project count as ambition signal: more projects = bigger appetite
- Key signal: do they keep expanding what they want?

**江湖阅历 (World Experience) — Breadth & diversity**
- Diversity: project count, daily project switches, tool diversity, language diversity
- Diversity: topic diversity across sessions
- Key signal: how many different worlds have they touched?

### Scoring Formula

Each raw metric is mapped to 0–100 via `linear(value, low, high)` or `log_scale(value, low, high)`, then combined per dimension with weighted average. Run `scripts/extract-metrics.py` to get raw metrics, then apply:

**内力 (Inner Power)**
```
wavg([
  (log_scale(daily_msgs, 10, 3500), 2.5),
  (linear(consecutive_days, 1, 180), 2.0),
  (linear(late_night_pct, 0, 30), 1.5),
  (linear(marathon_pct, 0, 30), 1.5),
  (linear(growth_ratio, 0.5, 2.5), 1.5),
])
```

**轻功 (Lightness)**
```
wavg([
  (linear(short_5_pct, 0, 70), 2.0),
  (linear(short_session_pct, 10, 80), 2.0),
  (log_scale(interrupt_rate, 0.1, 5), 1.5),
  (log_scale(sessions_per_day, 1, 50), 1.5),
])
```

**招式 (Technique)** — computed on substantive messages only (>50 chars)
```
wavg([
  (linear(sub_structured_pct, 5, 40), 3.0),       # file paths, line numbers, extensions
  (linear(sub_precise_action_pct, 2, 25), 2.0),   # "改成X", "replace X with Y"
  (linear(sub_avg_len, 80, 500), 1.0),             # length is minor floor check
])
```

**杀气 (Killing Intent)**
```
wavg([
  (linear(negation_pct, 2, 40), 2.0),
  (linear(emotion_pct, 0, 8), 2.5),       # emotion is the strongest signal
  (linear(redo_pct, 0, 3), 1.5),
  (log_scale(interrupt_rate, 0.1, 5), 1.0),
])
```

**悟性 (Comprehension)** — formula base only, content analysis raises in Phase 3.1
```
wavg([
  (linear(learning_pct, 0, 15), 2.5),
  (linear(source_reading_pct, 0, 3), 1.5),
  (linear(url_pct, 0, 8), 1.5),
  (linear(question_pct, 5, 50), 1.5),
])
```

**野心 (Ambition)** — scope/additive/rewrite computed on substantive messages only (>50 chars) to avoid dilution by confirmations
```
wavg([
  (linear(sub_scope_pct, 3, 30), 2.5),
  (linear(sub_additive_pct, 1, 12), 1.5),
  (linear(sub_rewrite_pct, 0, 5), 1.5),
  (linear(multi_demand_pct, 1, 20), 1.5),
  (log_scale(project_count, 10, 500), 1.0),   # sheer project scale as ambition signal
])
```

**江湖阅历 (World Experience)**
```
wavg([
  (log_scale(project_count, 3, 500), 2.5),
  (log_scale(daily_project_switches, 1, 15), 2.0),
  (linear(source_count, 1, 5), 1.5),
])
```

Helper functions:
```
linear(value, low, high) = clamp((value - low) / (high - low) * 100, 0, 100)
log_scale(value, low, high) = clamp(log(value/low) / log(high/low) * 100, 0, 100)
wavg([(score, weight), ...]) = Σ(score × weight) / Σ(weight)
```

## Phase 3.1: AI Content Sampling Correction

The formula gives a statistical base score. AI then samples actual messages and optionally inspects user projects to correct each dimension.

### Step 1: Message Sampling

1. Sample 10–15 substantive messages (>80 chars) from top projects (by message count)
2. Sample 5–10 messages from recent activity (last 2 weeks)
3. For each dimension, evaluate whether the formula score matches the content reality

### Step 2: Project Depth Assessment (for 招式/悟性/野心)

For users with significant project history, assess the top 3–5 projects:

1. **Identify key projects** from session data (highest message count, longest engagement)
2. **Read project structure** — Cargo.toml, package.json, directory layout
3. **Sample core code** — parser, engine, architecture-critical modules
4. **Assess three axes per project:**
   - **Architecture quality** — correct abstractions, clean boundaries, consistent patterns
   - **Implementation depth** — real complexity vs thin wrappers, hand-written vs glue code
   - **Originality** — init from scratch vs fork, and if fork how deep the modifications go

### Step 3: User Alignment

**Mandatory** when any of these are true:
- Top project has >5000 messages or spans >30 days
- Project contains non-trivial architecture (workspace, monorepo, multi-language, FFI)
- Project domain is ambiguous (can't tell if from-scratch vs fork, research vs product)
- AI cannot confidently assess originality or technical depth from structure alone

**May skip** only when projects are shallow (simple scripts, config repos, single-file tools) and formula scores look reasonable.

Before finalizing any correction scores, present the initial assessment (base scores + what you observed) to the user and ask:
- "Are there modifications or architectural decisions I'm not seeing?"
- "What's the competitive landscape — what existing tools does this compare to?"
- "Which projects were built from scratch vs forked/modified?"

Users often have context AI cannot infer from code alone: rendering engine swaps, competitive positioning, cross-project architectural vision. One round of alignment significantly improves accuracy.

**Do NOT assign correction scores before this step completes.** Present base scores + observations first, get user input, then correct.

### Correction Guidelines

| Dimension | Message samples | Project assessment | User alignment |
|-----------|----------------|-------------------|----------------|
| 内力 | Monthly trend, intensity consistency | — | — |
| 轻功 | Message rhythm, pivot speed | — | — |
| 招式 | Precise file refs, structured reviews | Architecture quality, implementation depth, originality | Fork depth, competitive diff |
| 杀气 | Negation tone (precise vs emotional) | — | — |
| 悟性 | Technical depth in messages | Technical sophistication of code, domain breadth | Learning speed, community novelty |
| 野心 | Scope expansion patterns | Project scale, ecosystem coherence | Vision, product positioning |
| 阅历 | Topic diversity in messages | Tech stack breadth across projects | — |

### Correction Rules

- Each correction must have a one-sentence justification
- **招式 and 悟性**: no correction cap — formula is a known weak proxy for these dimensions, actual project assessment can reveal dramatically different reality
- **Other dimensions**: maximum ±15 from formula base
- If formula and content agree, no correction needed — don't adjust for the sake of adjusting
- Project assessment is most impactful for 招式/悟性/野心; skip for other dimensions unless evidence warrants

## Phase 3.5: Identity Matching

Two-phase matching: formula narrows candidates, AI judges compatibility.

### Phase A: Formula Screening

**Weighted Euclidean distance** to each sect's anchor point (defined in `sects.md`):

```
distance(user, sect) = √(Σ w_i × (user_i - anchor_i)²)

w_i = 2.0  if anchor_i ≠ 50 (defining trait for this sect)
w_i = 0.5  if anchor_i = 50 (irrelevant to this sect)
```

Match score = `max(0, 100 - distance × 0.5)`, normalized to 0–100.

Select top 3–5 candidates with score ≥ 50. If no candidate reaches 50, go directly to Freelancer Track.

### Phase B: AI Compatibility Judgment

For each candidate sect, examine every dimension where |user - anchor| > 15:

1. **Is this deviation contradictory to the sect's identity?**
   - "恒山派 + 杀气 85" → contradictory, 恒山 is defined by gentleness → penalize
   - "逍遥派 + 野心 85" → compatible, 逍遥 founders had ambition, wild心 is not core to逍遥's identity → no penalty
   
2. **Is the user's strength an enhancement of the sect's identity?**
   - "逍遥派 + 内力 96" → enhancement, being stronger than the anchor is a positive → bonus

3. **Adjust match score:**
   - Contradictory deviation: keep or increase the distance penalty
   - Compatible deviation: reduce or remove the distance penalty
   - Enhancement: reduce penalty, optionally boost score by up to +5

**Key principle**: Sect anchors define the center of a personality cluster, not rigid boundaries. A dimension anchored at 50 means "not defining" — deviation in either direction is fine. A dimension anchored at 25 or 75 means "defining" — deviation in the opposite direction needs justification.

### Track Decision

After AI adjustment:
- **Adjusted score ≥ 60** → Sect Track (confident match)
- **Adjusted score 40–60** → AI decides: sect if deviation is compatible, freelancer if contradictory
- **Adjusted score < 40** → Freelancer Track

### Sect Track — Rank Assignment

Identify the matched sect's core dimensions (those with anchor ≠ 50). Use the user's average score on these core dimensions to determine rank:

| Rank | Chinese | Condition |
|------|---------|-----------|
| Disciple | 弟子 | Core dimension avg < 70 |
| Elder | 长老 | Core dimension avg 70–85 |
| Sect Leader | 掌门 | Core dimension avg > 85 |

Output format: `{Sect} · {Rank}` — e.g. "华山剑宗 · 掌门", "逍遥派 · 弟子"

### Freelancer Track — Identity Generation

When no sect matches well after AI judgment, generate a custom jianghu identity.

**Broad categories** (mandatory — all freelancer identities must fit one):
- 侠 — wandering hero, swordsman, lone ranger
- 商 — tavern owner, merchant, trade guild
- 隐 — hermit, fisherman, mountain recluse
- 匠 — swordsmith, mechanism master, alchemist
- 官 — constable, imperial guard, inspector
- 暗 — assassin, spy, shadow operative

**Rules for freelancer identity generation:**
1. Choose a category that fits the user's dimension profile
2. Generate a specific identity title within wuxia/jianghu aesthetic (e.g. "深巷铸剑师", "茶馆说书人", "走镖三十年的老镖头")
3. The title MUST feel like a character from a martial arts world — no modern or generic titles
4. The title should reflect actual behavioral patterns, not be random
5. No two users should get identical titles — incorporate dimensional quirks

### Matching Output

1. Record top 3 sect matches with formula scores + AI-adjusted scores
2. If Sect Track: sect name + rank + adjusted match score + one-sentence AI justification
3. If Freelancer Track: category + custom title + top 3 closest sects for reference

## Phase 4: Profile Generation

### 4.1 Identity Display
- Sect Track: `{Sect} · {Rank}` as main heading
- Freelancer Track: custom title as main heading, category as subtitle

### 4.2 Desensitization

Same rules as seven-sins. The generated card is designed to be shared publicly. **Never include:**
- Specific project names, repo names, product names, company names
- Personal names, usernames, file paths, URLs, domain names
- Specific message content or quotes
- Project domains or categories

Focus on **numbers, ratios, and behavioral descriptions**.

### 4.3 Dimension Copy
- **tagline**: ≤10 char — a wuxia-flavored verdict
- **data**: 1–2 key data points in a short sentence (wrap key numbers in `<strong>`). Follow desensitization rules.

Score < 20 → understated · 20–60 → neutral · > 60 → vivid · > 80 → legendary tone

### 4.4 Deep Dive
Go beyond stats — read actual content:
- Sample user messages for communication style
- Check deep-engagement projects for technical depth (especially for 悟性)
- Look at time distribution for lifestyle patterns
- Check monthly trends for 内力 trajectory

If a score contradicts your content analysis, adjust. **Insight trumps formula.**

### 4.5 Personal Title & Stamp Text

Generate a short personal title (≤6 chars recommended, ≤12 max) that captures the user's most distinctive trait. This is NOT the sect/freelancer identity — it's a personal epithet, like a jianghu nickname.

Examples: "三尺青锋", "不眠侯", "百炼城主", "快刀不解释"

**Stamp column layout**: The title will be rendered as a traditional Chinese seal stamp (印章). Split the title into columns following seal conventions — the stamp reads **right-to-left, top-to-bottom**:

| Chars | Columns | Layout (right→left) | Example |
|-------|---------|---------------------|---------|
| 2 | 1 col | `['AB']` | `['青锋']` |
| 3 | 2 cols (2+1) | `['AB', 'C']` | `['青锋', '客']` |
| 4 | 2 cols (2+2) | `['AB', 'CD']` | `['三尺', '青锋']` |
| 5 | 2 cols (3+2) | `['ABC', 'DE']` | `['百炼城', '主人']` |
| 6 | 2 cols (3+3) or 3 cols (2+2+2) | `['ABC', 'DEF']` | `['快刀不', '解释也']` |

The first array element is the **right column** (read first), the last is the **left column** (read last). Fill `DATA.title` with the full title string, and `DATA.stampText` with the pre-split array.

## Phase 5: Fill Template

Overwrite `templates/jianghu-dev/src/data.ts` with the user's profile data. The file exports a `ProfileData` object — keep the type definitions, replace `DATA` values.

`DATA` structure:
```ts
export const DATA: ProfileData = {
  lang: 'zh',
  track: 'sect',       // 'sect' | 'freelancer'
  sect: '华山剑宗',
  rank: '长老',        // 弟子/长老/掌门 (sect) or custom title (freelancer)
  title: '三尺青锋',
  stampText: ['三尺', '青锋'],
  matchScore: 78,       // 0-100
  summary: '...',       // Wuxia-flavored paragraph. NEVER mention project/repo/company names.
  stats: [
    { value: '玖拾贰', unit: '天' },
    { value: '贰万叁仟', unit: '消息' },
    { value: '肆拾柒', unit: '项目' },
    { value: '贰', unit: '兵器' },
  ],
  dimensions: [
    { key: 'neili',    name: '内力', score: 58, color: '#95302E', tagline: '...', data: '...' },
    { key: 'qinggong', name: '轻功', score: 82, color: '#3D8E86', tagline: '...', data: '...' },
    { key: 'zhaoshi',  name: '招式', score: 91, color: '#19325F', tagline: '...', data: '...' },
    { key: 'shaqi',    name: '杀气', score: 78, color: '#CB523E', tagline: '...', data: '...' },
    { key: 'wuxing',   name: '悟性', score: 52, color: '#615EA8', tagline: '...', data: '...' },
    { key: 'yexin',    name: '野心', score: 45, color: '#D6BC46', tagline: '...', data: '...' },
    { key: 'yueli',    name: '阅历', score: 38, color: '#5D7259', tagline: '...', data: '...' },
  ],
  credit: '画像由 天机阁 Lucida 造册 · {干支年}{季节}',
}
```

### Number Conventions

- **stats value**: 大写中文数字（壹贰叁肆伍陆柒捌玖拾佰仟万），小数四舍五入
- **dimensions data**: data point numbers → 大写中文数字 + `<strong>`; idiomatic/literary numbers (八成, 一脉相承, 从无到有) → keep original, no bold
- **dimensions score**: Arabic numerals (displayed as-is)
- **matchScore**: displayed as `契合 · {大写中文数字}` by the template
- **dimensions color**: fixed per dimension, do not change

### i18n

`DATA.lang` controls language (`'zh'` or `'en'`). Template fixed text auto-switches.

Fill text fields per language:
- `sect` / `rank` / `title` / `summary` — in target language
- `dimensions[].name` — Chinese: `'内力'`, English: `'Inner Power'`
- `dimensions[].tagline` / `dimensions[].data` — in target language
- `stats[].unit` — Chinese: `'天'`, English: `'days'`

## Phase 6: Output

1. Write data to `templates/jianghu-dev/src/data.ts`
2. Start Vite dev server: `cd templates/jianghu-dev && pnpm dev`
3. Open in browser, screenshot the page
4. Terminal summary: identity + 7 scores + one-liner

## Phase 7: Cleanup

Delete all intermediate data produced during profiling:
- `/tmp/lucida-metrics.json` (if saved)
- Any temp files created during extraction or sampling
- Clear metrics variables from context

The final card (data.ts + screenshot) is the only artifact that should persist. Raw behavioral data must not linger.
