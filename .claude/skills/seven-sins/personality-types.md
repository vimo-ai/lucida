# 32 Personality Archetypes

Reference data for Seven Deadly Sins profiling. Each archetype is defined by its dimension signature — the matching algorithm uses the anchor table in SKILL.md.

## Dimension Definitions

| Dimension | Measures | High | Low |
|-----------|----------|------|-----|
| Sloth | Effort minimization | Ultra-short messages, delegation words, extreme output/input ratio | Detailed messages, self-described problems |
| Pride | Self-centeredness | No context, no background, no references | Rich context, cites external sources |
| Greed | Demand maximization | Wants everything at once, scope creep, feature stacking | One question at a time, restrained scope |
| Wrath | Negation & interruption | High negation rate, frequent interrupts, "not this" | Accepts output, patient iteration |
| Gluttony | Consumption volume | Marathon sessions, extreme turn count | Short sessions, use-and-leave |
| Lust | Novelty & jumping | Frequent topic switching, scattered interests | Focused on single domain |
| Envy | External reference | Heavy citation of external sources, competitors, others' solutions | Self-sufficient, no external reference |

## Part 1: Known Paradigms (#1–20)

### #1 Hands-Off Boss (甩手掌柜)

**Dimensions**: Sloth↑ Pride↑ Greed↑ Wrath↓

Accept All without reading diffs. Pastes errors without explaining intent, never reviews output. "You handle it" then waits for results.

**Behavioral indicators**:
- Extreme output/input ratio
- Very low negation rate
- High % of messages starting with "help me" / "just do"
- Almost no code review follow-ups

---

### #2 Ornament (挂件)

**Dimensions**: Sloth↑ Pride↑ Greed↓ Wrath↓

Pure error-paste + "fix this." No context, no intent, no project background. One error per session.

**Behavioral indicators**:
- Extremely high % of messages containing stack traces / error logs
- Bimodal message length (pasted content long, own words ultra-short)
- Low session turn count
- Almost no follow-ups

---

### #3 Class Monitor (学习委员)

**Dimensions**: Sloth↓ Pride↓ Greed↑ Wrath↑ Gluttony↑

Writes detailed specs, splits into subtasks, commits per step, uses linter/CI as quality gates. Treats AI as a supervised executor — rejects substandard output.

**Behavioral indicators**:
- High average user message length
- High % of structured content (lists, code blocks, file paths)
- Negation messages include specific revision requests
- Long but orderly sessions

---

### #4 Contractor (包工头)

**Dimensions**: Sloth↑ Pride↑ Greed↑ Wrath↓ Gluttony↑

Gives AI a goal, lets it plan, read code, write code, run tests, iterate autonomously. User intervention is mostly approve/continue.

**Behavioral indicators**:
- One long message at session start (goal), then very few user messages
- AI messages far outnumber user messages
- High % of tool_use messages
- User input is mainly approval

---

### #5 Flamer (喷子)

**Dimensions**: Sloth↓ Pride↑ Greed↑ Wrath↑↑

Violently rejects everything. Frequent interrupts, high negation rate, emotional outbursts.

**Behavioral indicators**:
- Extremely high negation word frequency
- High % of messages with exclamation/question marks
- Sessions may terminate abruptly
- Very few positive confirmations

---

### #6 Rubber Duck (小黄鸭)

**Dimensions**: Sloth↓ Pride↓ Greed↓ Wrath↓ Gluttony↓

Doesn't need AI's answer. Figures things out by describing the problem to AI. Low dependency.

**Behavioral indicators**:
- User message length > AI message length
- User arrives at conclusions themselves
- Short sessions
- Low dependency (doesn't probe AI's solutions)

---

### #7 Strategist (狗头军师)

**Dimensions**: Sloth↓ Pride↓ Greed↑ Gluttony↑ Lust↑

Wants ideas not code. Brainstorming back and forth. Content is words not code.

**Behavioral indicators**:
- Low code block ratio
- Ping-pong pattern (user and AI message lengths similar)
- High topic diversity
- Sessions may span long periods

---

### #8 Socrates (苏格拉底)

**Dimensions**: Sloth↓ Pride↓ Wrath↓ Gluttony↑ Lust↑ Envy↑

Recursive deep discussion, chases process not conclusions. Heavy external references, shuttles between multiple perspectives.

**Behavioral indicators**:
- Extremely long sessions
- User messages are mostly questions ("why" / "what if" / "but")
- AI messages also very long
- Almost no imperative messages

---

### #9 Contrarian (杠精)

**Dimensions**: Pride↑ Wrath↑ Gluttony↑

Makes AI argue against itself, or never trusts AI output. Adversarial usage as a whetstone.

**Behavioral indicators**:
- High frequency of "but" / "are you sure" / "any counterexamples"
- High negation rate but without emotion (differs from Flamer)
- Frequently asks AI to self-correct
- Sessions tend long

---

### #10 Curious Cat (好奇宝宝)

**Dimensions**: Sloth↓ Pride↓ Wrath↓ Gluttony↑ Envy↑

Goal is understanding, not output. Asks questions, seeks explanations. References external sources for cross-validation.

**Behavioral indicators**:
- High frequency of "why" / "how does" / "can you explain"
- Short user messages (questions), long AI messages (answers)
- Higher % of external links/docs
- Very few imperative messages

---

### #11 Player (海王)

**Dimensions**: Wrath↑ Lust↑ Envy↑↑

Not loyal to one model, switches by task. Focuses on divergence points between models. Frequently compares other models' performance.

**Behavioral indicators**:
- High frequency of other AI names (ChatGPT/Gemini/Copilot)
- May paste other models' outputs
- Negation accompanied by comparison ("XX can do this")
- Short sessions (specific comparisons)

---

### #12 Cyber Devotee (赛博孝子)

**Dimensions**: Sloth↓ Pride↓ Greed↓ Wrath↓ Gluttony↑

Treats AI as 24/7 listener, anthropomorphizes AI (says thanks, please, sorry). Relationship over efficiency.

**Behavioral indicators**:
- Extremely high politeness word frequency
- High % of non-task messages
- Rich emotional vocabulary
- Very low negation rate

---

### #13 Day Trader (散户)

**Dimensions**: Sloth↑ Pride↑ Gluttony↓ Lust↑

Ask one question, get answer, close. Search engine replacement. Diverse topics but 1-2 turns per session.

**Behavioral indicators**:
- Very few turns per session (1-3)
- Independent topic per session
- No follow-ups
- Many sessions, each very short

---

### #14 Inspector (质检员)

**Dimensions**: Pride↓ Wrath↓ Envy↑

Submits own work for AI evaluation. Not creation, verification. "Check this for me."

**Behavioral indicators**:
- User messages start with large code/text blocks
- Accompanied by "review this" / "any issues" / "translate to"
- AI output is critique/correction, not new creation
- Short sessions

---

### #15 Dungeon Dweller (地缚灵)

**Dimensions**: Greed↑ Gluttony↑↑ Lust↓

Ultra-long sessions — world building, interactive narrative, or just someone who never starts a new session. Session time and turns far exceed mean.

**Behavioral indicators**:
- Session turns in top 1%
- Sessions may span multiple days
- Strong context continuity (no topic jumping)
- May actively manage context ("remember what we said about X")

---

### #16 Lab Rat (科研狗)

**Dimensions**: Pride↓ Greed↑ Gluttony↑ Envy↑

Uses large context window for long documents, datasets, literature. Upload → summarize → analyze → extract. Heavy external references.

**Behavioral indicators**:
- User messages contain large pasted content
- High frequency of file upload commands
- "Summarize" / "analyze" / "extract" / "compare" high frequency
- Long sessions

---

### #17 Deadline Fighter (DDL战士)

**Dimensions**: Greed↑ Wrath↑ Gluttony↑

Plans first, executes after approval. Intermittent heavy user — dormant normally, 72-hour sprint during project crunch.

**Behavioral indicators**:
- Clear "planning phase" and "execution phase" in sessions
- High message density during planning
- May show consecutive days of intense sessions
- Extreme variance in usage frequency

---

### #18 Hardhead (铁头娃)

**Dimensions**: Wrath↑ Gluttony↑ Lust↓

Debugs the same issue repeatedly without giving up. Won't change direction or topic — must fix this bug.

**Behavioral indicators**:
- Highly concentrated topic within session
- Same error/file referenced repeatedly
- Medium negation rate ("still wrong" not "you're wrong")
- Long sessions but single topic

---

### #19 Perfectionist (完美主义者)

**Dimensions**: Sloth↓ Pride↑ Wrath↑ Gluttony↑ Lust↓

Polishes the same thing endlessly. Not bugs — "it could be better."

**Behavioral indicators**:
- High frequency of "tweak this" / "not enough" / "can it be more..."
- Same code/text modified multiple times
- Long sessions but only one "final version"
- High negation rate but calm tone (differs from Flamer)

---

### #20 Drill Sergeant (教官)

**Dimensions**: Sloth↑ Pride↑

IDE inline assist. AI does autocomplete and local edits. Zero emotional investment, pure efficiency. User in driver's seat.

**Behavioral indicators**:
- Short, imperative messages
- High code context ratio
- Stable session rhythm
- Zero non-technical conversation

---

## Part 2: White Space Discovery (#21–32)

### #21 Ancestor (祖宗)

**Dimensions**: Sloth↑ Wrath↑ Pride↑ Gluttony↓

Types 3 words → wrong → another 3 words → still wrong → "can you even do this?" Ultra-short messages, instant negation, never explains what they actually want.

**Behavioral indicators**:
- Ultra-short messages + high negation frequency co-occurring
- Short sessions (gives up or explodes quickly)
- Almost no explanatory messages
- "Redo" / "forget it" / "not this" in loops

---

### #22 Hidden Master (扫地僧)

**Dimensions**: Sloth↑ Pride↓

Ultra-short messages but extreme information density. One sentence pinpoints file + line + problem. Few words not from laziness but from precision.

**Behavioral indicators**:
- Low message length but high density of file paths, line numbers, technical terms
- AI usually understands on first try (low follow-up rate)
- Low negation rate (precise instructions → AI gets it right)
- Short input but token information density far above average

---

### #23 Pit Digger (坑王)

**Dimensions**: Greed↑ Lust↑

Wants a lot and keeps changing direction. Starts with login page, drifts to OAuth, then dashboard.

**Behavioral indicators**:
- High topic switch count within session
- High demand messages per topic
- Frequent directional pivots ("actually" / "how about" / "let's try")
- Long sessions with no convergence

---

### #24 Hater (黑粉)

**Dimensions**: Wrath↑ Envy↑

Always comparing with other tools. "ChatGPT can do this" / "Cursor handles this well" / "other AIs can..."

**Behavioral indicators**:
- High frequency of other AI/tool names
- Negation accompanied by external comparison
- May paste other tools' screenshots or output
- Emotional + comparative co-occurring

---

### #25 Scholar (研究僧)

**Dimensions**: Gluttony↑ Envy↑ Pride↓ Wrath↓

Ultra-long sessions, heavy paper/doc/external code references. Deep research in one domain, drilling down on details.

**Behavioral indicators**:
- Extremely long session + extremely high external references co-occurring
- User messages contain academic/technical literature
- Questions drill deeper (not jumping, but descending)
- High topic concentration

---

### #26 Trend Spotter (种草机)

**Dimensions**: Sloth↑ Envy↑ Pride↓

Drops links/screenshots instead of writing requirements. "Build this" / "reference this repo" / "like that Notion feature."

**Behavioral indicators**:
- Extremely high URL ratio in messages
- Very little self-written text
- High frequency of "like" / "reference" / "similar to" / "this one"
- Requirements almost entirely via external references

---

### #27 Emperor Jiajing (嘉靖)

**Dimensions**: Pride↑ Gluttony↑ Wrath↓ Envy↓

Never explains why, but goes 300 turns in a session. AI keeps guessing intent, user keeps moving forward.

**Behavioral indicators**:
- Session turns top 5% + user message length bottom 20% co-occurring
- Almost no background/context messages
- AI frequently needs to ask for clarification
- Conversation like a road with no map

---

### #28 Guerrilla (游击队长)

**Dimensions**: Sloth↑ Lust↑ Gluttony↓

Rapid-fire unrelated one-line questions. Python → React → K8s, one sentence each.

**Behavioral indicators**:
- Many sessions, each extremely short
- Extremely high topic diversity across sessions
- Only 1-2 turns per session
- Short messages, all independent questions

---

### #29 Giant Baby (巨婴)

**Dimensions**: Wrath↑ Lust↑

Tries one approach → dissatisfied → switches direction → still dissatisfied → switches again. Not fixing the same thing — constantly changing lanes.

**Behavioral indicators**:
- High negation + high topic switching co-occurring
- Negation followed by direction change, not modification
- Multiple completely different technical approaches in one session
- May never converge

---

### #30 Frankenstein (缝合怪)

**Dimensions**: Greed↑ Envy↑ Pride↓

Heavy competitor/open-source references, but not learning — wants "like XX but better."

**Behavioral indicators**:
- High external references + high demand co-occurring
- High frequency of "like" / "similar" / "but add" / "better than"
- Competitor names appear repeatedly
- Requirements = competitor features + differentiation

---

### #31 Riddler (谜语人)

**Dimensions**: Pride↑ Lust↑ Gluttony↓ Envy↓

No background, topics jump wildly. AI has no idea what project this person is working on.

**Behavioral indicators**:
- High topic switch frequency + low context information co-occurring
- Almost no transitions between messages
- AI frequently asks "what's the use case"
- Short sessions but many topics

---

### #32 OCD (强迫症)

**Dimensions**: Sloth↑ Pride↓ Wrath↑

Precise instructions but zero tolerance. Tells you exactly what to do; deviates once and explodes.

**Behavioral indicators**:
- Short messages but extremely precise technical instructions
- Negation caused by AI not following instructions exactly
- User rarely explains "why X," just says "use X"
- Zero tolerance: one deviation triggers outburst
