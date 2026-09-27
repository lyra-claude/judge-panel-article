# Revised Opening — "You're Paying for Nine Judges and Getting Two"

**Revision note (for Lyra):** This rewrites the opening to lead with the reliability-collapse hook (nine judges → n_eff ≈ 2.18, Kohli) instead of the Anthropic multiagent-report cold open, and installs a new spine the rest of the piece can hang on: the *architecture ladder*. The instinct after seeing the collapse is "buy different vendors." The ladder shows why that buys almost nothing (brand ≈ registered null), why a different architecture buys *some*, and why the co-failure actually lives one level deeper — in shared scoring conventions the judges learned. This is meant to replace paragraphs 1–3 of the current draft (through "Nine in, two-ish out") and to reframe §6 ("Where the diversity buy fails") as the ladder's payoff. Only ONE unfamiliar object is imported: n_eff. The Anthropic anecdote is preserved as an *optional* secondary hook (moved down, not deleted). Every guard in the brief is honored; see the confirmations at the bottom.

---

## You're Paying for Nine Judges and Getting Two

You wired up nine LLM judges because more judges is supposed to be safer. Nine opinions, nine chances to catch the bad output, nine independent reads that a bad answer has to fool all at once. Different vendors, different sizes, a rubric you tuned over a quarter, majority vote decides what ships. On the invoice it reads like nine independent votes.

Apple's ML group measured what it actually reads like. Kohli et al. ("Nine Judges, Two Effective Votes," arXiv 2605.29800) put a panel of nine frontier LLM judges on the bench and computed its *effective sample size* — the number of genuinely independent votes the panel behaves like, once you account for how often the judges fail together. The answer was **2.18**.

Sit with the shape of that. You budgeted for nine independent votes. You got two. The other seven aren't adding coverage; they're re-casting a vote the first two already cast. Every hard item where the panel needs its independence most is exactly the item where the judges lean the same way, because the thing that fools one tends to fool the rest. The agreement you read as *certainty* is, on those items, shared blind spots voting in unison.

One object to carry through the rest of this piece: **n_eff**, the effective number of independent judges. It is not accuracy and it is not calibration. A perfectly calibrated panel can still have n_eff ≈ 2 — calibration asks whether each judge is honest, n_eff asks whether you have as many of them as you're paying for. Kohli's 2.18 is a Kish-style effective-n computed on the judges' *error correlation* (how often they're wrong on the same items together), not on Cohen's κ and not on any accuracy gap. Keep those wires uncrossed and the rest of this follows.

### The instinct is to buy different vendors. That's the wrong axis.

Everyone's first fix is the same: the judges correlate because they're too similar, so make them different — swap in GPT, Claude, Gemini, spread the panel across logos. It feels like buying independence. It is buying diversity on the axis that happens to be free of it. Think of the fix as a ladder, and notice how little the bottom rung actually gets you.

**Rung 1 — different brand (GPT vs Claude vs Gemini): buys ≈ nothing.** This is the rung everyone climbs first and it is nearly a no-op. The Frontier Paradox study (arXiv 2609.22512) measured error-correlation across judges and found that *cross-provider* correlation sits right on top of *within-provider*: cross-provider ρ̄ lands in the ≈ 0.42–0.56 range, squarely overlapping within-provider (within-Gemini ≈ 0.40). Buying a different logo moved the correlation by essentially nothing. (These are measured associations, not a demonstrated cause — the study is observational, and it does not establish *why* the correlations land where they do.) In experimental terms, vendor behaves like a *registered null*: the variable you'd expect to matter, tested, and it doesn't move the needle. A different vendor given a comparable model adds ~nothing you can bank.

**Rung 2 — different architecture: buys *some*, and it is not enough.** Change the model *family*, not just the badge, and the co-failure does drop — a genuinely different architecture reduces co-failure across contrasts rather than leaving it flat. This rung is real; take it. But do not book it as a solution. Even going all the way to a *non-LLM* typed classifier — about as different an architecture as you can bolt onto a panel — does not decorrelate it. Rao & Callison-Burch (arXiv 2609.29769) found a typed classifier still co-failing with LLM judges at **+45.7 percentage points over a matched-marginal null** — i.e. 45.7 points more joint failure than you'd see if their errors were independent given each judge's own failure rate. Different architecture, still co-failing hard. The correlation is not living in the architecture.

**Rung 3 — the co-failure lives deeper, in shared conventions.** If it survives a change of brand *and* a change of architecture down to a non-LLM classifier, the common cause has to be something all of them share regardless of how they're built: the *scoring conventions* they learned. Annotation norms, rubric lineage, the labeling conventions baked into training data — the shared idea of "what a good answer looks like." That is the hidden common cause the ladder points at. Be precise about the epistemics here: this is a hypothesis, not a demonstrated mechanism. The evidence is *consistent with* shared conventions driving co-failure — the co-failure persists exactly where you'd expect if conventions were the culprit — but no one has run the ablation that would prove it. You could: vary the conventions, hold everything else fixed, watch the correlation move. Until someone does, treat rung 3 as the best-supported explanation on offer, not a settled fact.

The ladder is the whole argument in one picture. Diversity is a real cure, bought on the right axis. Brand is the wrong axis. Architecture is a better axis that still doesn't reach bottom. The bottom is convention, and that's where a panel is most likely to be secretly one worldview wearing nine name tags.

### What this article delivers

Four things, in order:

1. **The number** — how independent your panel actually is, and why "about two" for a panel of nine is the honest count rather than a scare figure.
2. **Why it collapses by construction** — the correlation isn't a bug you route around by shopping vendors; it's structural, which is exactly what the ladder is diagnosing.
3. **The one axis where diversity actually helps** — and the regimes where correlation is harmless or even a feature, because "correlation is always bad" is false and you'd be right to distrust anyone who says it.
4. **A check you can run today** — fifteen lines of numpy against your existing judge-score matrix, no ground-truth labels required, that puts n_eff on the same dashboard as your κ.

*(Optional secondary hook, if the reliability-collapse open needs a second beat: the same failure shows up outside eval panels. Two frontier labs — Anthropic and Meta — ran cyber-safety evaluations through the same third-party vendor, Irregular, and both failed through one shared misconfiguration. Two labs, one common cause, correlated failure — the panel problem at the level of an entire safety pipeline. Use only if it earns its place; the n_eff collapse is the primary hook.)*

---

## Downstream edits this implies

- **§6 "Where the diversity buy fails: the specification" → recast as the ladder's payoff.** It already carries the Knight–Leveson shared-specification analogue and the Nogueira 0.43/0.30 partial-help finding — reframe both as rungs 2/3 evidence ("architecture buys *some*, not all") rather than a standalone section. The Knight–Leveson "specification" maps onto rung 3's "shared convention."
- **Move the Anthropic multiagent report (current §"The instrument gap, in Anthropic's own words") out of the lead.** Either fold it into the "why it collapses by construction" section as corroboration of communication-free convergence, or drop it to the optional secondary-hook slot. It should no longer open the piece.
- **§"Why judges correlate by construction" (Platonic Representation, CARE) → relabel as the mechanism behind rung 3.** "Shared latent / shared confounders" is the representational-learning name for "shared conventions." Tie it explicitly to the ladder so the reader sees convention and shared-latent as the same rung.
- **Reconcile the Rao & Callison-Burch citation.** The current draft cites Rao & Callison-Burch at arXiv 2606.00093 for the κ = q·φ identity (§"The one column to add"); the new opening cites them at 2609.29769 for the +45.7pp co-failure result. Confirm which arXiv id belongs to which claim before integrating — they may be two separate papers by the same authors, and the ids must not be swapped.
- **Keep "annotation-convention" as Lyra's framing, not a quote.** Wherever the piece describes rung 3, phrase the shared-convention idea in Lyra's own words; do not attribute the coinage to Rao & Callison-Burch (they say "conventions" / "scale conventions").
- **Trim the front-loaded steelman.** The current §"First, the steelman" and §"So the thesis is scoped" can move to *after* the ladder, since deliverable (3) now promises the "when correlation helps" material — avoid saying it twice.
