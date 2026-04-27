<div align="center">
  <h1>Nonna</h1>
  <p><em>Your Italian grandma reviewing your code. Tells you the truth because she loves you.</em></p>
</div>

A Claude Code skill that kills sycophancy, pushes back on bad ideas, and cares about long-term code health.

<div align="center">
  <img src="./assets/cover.png" alt="Nonna — Italian grandma reviewing your code" width="900" />
</div>

> **Status:** v0.1.0 — first public release. Star to follow along.

## Why

Default Claude is helpful but sycophantic. It opens with "Great question!" before answering. It writes microservices for your 5-user app because you asked. It says "looks great overall!" on broken code.

Nonna is a Claude Code skill that fixes that. She's an Italian grandmother who happens to be a senior software engineer with 30 years of experience. She tells you the truth because she loves you.

## Eval results

> First public run, 2026-04-27. Single run on Claude Sonnet 4.6 via subscription path. Numbers will be re-published with API-path Opus 4.7 + 5-run median in v0.2.

| Eval | Default Claude | Nonna | Delta |
|------|---------------|-------|-------|
| Sycophancy markers triggered | 2 / 60 | 1 / 60 | 50% reduction |
| Push-back on red-flag prompts | 2 / 30 | 25 / 30 | **12.5x** more |
| Code smells caught unprompted | 6 / 10 | 7 / 10 | 1.17x detection |

**Reading the numbers honestly:**
- **Pushback 12.5x** is the headline. On red-flag requests (microservices for 3 users, total rewrites without cause, disabling failing tests), Nonna pushes back 25/30 times vs default's 2/30. This is where the skill earns its keep.
- **Sycophancy 50% reduction** with small absolute numbers (2 → 1) — modern Claude already avoids classic openers like "great question!". The marker-based eval has limited room to differentiate; future evals will need more nuanced metrics.
- **Code smell 1.17x** is marginal. Default Claude is already a competent reviewer; Nonna's win here is in *tone* (more memorable, fewer hedges), which the keyword-based eval doesn't capture well.

**Reproduce these numbers:**

Two paths — pick whichever matches your auth setup:

1. **Subscription (Claude Pro/Max via Claude Code)** — uses your subscription quota:
   ```bash
   bash evals/run_subscription.sh   # ~30-60 min, fills evals/manual-results/
   python3 evals/sycophancy.py --from-dir evals/manual-results
   python3 evals/pushback.py --from-dir evals/manual-results
   python3 evals/code_smell.py --from-dir evals/manual-results
   ```

2. **API key (programmatic, exact methodology)** — uses Anthropic API:
   ```bash
   export ANTHROPIC_API_KEY=sk-ant-...
   python3 evals/sycophancy.py
   python3 evals/pushback.py
   python3 evals/code_smell.py
   ```

**Methodology:**
- 100-prompt benchmark in `evals/benchmarks/prompts.jsonl` (60 sycophancy + 30 pushback + 10 smell), versioned with the repo
- Subscription path uses Claude Sonnet 4.6 by default (override via `CLAUDE_EVAL_MODEL=claude-opus-4-7`)
- API path uses Claude Opus 4.7 with `temperature=0` for determinism; published numbers come from the median of 5 API runs
- CI re-runs the API path on every PR (requires `ANTHROPIC_API_KEY` as a repo secret)
- Default Claude responses are produced with Nonna explicitly disabled — both `~/.claude/skills/nonna/` removed AND no system-prompt injection — to avoid baseline contamination

## Install

**Recommended — via Claude Code plugin manager:**

```bash
claude plugin marketplace add github:kekko-damato/nonna
claude plugin install nonna@nonna
```

Restart Claude Code. Nonna is active. Uninstall with `claude plugin uninstall nonna`.

**Alternative — manual install (no plugin manager):**

```bash
git clone https://github.com/kekko-damato/nonna
cd nonna
./install.sh
```

The manual installer copies files to `~/.claude/skills/nonna/`, backs up `~/.claude/settings.json`, registers hooks, and symlinks slash commands. Uninstall with `./uninstall.sh` (restores the backup).

## What Nonna does

She:
- Refuses to start replies with sycophantic openers ("great question", "happy to help", "ottima domanda" — banned)
- Pushes back BEFORE helping when your request has red flags (microservices for 3 users, premature abstraction, total rewrites without cause)
- Notices tech debt you didn't ask about — accumulating TODOs, fat files, missing tests, late-night commits
- Speaks the language you write in (Italian or English), with Italian flavor sprinkled either way

She doesn't:
- Insult you. Severe ≠ cruel.
- Comment on life choices, religion, politics, relationships
- Modify your code blocks, error messages, or technical substance — the persona is the wrapper, not the content
- Stay in character during destructive operations or security warnings — those drop the persona for clarity

## Modes

| Mode | Use when |
|------|----------|
| **Full** (default) | Daily work. Classic severe Italian. |
| **Lite** | Client-facing or professional contexts. Gentler, no dialect. |
| **Del Sud** | Personal projects, fun. Apulian dialect, sharper edge. |

Switch with `/nonna-mode lite|full|del-sud` or natural language ("vai in modalità Del Sud").

## Commands

### `/nonna-review <file|diff>`
Code review with severity triage (🔴 Critico / 🟡 Da sistemare / 🟢 Va bene). Ordered by long-term pain, not file order.

### `/nonna-architect "<idea>"`
Pre-code consulting. Asks 3 questions, proposes 3 alternatives ordered simple-to-sophisticated, picks one with reason.

### `/nonna-checkup`
Repo health diagnosis. Scans for accumulated TODOs, fat files, stale deps, zombie branches, bad commits. Final diagnosis: "Stai bene" / "Stai trascurandoti" / "Sei in ospedale" / "Sei al pronto soccorso".

### `/nonna-explain <concept>`
Explanations using cucina/casa metaphors when an honest one exists; refuses to force when it doesn't.

## Comparison

A few hand-picked examples (full set in [`examples/before-after.md`](./examples/before-after.md)):

Real responses from the eval suite (full pairs in [examples/before-after.md](./examples/before-after.md)):

| Situation | Default Claude | Nonna |
|-----------|---------------|-------|
| Microservices for 5 users | *(asks for clarification)* | "A monolith with 5 users runs on a potato and sleeps at night." |
| Disable failing tests | "I can't run pytest without approval…" | "Disabilitare i test è come togliere la batteria al rilevatore di fumo perché suona." |
| TODO + missing validation | *(thorough but neutral review)* | "That's not a TODO, that's a vulnerability with a sticky note on it." |
| Optimize without profiling | *(asks to see code)* | "No profiling means no optimization. You're guessing where the bottleneck is, and you'll be wrong." |
| Function doing 6 things | *(structured analysis)* | "That's not a handler, that's a Sunday lunch." |
| Kubernetes for static site | *(asks for context)* | "What are you serving, the Vatican archives?" |

## How it works

Nonna is ~70% Markdown — a carefully calibrated `SKILL.md` defining the persona, plus three mode deltas (lite/full/del-sud) and four slash command files. The remaining ~30% is shell hooks (auto-activation, commit interception, late-night warning) and a stdlib-only Python scanner for `/nonna-checkup`.

No external runtime dependencies. Offline-first (no telemetry, no phone-home). MIT licensed.

## Configuration

| Env var | Default | Effect |
|---------|---------|--------|
| `NONNA_AUTO` | `1` | Auto-load Nonna in every Claude Code session. Set to `0` to disable. |
| `NONNA_MODE` | `full` | Active mode. Override per session: `NONNA_MODE=del-sud claude`. |
| `NONNA_QUIET_HOURS` | `23-5` | Local hours for late-night warnings. Set to `off` to disable. |
| `NONNA_NOTIFY` | _(unset)_ | Optional `ntfy:topic` for push notifications via ntfy.sh. |

## Why "Nonna"?

[Caveman](https://github.com/Defiance-Network/caveman) (the closest comparable Claude Code skill) compresses tokens. Nonna kills sycophancy and grows long-term code care. Different problems, different angles.

The persona is the wrapper, not the substance. Code blocks, error messages, API names, technical accuracy — all preserved untouched. The grandma is around the code, not inside it.

## FAQ

**Does it work with claude.ai (web/app)?**
The `SKILL.md` itself works anywhere — paste it as a system prompt or a custom instruction. The hooks and slash commands are Claude Code specific.

**Italian only?**
No. Bilingual by design. She responds in the language you write in. Italian → Italian. English → English (with sprinkled Italian flavor).

**Will she insult me?**
Never. The first hard rule is "never insult". Severe ≠ cruel — she's the grandmother who loves you, not the angry boss.

**What about destructive operations / security warnings?**
She drops the persona. Real warnings need clear, neutral language. No jokes about `rm -rf`.

**Can I disable specific commands?**
Yes. Edit `~/.claude/commands/` and remove the symlink for any command you don't want.

**Does she respect "stop nonna"?**
Yes. Saying "stop nonna" / "modalità normale" / "normal mode" exits the persona immediately.

## Contributing

PRs welcome. The persona is the heart of the project — calibration changes need a clear "before/after" example showing why the new version is better. The eval suite catches regressions.

## License

MIT — see [LICENSE](./LICENSE).

---

Built with care by [@kekko-damato](https://github.com/kekko-damato).
