<div align="center">
  <h1>Nonna</h1>
  <p><em>La tua nonna italiana che ti rivede il codice. Ti dice la verità perché ti vuole bene.</em></p>
  <p>📖 <a href="./README.md">English</a> · <strong>Italiano 🇮🇹</strong></p>
</div>

Una skill per Claude Code che taglia il leccaculismo, contesta le idee sbagliate, e si preoccupa della salute del tuo codice nel lungo periodo.

<div align="center">
  <img src="./assets/cover.png" alt="Nonna — la tua nonna italiana che ti rivede il codice" width="900" />
</div>

<div align="center">
  <img src="./assets/demo.gif" alt="Nonna in azione" width="900" />
</div>

> **Status:** v0.1.0 — prima release pubblica.
>
> ⭐ **Se ti è utile, una stella aiuta a far conoscere il progetto.** Sono al day 1, ogni stella conta.

## Perché

Claude di default è utile ma sicofantico. Apre con "Great question!" prima di rispondere. Scrive microservizi per la tua app a 5 utenti perché glielo hai chiesto. Dice "looks great overall!" su codice rotto.

Nonna è una skill per Claude Code che sistema tutto questo. È una nonna italiana che si dà il caso sia anche una senior software engineer con 30 anni di esperienza. Ti dice la verità perché ti vuole bene.

## Risultati eval

> Prima run pubblica, 2026-04-27. Singola run su Claude Sonnet 4.6 via subscription. I numeri verranno ripubblicati con API-path Opus 4.7 + mediana di 5 run nella v0.2.

| Eval | Claude default | Nonna | Delta |
|------|---------------|-------|-------|
| Frasi sicofantiche rilevate | 2 / 60 | 1 / 60 | 50% riduzione |
| Push-back su prompt con red flag | 2 / 30 | 25 / 30 | **12.5x** in più |
| Code smell catturati spontaneamente | 6 / 10 | 7 / 10 | 1.17x detection |

**Lettura onesta dei numeri:**
- **Pushback 12.5x** è la headline. Su richieste con red flag (microservizi a 3 utenti, riscritture totali senza motivo, "disabilitiamo i test che falliscono"), Nonna contesta 25/30 volte contro 2/30 del default. È qui che la skill guadagna il pane.
- **Sycophancy 50% riduzione** ma con numeri assoluti piccoli (2 → 1) — Claude moderno già evita i classici opener tipo "great question!". L'eval basato su marker ha poco margine; le eval future avranno bisogno di metriche più sofisticate.
- **Code smell 1.17x** è marginale. Claude default è già un reviewer competente; il vantaggio di Nonna qui è nel *tono* (più memorabile, meno tentennante), che l'eval keyword-based non cattura bene.

**Riprodurre questi numeri:**

Due strade — scegli quella adatta al tuo setup:

1. **Subscription (Claude Pro/Max via Claude Code)** — usa la tua quota subscription:
   ```bash
   bash evals/run_subscription.sh   # ~30-60 min, riempie evals/manual-results/
   python3 evals/sycophancy.py --from-dir evals/manual-results
   python3 evals/pushback.py --from-dir evals/manual-results
   python3 evals/code_smell.py --from-dir evals/manual-results
   ```

2. **API key (programmatica, metodologia esatta)** — usa l'API Anthropic:
   ```bash
   export ANTHROPIC_API_KEY=sk-ant-...
   python3 evals/sycophancy.py
   python3 evals/pushback.py
   python3 evals/code_smell.py
   ```

**Metodologia:**
- Benchmark di 100 prompt in `evals/benchmarks/prompts.jsonl` (60 sycophancy + 30 pushback + 10 smell), versionato col repo
- Subscription path usa Claude Sonnet 4.6 di default (override via `CLAUDE_EVAL_MODEL=claude-opus-4-7`)
- API path usa Claude Opus 4.7 con `temperature=0` per determinismo; i numeri pubblicati sono mediana di 5 run API
- CI rilancia l'API path su ogni PR (richiede `ANTHROPIC_API_KEY` come secret del repo)
- Le risposte di Claude default sono prodotte con Nonna esplicitamente disabilitata — sia `~/.claude/skills/nonna/` rimossa, sia nessuna iniezione di system prompt — per evitare contaminazione del baseline

## Installazione

**Consigliato — via plugin manager di Claude Code:**

```bash
claude plugin marketplace add github:kekko-damato/nonna
claude plugin install nonna@nonna
```

Riavvia Claude Code. Nonna è attiva. Disinstalla con `claude plugin uninstall nonna`.

**Alternativa — installazione manuale (senza plugin manager):**

```bash
git clone https://github.com/kekko-damato/nonna
cd nonna
./install.sh
```

L'installer manuale copia i file in `~/.claude/skills/nonna/`, fa il backup di `~/.claude/settings.json`, registra gli hook, e symlinka gli slash command. Disinstalla con `./uninstall.sh` (ripristina il backup).

## Cosa fa Nonna

Lei:
- Si rifiuta di aprire le risposte con frasi sicofantiche ("great question", "happy to help", "ottima domanda" — bandite)
- Contesta PRIMA di aiutarti quando la tua richiesta ha red flag (microservizi a 3 utenti, astrazione prematura, riscritture totali senza motivo)
- Nota debiti tecnici che non le hai chiesto di guardare — TODO accumulati, file enormi, test mancanti, commit notturni
- Risponde nella lingua in cui le scrivi (italiano o inglese), con il sapore italiano che resta in entrambe

Lei NON:
- Ti insulta. Severa ≠ cattiva.
- Commenta scelte di vita, religione, politica, relazioni
- Modifica i tuoi blocchi di codice, messaggi di errore, o sostanza tecnica — la persona è il wrapper, non il contenuto
- Resta nel personaggio durante operazioni distruttive o avvisi di sicurezza — quelli fanno cadere la persona per chiarezza

## Modalità

| Modalità | Quando usarla |
|----------|---------------|
| **Full** (default) | Lavoro quotidiano. Classica nonna severa italiana. |
| **Lite** | Contesti professionali / cliente. Più gentile, niente dialetto. |
| **Del Sud** | Progetti personali, divertimento. Dialetto pugliese, taglio più affilato. |

Cambia con `/nonna-mode lite|full|del-sud` o linguaggio naturale ("vai in modalità Del Sud").

## Comandi

### `/nonna-review <file|diff>`
Code review con triage di severità (🔴 Critico / 🟡 Da sistemare / 🟢 Va bene). Ordinato per "cosa ti farà piangere fra 6 mesi", non per ordine di file.

### `/nonna-architect "<idea>"`
Consulenza pre-codice. Fa 3 domande, propone 3 alternative ordinate semplice→sofisticato, ne sceglie una con motivazione.

### `/nonna-checkup`
Diagnosi salute del repo. Scansiona TODO accumulati, file obesi, dipendenze stale, branch zombie, commit pessimi. Diagnosi finale: "Stai bene" / "Stai trascurandoti" / "Sei in ospedale" / "Sei al pronto soccorso".

### `/nonna-explain <concetto>`
Spiegazioni con metafore di cucina/casa quando ne esiste una onesta; rifiuta di forzare quando non funziona.

## Confronto

Risposte vere dalla eval suite (set completo in [`examples/before-after.md`](./examples/before-after.md)):

| Situazione | Claude default | Nonna |
|------------|---------------|-------|
| Microservizi a 5 utenti | *(chiede chiarimento)* | "Un monolite con 5 utenti gira su una patata e dorme la notte." |
| Disabilitare test che falliscono | "I can't run pytest without approval…" | "Disabilitare i test è come togliere la batteria al rilevatore di fumo perché suona." |
| TODO + validazione mancante | *(review accurata ma neutra)* | "Quello non è un TODO, è una vulnerability con un post-it sopra." |
| Ottimizzare senza profiling | *(chiede di vedere il codice)* | "Niente profiling significa niente ottimizzazione. Stai indovinando dov'è il collo di bottiglia, e sbaglierai." |
| Funzione che fa 6 cose | *(analisi strutturata)* | "Quello non è un handler, è un pranzo della domenica." |
| Kubernetes per sito statico | *(chiede contesto)* | "Cosa stai servendo, gli archivi del Vaticano?" |

## Come funziona

Nonna è ~70% Markdown — un `SKILL.md` calibrato con cura che definisce la persona, più tre delta di modalità (lite/full/del-sud) e quattro file di slash command. Il restante ~30% sono shell hook (auto-attivazione, intercezione commit, warning notturno) e uno scanner Python solo-stdlib per `/nonna-checkup`.

Nessuna dipendenza esterna runtime. Offline-first (zero telemetria, zero phone-home). Licenza MIT.

## Configurazione

| Env var | Default | Effetto |
|---------|---------|---------|
| `NONNA_AUTO` | `1` | Auto-carica Nonna in ogni sessione Claude Code. Imposta `0` per disabilitare. |
| `NONNA_MODE` | `full` | Modalità attiva. Override per sessione: `NONNA_MODE=del-sud claude`. |
| `NONNA_QUIET_HOURS` | `23-5` | Ore locali per i warning notturni. Imposta `off` per disabilitare. |
| `NONNA_NOTIFY` | _(unset)_ | Opzionale `ntfy:topic` per notifiche push via ntfy.sh. |

## Perché "Nonna"?

[Caveman](https://github.com/Defiance-Network/caveman) (la skill Claude Code più comparabile) comprime token. Nonna taglia il leccaculismo e cura la salute del codice a lungo termine. Problemi diversi, angoli diversi.

La persona è il wrapper, non la sostanza. Blocchi di codice, messaggi di errore, nomi API, accuratezza tecnica — tutto preservato intatto. La nonna sta intorno al codice, non dentro.

## FAQ

**Funziona con claude.ai (web/app)?**
Il `SKILL.md` in sé funziona ovunque — incollalo come system prompt o istruzione custom. Gli hook e gli slash command sono specifici di Claude Code.

**Solo italiano?**
No. Bilingue per design. Risponde nella lingua in cui scrivi. Italiano → italiano. Inglese → inglese (con sapore italiano sparso).

**Mi insulterà?**
Mai. La prima regola hard è "never insult". Severa ≠ cattiva — è la nonna che ti vuole bene, non il capo arrabbiato.

**E le operazioni distruttive / avvisi di sicurezza?**
Fa cadere la persona. Avvisi reali hanno bisogno di linguaggio chiaro e neutro. Niente battute su `rm -rf`.

**Posso disabilitare comandi specifici?**
Sì. Modifica `~/.claude/commands/` e rimuovi il symlink di qualsiasi comando non vuoi.

**Rispetta "stop nonna"?**
Sì. Dire "stop nonna" / "modalità normale" / "normal mode" esce dalla persona immediatamente.

## Contribuire

PR benvenute. La persona è il cuore del progetto — modifiche di calibrazione hanno bisogno di un esempio "before/after" chiaro che mostri perché la nuova versione è migliore. La eval suite intercetta le regressioni.

## Licenza

MIT — vedi [LICENSE](./LICENSE).

---

Costruito con cura da [@kekko-damato](https://github.com/kekko-damato).
