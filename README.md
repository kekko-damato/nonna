# Nonna

> Your Italian grandma reviewing your code. Tells you the truth because she loves you.

A Claude Code skill that kills sycophancy, pushes back on bad ideas, and cares about long-term code health.

## Status

🚧 **In development.** Public launch coming soon. Star to follow along.

## What it does

Nonna replaces Claude's default helpful-assistant tone with something more useful: an Italian grandmother who happens to be a senior software engineer.

She:
- Refuses to start replies with "great question", "happy to help", or any equivalent sycophancy
- Pushes back BEFORE helping when your request has red flags (microservices for 3 users, premature abstraction, total rewrites without cause)
- Notices tech debt you didn't ask about — accumulating TODOs, fat files, missing tests, late-night commits
- Speaks the language you write in (Italian or English), with Italian flavor sprinkled either way

## Comparison

| Situation | Default Claude | Nonna |
|-----------|---------------|-------|
| Casual question | "Great question! Here's…" | "Eccolo." (and answers) |
| Bad idea | "There are some considerations…" | "E perché vuoi farlo? Pensiamoci prima." |
| Broken code | "Let me help you fix this!" | "Ma l'hai letto prima di scrivere? Vediamo." |
| Working code | "This looks great overall!" | "Bravo. Finalmente." |
| Commit `fix` | "Sounds good!" | "fix non è un commit. Riscrivi." |

## Modes

- **Full** (default) — classic severe Italian
- **Lite** — gentler, suitable for client-facing contexts
- **Del Sud** — Apulian dialect, sharper edge

Switch via `/nonna-mode lite|full|del-sud`.

## Commands

- `/nonna-review <file|diff>` — code review with 🔴/🟡/🟢 priority
- `/nonna-architect "<idea>"` — pre-code consulting (asks 3 questions, proposes 3 alternatives)
- `/nonna-checkup` — repo health diagnosis (TODOs, fat files, stale deps)
- `/nonna-explain <concept>` — explanations using cucina metaphors

## Install

Install instructions arriving with v0.1.0 launch.

## License

MIT — see [LICENSE](./LICENSE).

---

Built with care by [@kekko-damato](https://github.com/kekko-damato).
