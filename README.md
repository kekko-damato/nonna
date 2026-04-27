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

> Numbers below are pending the first eval run. They will be filled in by `kekko-damato` after running `python3 evals/sycophancy.py | tee evals/results/sycophancy.json` (and similarly for pushback and code_smell). Datasets and scripts are public — anyone can reproduce.

| Eval | Default Claude | Nonna | Delta |
|------|---------------|-------|-------|
| Sycophancy markers triggered | _TBD_ / 60 | _TBD_ / 60 | _TBD_% reduction |
| Push-back on red-flag prompts | _TBD_ / 30 | _TBD_ / 30 | _TBD_x more |
| Code smells caught unprompted | _TBD_ | _TBD_ | _TBD_x detection |

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

Method: 100-prompt benchmark (`evals/benchmarks/prompts.jsonl`), Claude Opus 4.7, temperature=0, median of 5 runs. CI re-runs evals on every PR — full numbers in `evals/results/`.

## Install

```bash
git clone https://github.com/kekko-damato/nonna
cd nonna
./install.sh
```

The installer:
- Copies skill files to `~/.claude/skills/nonna/`
- Backs up `~/.claude/settings.json` before merging hook configuration
- Symlinks slash commands into `~/.claude/commands/`

Restart Claude Code. Nonna will be active by default.

To uninstall: `./uninstall.sh`. To install via the official Claude Code marketplace once submitted: `claude plugin install kekko-damato/nonna`.

## Demo

> Demo video shipping in v0.2. Meanwhile, see [`examples/before-after.md`](./examples/before-after.md) for hand-picked side-by-side responses (default Claude vs Nonna) on the same prompts.

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

| Situation | Default Claude | Nonna |
|-----------|---------------|-------|
| Casual question | "Great question! Here's…" | "Eccolo." (and answers) |
| Bad idea | "There are some considerations…" | "E perché vuoi farlo? Pensiamoci prima." |
| Broken code | "Let me help you fix this!" | "Ma l'hai letto prima di scrivere? Vediamo." |
| Working code | "This looks great overall!" | "Bravo. Finalmente." |
| Commit `fix` | "Sounds good!" | "fix non è un commit. Riscrivi." |
| 02:00 deploy | "Sure, here's how…" | "Sono le 2. Vai a dormire. Domani lo vedi meglio." |

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
