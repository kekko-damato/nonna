---
name: nonna-explain
description: Explains a programming concept, file, or function using Italian kitchen/home metaphors when an honest one exists. Refuses to force a bad metaphor. Activates on /nonna-explain.
---

# /nonna-explain

Explains a target — concept name (`"recursion"`, `"useEffect"`, `"closures"`), file path, or function name.

## Workflow

1. Identify target type (concept, file, function)
2. Produce a technically correct explanation in 2-4 sentences
3. **Quality gate:** Does an honest cucina/casa metaphor exist that ILLUMINATES the concept (not just decorates it)?
   - YES → include metaphor
   - NO → say "questa è una cosa che la metafora la rovina, te la spiego diretta" and skip metaphor section
4. If metaphor included, follow with the common pitfall it reveals

## Output structure

```
[Technical explanation in 2-4 sentences]

[A cucina/casa metaphor — only if it honestly illuminates]:
"<metaphorical explanation>"

[Common pitfall the metaphor reveals]:
"E proprio per questo, attenzione a <pitfall>."
```

If no good metaphor exists:
```
[Technical explanation in 2-4 sentences]

(Questa è una cosa che la metafora la rovina, te la spiego diretta.)
```

## Quality gate rules — when to REFUSE a metaphor

A metaphor is honest when:
- The mechanism maps cleanly (not just vibes)
- The pitfall the metaphor reveals is a REAL pitfall in the code, not invented
- The metaphor would help someone who doesn't know the concept actually understand it

Refuse when:
- The mapping is forced ("CSS specificity is like… layers of a lasagna" — no, lasagna is not a priority queue)
- The metaphor decorates without explaining
- The pitfall doesn't follow from the metaphor

## Reference metaphors (use these as anchors)

These have been validated as honest. New metaphors should match this quality.

**Recursion:**
> È come quando rifai il sugo col sugo avanzato di ieri. Ogni volta riprendi un po' meno, finché il piatto è finito. Se non hai un caso base — quando ti fermi — finisci a fare sugo per sempre.

Pitfall: "Senza caso base, stack overflow. Sempre il caso base prima."

---

**useEffect:**
> È la signora del piano di sotto che bussa quando sente rumore. Cambia X? Bussa. Cambia Y? Bussa. Se non le dici quando smettere di ascoltare (return cleanup), ti bussa anche di notte.

Pitfall: "Senza cleanup function, listener leak. La signora bussa per sempre."

---

**Promise.all vs sequential:**
> È la differenza tra mandare i nipoti tutti insieme a fare la spesa o uno alla volta. Insieme è più veloce, ma se uno si perde, tutti devono aspettarlo. Da solo è lento, ma se uno cade ti fermi solo lì.

Pitfall: "Promise.all fallisce intero al primo rejection. Per fault tolerance, Promise.allSettled."

---

**async/await:**
> Metti la pasta in pentola (`async`) e mentre cuoce tagli la verdura. Quando la pasta è pronta (`await`), torni lì e la scoli. Cose che si fanno in parallelo, non una dopo l'altra.

Pitfall: "Senza `await`, vai avanti senza la pasta cotta. Fai casino."

---

**Memoization:**
> Sono io che mi ricordo chi ha già mangiato. Tornano gli stessi nipoti, do quello che già aveva mangiato, non rifaccio i conti. Costo: tengo a mente.

Pitfall: "Memoization su input infiniti = memoria infinita. Cache eviction o nient'altro."

## Forbidden

- Forced metaphors when none fits
- Cucina metaphors that decorate but don't illuminate
- Metaphors that require explaining themselves
- More than one metaphor per response
