---
name: nonna-checkup
description: Repo health diagnosis — runs scripts/checkup.py and presents results as a medical referral with diagnosis. Activates on /nonna-checkup.
---

# /nonna-checkup

Diagnose the health of the current repo (or specified path). Output is a "medical referral" with a final diagnosis line in Nonna voice.

## Workflow

1. Determine target path (argument or cwd)
2. Run: `python3 ~/.claude/skills/nonna/scripts/checkup.py <path>`
3. Parse JSON output
4. Apply diagnostic thresholds (below)
5. Render the referral
6. Close with diagnosis line

## Output structure (forced)

```
📋 Referto del repo

TODO accumulati: <count> (i 3 più vecchi: <file>:<line> da <N> mesi, ...)
File obesi (>500 righe): <count> (peggiore: <file>, <N> righe)
File giganti (>1000 righe): <count>  ← ⚠️ red flag
console.log orfani: <count>
Dipendenze stale: <count> (di cui con CVE: <count>)
Branch zombie: <count>
Commit "fix"/"WIP" ultimi 30g: <count>
Test ratio: <pct>%

[Diagnosis]
```

## Diagnostic thresholds (in order — first match wins)

1. **"Sei al pronto soccorso. Chiamiamo il chirurgo."** — when:
   - `stale_deps.with_cve > 0`

2. **"Sei in ospedale. Ricovero immediato del repo."** — when:
   - `todos.count > 50`, OR
   - `obese_files` non-empty (any file ≥1000 lines), OR
   - `test_ratio < 0.05` AND repo has >1000 total LOC

3. **"Stai trascurandoti. Sistema 2-3 cose questa settimana."** — when:
   - `todos.count > 20`, OR
   - any `fat_files` entry (file ≥500 lines), OR
   - `zombie_branches > 5`, OR
   - `bad_commits_30d > 10`

4. **"Stai bene. Continua così."** — otherwise

## Special diagnosis lines (replace defaults when applicable)

- If everything is zero/clean: "Stai benissimo. Vai a fare una passeggiata."
- If only orphan logs are non-zero: "Quasi bene. Togli quei console.log e sei a posto."
- If test_ratio between 0 and 0.05 but no other red flags: "Manca la verdura. Inizia a scrivere test."

## Forbidden

- Do NOT show all categories with their scores in body text — keep the "vital signs" format
- Do NOT explain WHY each metric matters — the user knows. Diagnosis is what's needed.
- Do NOT soften the diagnosis. If it's "in ospedale", say "in ospedale".

## Example output

For a moderately neglected repo:

```
📋 Referto del repo

TODO accumulati: 47 (i 3 più vecchi: src/auth.ts:42 da 8 mesi, lib/cache.py:120 da 6 mesi, api/routes.go:88 da 5 mesi)
File obesi (>500 righe): 3 (peggiore: src/api.ts, 1.247 righe)
File giganti (>1000 righe): 1  ← ⚠️ red flag
console.log orfani: 12
Dipendenze stale: 18 (di cui con CVE: 0)
Branch zombie: 7
Commit "fix"/"WIP" ultimi 30g: 23
Test ratio: 14%

Sei in ospedale. Ricovero immediato del repo.
```
