---
name: seven-sins
description: Seven Deadly Sins personality profiling. Analyzes your AI conversation history, scores 7 behavioral dimensions, matches to 32 archetypes, and renders a shareable HTML card. Shared data pipeline in shared/data-extraction.md.
---

## Overview

Profile users across 7 sin dimensions (0–100), match to one of 32 personality archetypes, generate a shareable HTML report.

**Prerequisites**: Run the shared data extraction pipeline first — see `shared/data-extraction.md` (Phase 1–2).

**Output**: `output/{user}-seven-sins.html`

## Phase 3: Scoring — Metrics → Sin Dimensions

Map extracted behavioral metrics to 7 sin dimensions. Each sin draws from multiple metric categories — different users hit different angles, and that's fine.

### Dimension Mapping

**Sloth (懒惰) — Minimizing effort**
- Message characteristics: short message ratio, top frequent messages, delegation keywords
- Communication style: input-output ratio (high = low effort)
- Message characteristics: paste ratio (copy-paste vs describing)

**Pride (傲慢) — Self-centered**
- Communication style: context-less ratio, negation/correction, solution-driven ratio, imperative ratio, self-built tendency

**Lust (色欲) — Technical diversity**
- Diversity: project count, project switching, language diversity, topic diversity, tech stack drift, tool diversity

**Gluttony (暴食) — Consumption intensity**
- Activity patterns: daily message volume, session density, marathon ratio, longest session, late night ratio, monthly growth

**Greed (贪婪) — Scope inflation**
- Scope & ambition: rewrite impulse, scope words, additive demands, multi-demand messages, high-intensity days
- Message characteristics: long message density

**Envy (嫉妒) — External reference**
- External references: source reading, clone/fork, URL references, competitor comparison, reference projects, learning intent

**Wrath (暴怒) — Control & correction**
- Control & frustration: interrupts, emotion words, redo words, consecutive negations, short-lived sessions, repeated questions

### Scoring Approach

Pick the strongest angles per sin, weighted combination. The formula is a starting point, not a hard rule — if a score doesn't match your content analysis intuition, adjust it. **Scoring serves profiling, not the other way around.**

Reference baselines (typical AI user):
- Avg message length: 50–100 chars
- Short message ratio: 20–40%
- Daily messages: 50–200
- Project count: 5–20
- Interrupt rate: < 0.5%
- Input-output ratio: 1:3 to 1:10

## Phase 3.5: Personality Type Matching

Match the 7 sin scores to the closest of 32 personality archetypes.

### Dimension Encoding

| Marker | Score | Meaning |
|--------|-------|---------|
| ↑↑ | 90 | Very high (core trait) |
| ↑ | 75 | High |
| (unmarked) | 50 | Neutral |
| ↓ | 25 | Low |
| ↓↓ | 10 | Very low |

### 32 Archetype Anchor Table

| # | Title | Sloth | Pride | Greed | Wrath | Gluttony | Lust | Envy |
|---|-------|-------|-------|-------|-------|----------|------|------|
| 1 | 甩手掌柜 | 75 | 75 | 75 | 25 | 50 | 50 | 50 |
| 2 | 挂件 | 75 | 75 | 25 | 25 | 50 | 50 | 50 |
| 3 | 学习委员 | 25 | 25 | 75 | 75 | 75 | 50 | 50 |
| 4 | 包工头 | 75 | 75 | 75 | 25 | 75 | 50 | 50 |
| 5 | 喷子 | 25 | 75 | 75 | 90 | 50 | 50 | 50 |
| 6 | 小黄鸭 | 25 | 25 | 25 | 25 | 25 | 50 | 50 |
| 7 | 狗头军师 | 25 | 25 | 75 | 50 | 75 | 75 | 50 |
| 8 | 苏格拉底 | 25 | 25 | 50 | 25 | 75 | 75 | 75 |
| 9 | 杠精 | 50 | 75 | 50 | 75 | 75 | 50 | 50 |
| 10 | 好奇宝宝 | 25 | 25 | 50 | 25 | 75 | 50 | 75 |
| 11 | 海王 | 50 | 50 | 50 | 75 | 50 | 75 | 90 |
| 12 | 赛博孝子 | 25 | 25 | 25 | 25 | 75 | 50 | 50 |
| 13 | 散户 | 75 | 75 | 50 | 50 | 25 | 75 | 50 |
| 14 | 质检员 | 50 | 25 | 50 | 25 | 50 | 50 | 75 |
| 15 | 地缚灵 | 50 | 50 | 75 | 50 | 90 | 25 | 50 |
| 16 | 科研狗 | 50 | 25 | 75 | 50 | 75 | 50 | 75 |
| 17 | DDL战士 | 50 | 50 | 75 | 75 | 75 | 50 | 50 |
| 18 | 铁头娃 | 50 | 50 | 50 | 75 | 75 | 25 | 50 |
| 19 | 完美主义者 | 25 | 75 | 50 | 75 | 75 | 25 | 50 |
| 20 | 教官 | 75 | 75 | 50 | 50 | 50 | 50 | 50 |
| 21 | 祖宗 | 75 | 75 | 50 | 75 | 25 | 50 | 50 |
| 22 | 扫地僧 | 75 | 25 | 50 | 50 | 50 | 50 | 50 |
| 23 | 坑王 | 50 | 50 | 75 | 50 | 50 | 75 | 50 |
| 24 | 黑粉 | 50 | 50 | 50 | 75 | 50 | 50 | 75 |
| 25 | 研究僧 | 50 | 25 | 50 | 25 | 75 | 50 | 75 |
| 26 | 种草机 | 75 | 25 | 50 | 50 | 50 | 50 | 75 |
| 27 | 嘉靖 | 50 | 75 | 50 | 25 | 75 | 50 | 25 |
| 28 | 游击队长 | 75 | 50 | 50 | 50 | 25 | 75 | 50 |
| 29 | 巨婴 | 50 | 50 | 50 | 75 | 50 | 75 | 50 |
| 30 | 缝合怪 | 50 | 25 | 75 | 50 | 50 | 50 | 75 |
| 31 | 谜语人 | 50 | 75 | 50 | 50 | 25 | 75 | 25 |
| 32 | 强迫症 | 75 | 25 | 50 | 75 | 50 | 50 | 50 |

### Matching Algorithm

**Weighted Euclidean distance**: dimensions explicitly marked in the type definition (≠50) get weight **2.0**; neutral dimensions (=50) get weight **0.5**. Key dimensions dominate; irrelevant ones don't interfere.

```
distance(user, type) = √(Σ w_i × (user_i - anchor_i)²)

w_i = 2.0  if anchor_i ≠ 50 (defining trait)
w_i = 0.5  if anchor_i = 50 (irrelevant to this type)
```

### Matching Output

1. Closest type = **primary archetype**
2. Record top 3 matches
3. Match score = `max(0, 100 - distance × 0.5)`, normalized to 0–100
4. If top 1 score < 40, label as "hybrid" and list top 3

## Phase 4: Profile Generation

### 4.1 Personality Type
Use the matched archetype title as the main heading. The 32 types are the identity labels — don't generate custom titles.

### 4.2 Desensitization

The generated card is designed to be shared publicly. **Never include any of the following in tagline, data, or summary fields:**
- Specific project names, repo names, or product names
- Company names, organization names, or team names
- Personal names, usernames, or identifiable handles
- File paths, URLs, or domain names
- Specific message content or quotes

**Do not reveal project domains or categories either** — describe purely from the behavioral pattern angle:
- ✗ listing project names → ✓ "341 projects, switching 8.2 per day on average"
- ✗ naming specific tools user built → ✓ "76% imperative messages without a single question mark"
- ✗ describing project categories → ✓ "new hole dug before the last one is filled"

Focus on **numbers, ratios, and behavioral descriptions** — never on what the user was working on.

### 4.3 Sin Copy
- **tagline**: ≤10 char verdict/maxim
- **data**: 1–2 key data points in a short sentence (wrap key numbers in `<strong>`). Follow desensitization rules above.

Score < 20 → understated · 20–60 → neutral · > 60 → punchy · > 80 → roast mode

### 4.4 Deep Dive
Go beyond stats — read actual content:
- Sample user messages for writing style
- Look at project names for interest domains (but don't expose them in output)
- Check time distribution for lifestyle patterns

If a score contradicts your content analysis, adjust. **Insight trumps formula.**

## Phase 5: Fill Template

Template: `templates/seven-sins.html`

The template is data-driven — modify only the `DATA` object at the top of the `<script>` tag. Template JS auto-renders the DOM and radar chart.

`DATA` structure:
```js
const DATA = {
  lang: 'zh', // 'zh' | 'en'
  personality: 'archetype title (one of 32)',
  personalityMatch: 78, // 0-100
  archetype: '', // leave empty, personality is the main title
  summary: '3-5 sentences. Cover all 7 dimensions. Style: sharp but insightful, like a friend roasting you with precision. Don\'t list dimensions — show causality: which sins cause which, which are means vs ends. Weave in the archetype naturally. NEVER mention specific project/repo/company names — use anonymized descriptions.',
  stats: [
    { value: '178', unit: 'days' },
    { value: '528K', unit: 'msgs' },
    { value: '528', unit: 'projects' },
    { value: '12', unit: 'langs' },
  ],
  sins: [
    { key: 'sloth',    name: '懒惰', score: 98, color: '#7b9db5', tagline: '...', data: '...' },
    { key: 'pride',    name: '傲慢', score: 95, color: '#b5707e', tagline: '...', data: '...' },
    { key: 'lust',     name: '色欲', score: 82, color: '#c49a5c', tagline: '...', data: '...' },
    { key: 'gluttony', name: '暴食', score: 78, color: '#6b9b7a', tagline: '...', data: '...' },
    { key: 'greed',    name: '贪婪', score: 78, color: '#b5a04a', tagline: '...', data: '...' },
    { key: 'envy',     name: '嫉妒', score: 60, color: '#5c8f8a', tagline: '...', data: '...' },
    { key: 'wrath',    name: '暴怒', score: 55, color: '#a8614e', tagline: '...', data: '...' },
  ],
  credit: 'Generated by Lucida × Claude · 2026-04-22',
};
```

**key and color are fixed** — only fill in score, tagline, data.

### i18n

`DATA.lang` controls language (`'zh'` or `'en'`). Template fixed text auto-switches.

Fill text fields per language:
- `personality` / `summary` — in target language
- `sins[].name` — Chinese: `'傲慢'`, English: `'Pride'`
- `sins[].tagline` / `sins[].data` — in target language
- `stats[].unit` — Chinese: `'天'`, English: `'days'`

## Phase 6: Output

1. Copy template to `output/{user}-seven-sins.html`, modify the DATA object
2. `open` in browser
3. Terminal summary: archetype + 7 scores + one-liner
