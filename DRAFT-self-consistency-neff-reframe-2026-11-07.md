# Self-consistency isn't losing its edge — it's running out of effective samples

**DRAFT — work in progress, not reviewed.** 2026-11-07.

*Note on sourcing: every number attributed to a paper below is verified-from-primary. Anywhere I go beyond what a paper actually states, I mark it inline as my inference. Don't quote the inferences as if they were someone's findings.*

---

## The complaint

The complaint about self-consistency is now a genre. You sample k reasoning paths from a
single model, take the majority answer, and the accuracy curve flattens almost immediately.
People call this "diminishing returns on samples" and move on, usually to a more expensive
decoding trick.

The numbers are real and they are small. Loo's "Self-Consistency Is Losing Its Edge" (arXiv
2511.00751) scales sampled reasoning paths out to 20 and reports the accuracy gain is **0.4% on
HotpotQA** and **1.6% on MATH-500**. Performance plateaus early and, at high sample counts,
sometimes declines. That last part matters: you are not asymptoting toward a ceiling, you are
occasionally sliding back down from it.

The usual reading is that majority voting is a weak aggregator and we should weight the votes.
CISC — "Confidence Improves Self-Consistency in LLMs" (Taubenfeld et al., ACL 2025 Findings,
arXiv 2502.06233) — does exactly that, weighting each path by the model's own confidence, and it
works: **over 40% fewer reasoning paths on average** to reach the same answer. Good engineering.
But notice what it concedes. If you can throw away 40% of your paths and lose nothing, 40% of
your paths were carrying no new information. That is not a decoding problem. That is a counting
problem.

## The reframe

Here is the lens. *(This mechanism — tying these particular diminishing-returns results to a
single n_eff story — is my reframe. The cited papers do not prove it. They supply the symptoms;
the diagnosis below is mine.)*

You are not hitting diminishing returns on **samples**. You are hitting diminishing returns on
**effective samples**.

Twenty reasoning paths from one model are not twenty independent draws. They are twenty draws
from one set of weights with one set of biases, one training mix, one preferred way of being
wrong. When the model is confidently mistaken about a question, resampling it does not give you a
second opinion — it gives you the same opinion in a new costume. The paths are correlated, and
correlated draws don't add up the way independent ones do.

This is the same arithmetic the companion article runs on LLM-judge panels, just pointed at a
different population. The Kish design-effect formula for the effective number of independent
draws is

    n_eff = n / (1 + (n−1)·ρ)

where n is how many samples you actually drew and ρ is the mean pairwise correlation of their
errors. Read the limits off it directly. If ρ = 0 the samples are independent and n_eff = n —
every path earns its keep. If ρ = 1 they are perfect copies and n_eff = 1 no matter how large n
gets. In between, n_eff saturates at 1/ρ and stops moving. Draw the 21st path, the 50th, the
200th — past the saturation point you are paying for samples the estimator has already stopped
counting.

That is the whole shape of the complaint. A curve that climbs for the first few samples and then
flattens is exactly what n/(1 + (n−1)ρ) looks like when ρ is bounded away from zero. The plateau
is not a property of majority voting. It is a property of drawing repeatedly from one model.

So "self-consistency is losing its edge" is, on this reading, a statement about ρ. You were
never going to beat the correlation structure by drawing more from inside it.

## What this reframe buys CISC — and what it warns about

The lens also explains *why* confidence weighting helps. CISC's 40% path-count reduction is what
you'd expect if confidence is an imperfect proxy for which draws are redundant: down-weight the
agreeing-because-correlated mass and the effective count per path goes up, so you need fewer
paths. *(That causal story is my interpretation, not a CISC finding — CISC does not measure
correlation or redundancy. They report the path-count reduction; the n_eff explanation for it is
mine.)*

But the same lens carries a warning, and I want to be careful about whose claim it is. CISC does
not study correlated or shared errors at all. The one thing they state that touches this is a
theoretical worst-case binary framing: in the worst case, all the incorrect answers are
identical. **Here is my extension of that worst-case framing, flagged as mine:** under a model
monoculture, "all incorrect answers identical" is not a pathological corner — it is the
*expected* behavior when the model is systematically wrong, because the errors share a source. In
that regime a confidence-weighted vote can confidently up-weight the shared wrong answer. The
weighting that saves you paths when confidence tracks correctness can amplify a correlated
mistake when confidence tracks the model's bias instead. That is not something CISC claims. It is
what their worst case looks like once you believe errors are correlated rather than independent.

The code-generation people have already seen the amplification directly. Vallecillos-Ruiz, Hort &
Moonen, "Wisdom and Delusion of LLM Ensembles for Code Generation and Repair" (arXiv 2510.21513),
report that consensus strategies "fall into a 'popularity trap,' amplifying common but incorrect
outputs." Their numbers on the other side are striking: the ensemble upper bound can sit **up to
83% above the best single model**, and a diversity-based strategy realizes **up to 95% of that
bound**. Read those two facts together. The headroom is enormous and it is unlocked by
*diversity*, not by consensus — consensus is the thing that walks into the popularity trap.
*(Their stated claim is the amplification of common-but-incorrect outputs. If you want the
sharper line — that naive consensus can underperform a single model — treat that as my inference
from the popularity-trap result, not as a number they report.)*

The parallel to the companion piece is qualitative and I'll keep it that way: that article found
a double-digit panel of LLM judges behaving like roughly two effective judges. Different study,
different estimand, different numbers — I am not chaining anything here to that figure. The shared
moral is only that a count you thought was large collapses to a small effective count once you
measure how correlated the members are.

## The foil: even the sequential governors assume independence

You might hope the adaptive-compute crowd has already solved this. FOIL's Wald-SPRT governor
(Morandi, arXiv 2605.19193) is the sharpest version — a sequential probability-ratio test used as
a "compute governor" for multi-agent debate, spending more rounds on hard items and cutting off
easy ones. It is genuinely good engineering, and on MMLU it is efficient: the calibrated KL
"collapses to about 0" and the rule "caps on 99.5% of items."

But read the assumption. FOIL works "under i.i.d. assumptions" — it treats successive rounds as
independent evidence. And look at where it degenerates: the KL collapsing to zero means the
rounds have stopped being discriminable, so the test caps out and stops. That degenerate regime —
rounds carrying no new information — is *precisely* the correlated regime this reframe is about.
The SPRT doesn't measure the correlation; it assumes it away, and then quietly bottoms out
exactly when the correlation bites. The governor tells you when to stop spending compute. It does
not tell you that the reason you should stop is that your samples were never independent to begin
with.

## What's actually missing

So the gap, stated plainly: all of these — majority voting, confidence weighting, sequential
compute governors — assume the samples are independent evidence and then underdeliver exactly in
proportion to how correlated the samples really are. None of them *measure* that correlation
while it's happening.

That measurement is the thing I keep circling back to: an anytime-valid, margins-free monitor of
co-failure — a test you can peek at after any number of samples without blowing your error rate,
that needs no ground-truth labels and no assumed base rates, and that reports when ρ is rising
and your effective-n is sliding toward 1. The SPRT foil is anytime-valid but assumes independence;
the diminishing-returns papers measure the symptom but not the correlation. The monitor is what
sits in the empty chair.
