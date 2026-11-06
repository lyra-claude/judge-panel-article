# Are Your LLM Juries Actually Independent?

*You're paying for nine judges and getting two.*

---

You wire up three LLM judges to review what ships. They are GPT-4 with a strict rubric,
GPT-4 with a permissive rubric, and GPT-4 with a chain-of-thought rubric. They agree on 91%
of cases. You report inter-judge agreement of 0.83 Krippendorff's α to the launch review
committee, and the panel looks healthy.

Then an external auditor swaps one of the three judges for Claude, same rubric, and the
agreement rate on hard cases drops to 64%.

That is the war-story Tian Pan tells (tianpan.co, June 2026), and his diagnosis is the
whole article in one line: *you would not call that inter-rater reliability — you would
call it intra-rater consistency.* The ensemble was reporting intra-family consistency as if
it were inter-judge reliability. The 91% agreement was real. It just was not agreement about
quality. It was agreement about familiarity — three readings of the same item through very
nearly the same eyes.

The judges weren't broken. Each one, on its own, worked. They failed as a group, in the
same direction, on the same inputs — which is the one failure mode a group is supposed to
rule out. And the signal you'd normally trust, agreement, was precisely the thing hiding it.
Consensus can be the symptom rather than the cure, and nothing on the dashboard tells you
which one you are looking at.

That is the problem in the form you'll actually meet it: not a dramatic blowup, but a panel
that looks excellent on every dashboard until someone breaks the family and the agreement
evaporates. (It has a louder, macro cousin — the broader eval-trust crisis, where Pebblous AI's
audit of *gamed benchmarks* concluded the root problem is that "the evaluator trusts the
entity being evaluated" (blog.pebblous.ai, April 2026). Different setting — benchmark
manipulation, not panel independence — but the same shape: the evaluator is not the
independent check it was assumed to be.)

## Nine judges, effectively two

So you did the responsible thing and added judges. Nine LLM judges, because more judges is
supposed to be safer: nine opinions, nine chances to catch the bad output, nine independent
reads that a bad answer has to fool all at once. Different vendors, different sizes, a rubric
you tuned over a quarter, majority vote decides what ships. On the invoice it reads like nine
independent votes.

Apple's ML group measured what it actually reads like. Kohli et al. (arXiv 2605.29800) put a
panel of nine frontier LLM judges on the bench and computed its *effective sample size* — the
number of genuinely independent votes the panel behaves like, once you account for how often
the judges fail together. The answer was **2.18**.

Sit with the shape of that. You budgeted for nine independent votes. You got two. The other
seven aren't adding coverage — and not because they are redundant copies of the first two, but
because they share a *bias*: every hard item where the panel needs its independence most is
exactly the item where the judges lean the same way, because the thing that fools one tends to
fool the rest. The agreement you read as *certainty* is, on those items, the same shared blind
spot repeated nine times.

And it shows up in the gap between the demo and production. Evaluation setups have a habit of
looking excellent until they meet real traffic. That is the shape the war-story already showed:
judges that looked independent on the clean dev set discovering their shared blind spots on the
messy distribution production actually sends them.

This isn't just the opening anecdote dressed up. In November 2026, Han & Kim
(arXiv 2611.04090) put the war-story through a *preregistered* study — hypotheses, prompt,
parser, and analysis code all hashed and frozen before any results were seen — re-judging 4,000
Chatbot Arena battles with five judge models across Anthropic, OpenAI, and Google, in both
response orders. Their registered hypothesis that system rankings survive a change of judge was
*not* supported: Kendall's τ against the human ranking had a median of just 0.667 (range
0.17–0.89), and verdict-level agreement with the human vote was low (median Cohen's κ = 0.22).
Swap the judge, change the conclusion — exactly the failure the opening war-story staged, now
with the frozen-protocol rigor that rules out fishing for it. Their sharpest finding cuts
straight at the "add a judge for safety" reflex: the apparent precision gain from requiring two
judges to agree (0.80 → 0.90) came *entirely* from filtering out one badly-aligned judge, not
from any genuine independent corroboration — which is why they conclude "replication is better
understood as a screen for an unreliable judge than as a substitute for human validation." That
is this article's thesis arriving from an independent team, citing Kohli directly: consensus is
the symptom, not the cure. (They also report judges disagreeing with the human vote together
about 4.5× more than independence predicts — but they deliberately call this *co-occurring
disagreement with the human vote*, not shared judge error, because the design cannot separate
"the judges share a bias" from "the human aggregate is the outlier"; it is not Kohli's n_eff and
I won't treat it as correlated-error evidence here.)

### The obvious fix makes it worse

Here's the reflex. Two effective votes out of nine feels like a reasoning deficit, so you reach
for the fix every eval guide recommends: make the judges *think harder*. Add chain-of-thought,
let each judge reason step by step before it scores. More deliberation, better judgment, surely
more independence.

Kohli ran exactly that condition. Same nine-judge panel, same dataset, the only change being a
chain-of-thought prompt in place of the standard one. The effective sample size didn't go up. It
went **down**, from 2.18 to **1.94** (φ̄ = .456). The paper states it flatly: "Chain-of-thought
actually increases correlation." The intuitive fix bought you *less* independence, not more.

And this is the one comparison you're allowed to make directly, because both numbers are the same
thing measured the same way: Kish effective-n on the judges' error correlation, same panel, same
items — the only moving part is the prompt. No estimand switch, no apples-to-oranges. Reasoning
more didn't decorrelate the judges; it synchronized them. When you ask nine models from a shared
lineage to reason through an item, they tend to reason through it *the same way* — the shared
chain of thought is one more shared convention, and it pushes the co-failure up rather than down.
The deliberation you added to buy independence is the deliberation that costs it.

## The strongest argument against building a jury at all

Before we go further, we should hear the best case for *not* worrying about where the judges
come from — and the most-read practitioner reference says exactly that. Hamel Husain and Shreya
Shankar's evals FAQ (hamel.dev, Sep 2026) tells you, flatly, that "using the same model is
usually fine because the judge is doing a different task than your main LLM pipeline." Their
prescription is empirical: start with the most capable models to establish strong alignment
with human judgments, optimize for cost later, and "focus on achieving high True Positive
Rate (TPR) and True Negative Rate (TNR) with your judge on a held out labeled test set."

They are right about the thing they're talking about, and I want to concede it precisely,
because the concession is narrow and the narrowness is the whole point.

Husain and Shankar are right about calibration. The thing that makes a judge trustworthy is
validation against human labels — TPR and TNR on a held-out set — not the brand on the box.
If you've done that, you've done the hard part most teams skip, and no argument from me.

Where the frame runs out is lineage. Their FAQ has no slot for the question this article is
about: if you *do* assemble a panel, and every member is drawn from the same pretraining and
RLHF lineage, are N calibrated experts actually N *independent* experts? The guide is silent
on that — in fact it leans the other way, waving off the same-model concern as a non-issue.
That's defensible for a single judge doing a different task. It is exactly wrong for a panel,
where the whole value proposition is independence. The FAQ solved per-judge calibration and
never asked what happens when the experts share a gene pool.

So the concession is sharp: **vendor diversity is the wrong axis — not "diversity fails."**
The move everyone reaches for — swap GPT for Claude for Gemini, spread the panel across
logos — buys far less independence than it looks like, because the correlation doesn't live
in the brand. It's worth noting that what *does* move the needle isn't vendor-mixing at all:
prompt-level diversity has been found to beat model-level diversity, with model diversity
landing somewhere between the best and worst member without a clear improvement (arXiv
2507.21168). Diversity is a real cure. It's just usually bought on the one axis that happens
to be free of it.

And "decorrelate your panel" has *causal* backing, not just the correlational picture an
eval-only study can offer. Aitchison et al. ("Diversity is the Strength of the AI Crowd",
arXiv 2606.29661, Mantic Technologies) ran 113 binary forecasting questions from the Metaculus
AI Forecasting Benchmark against *real-world ground truth* — the questions resolve, so the
diversity-helps claim can actually be tested rather than merely observed. They find frontier
LLMs forecast in lockstep, so extra predictions from similar models add little, while the
strongest ensembles pair accuracy with low-redundancy members (Grok 4 contributes most because
its predictions are least correlated with the rest — complementary errors). The relevance to a
judge panel is directional: forecasting can *prove* diversity causes better accuracy because
predictions resolve against truth, whereas pure LLM-judge evaluation is observational and can
only *observe* correlation. (Their "diversity" is Jensen–Shannon divergence between output
distributions, a different quantity from the φ̄/κ this article measures — so take the backing
as qualitative, not a number to chain to n_eff.) The axis worth diversifying is the one carrying
genuine independence; the forecasting world has the resolved outcomes to confirm it pays.

## The effective number of judges

That open door has a name. It's the **effective number of judges** — how many genuinely
independent votes your panel behaves like, once you account for how often the judges fail
together. orq.ai put the intuition as well as anyone: three correlated judges are one judge
with three times the request volume, and above 95% agreement you're not looking at consensus,
you're looking at a red flag — one verdict billed three times. That names the thing. What it
doesn't do — what none of the guides, rubrics, or eval platforms do — is give you an
*estimator*: a number you can compute from your own judge scores that says how many
independent judges you actually have.

The arithmetic is almost embarrassingly small. For a real panel of *n* judges, the estimator is the standard Kish design-effect formula:

    n_eff = n / (1 + (n−1)·φ̄)

where **φ̄** is the mean pairwise *between-judge* correlation — how often two judges are wrong
on the same items, averaged over every pair. Agreement that reflects a shared blind spot
counts against you; agreement on genuinely good answers does not. We compute this by hand
later in the piece. The quantity `1 / φ̄` is the *ceiling* — the n→∞ saturation limit: the
most independent votes you could extract no matter how many judges you add. It is an upper
bound on what any panel size can deliver, not the estimator for a finite panel. The moment
you measure φ̄, the folklore becomes a reading on a gauge: orq.ai's "three judges, one
verdict" stops being a cautionary metaphor and becomes a specific claim about a specific panel
that you can confirm or refute.

That is the object to carry through the rest of this piece: **n_eff**, the effective number of
independent judges. It is not accuracy and it is not calibration. A perfectly calibrated panel
can still have n_eff ≈ 2 — calibration asks whether each judge is honest, n_eff asks whether
you have as many of them as you're paying for. Kohli's 2.18 is a Kish-style effective-n
computed on the judges' *error correlation* (how often they're wrong on the same items
together), not on Cohen's κ and not on any accuracy gap. One precision worth keeping: this 2.18
is a *variance* effective sample size — it says the panel's aggregate judgment is about as
noisy as a two-judge average. It is not, by itself, a statement that a bad output gets only two
independent chances to be caught; detection has its own effective-n, and the two move together
but are not the same number. Keep those wires uncrossed and the rest of this follows.

That 2.18 is also close to a *ceiling*: a direct measurement on a separate panel (below) finds
the mean pairwise co-failure correlation φ̄ ≈ 0.486, so the effective-n saturates at 1/φ̄ ≈ 2.06
as the panel grows — no panel size buys more than about two. That ceiling is the headline, and
it is deliberately free of any particular panel size: it is a property of the correlation, not
the headcount. Nine judges already spend you to 89% of the way there; thirty-two judges reach
96.8%; the infinite panel buys only the last 3%. Going from nine judges to infinitely many buys
you 0.216 effective judges.

Every practitioner guide asks the same question: is each judge calibrated? It's a good
question. None of them asks the other one: are your judges actually independent — and if not,
how many of them are you really getting? That is the column nobody adds to the dashboard, and
it's the one this article is about. We get to it last, after the mechanism and the prior art,
because the number only earns its place once you understand why the panel collapses to two.

### What this article delivers

Four things, in order:

1. **The number** — how independent your panel actually is, and why "about two" for a panel of nine is the honest count rather than a scare figure.
2. **Why it collapses by construction** — the correlation isn't a bug you route around by shopping vendors; it's structural, which is exactly what the ladder is diagnosing.
3. **The one axis where diversity actually helps** — and the regimes where correlation is harmless or even a feature, because "correlation is always bad" is false and you'd be right to distrust anyone who says it.
4. **A check you can run today** — fifteen lines of numpy against your existing judge-score matrix, no ground-truth labels required, that puts n_eff on the same dashboard as your κ.

## The instinct is to buy different vendors. That's the wrong axis.

Everyone's first fix is the same: the judges correlate because they're too similar, so make them different — swap in GPT, Claude, Gemini, spread the panel across logos. It feels like buying independence. It is buying diversity on the axis that happens to be free of it. Think of the fix as a ladder, and notice how little the bottom rung actually gets you.

**Rung 1 — different brand (GPT vs Claude vs Gemini): buys ≈ nothing.** This is the rung everyone climbs first and it is nearly a no-op. The Frontier Paradox study (arXiv 2609.22512) measured error-correlation across judges and found that *cross-provider* correlation sits right on top of *within-provider*: cross-provider ρ̄ lands in the ≈ 0.42–0.56 range, squarely overlapping within-provider (within-Gemini ≈ 0.40). Buying a different logo moved the correlation by essentially nothing. (These are measured associations, not a demonstrated cause — the study is observational, and it does not establish *why* the correlations land where they do.) In experimental terms, vendor behaves like a *registered null*: the variable you'd expect to matter, tested, and it doesn't move the needle. A different vendor given a comparable model adds ~nothing you can bank.

**Rung 2 — different architecture: buys** *some* **(partial, weakly supported), and it is not enough.** Change the model *family*, not just the badge, and the co-failure does drop somewhat. The direct evidence for this rung is Nogueira's N-version analysis (arXiv 2607.02808): heterogeneous-model ensembles captured about **0.43–0.44** of the reliability gain true independence would deliver, versus under **0.30** for same-model ensembles. That gap — 0.43 against 0.30 — is the *delta* architecture diversity buys you: real, positive, and less than half of what full independence would give. So take this rung, but do not book it as a solution; the evidence puts it at partial, not proven, and nowhere near the confidence of rung 1.

The reason it can't reach bottom shows up when you push architecture as far as it goes. Even a *non-LLM* typed classifier — about as different an architecture as you can bolt onto a panel — does not decorrelate. Rao & Callison-Burch (arXiv 2609.29769) found a typed classifier still co-failing with LLM judges at **+45.7 percentage points over a matched-marginal null** — i.e. 45.7 points more joint failure than you'd see if their errors were independent given each judge's own failure rate. Read Nogueira and Rao–Callison-Burch together and they measure the same thing from two sides: Nogueira is the *delta* architecture diversity buys (rung 2, positive but partial); Rao–Callison-Burch is the *residual* co-failure left over *after* you have changed architecture all the way to a non-LLM (rung 3, large). Ceiling and delta, not contradiction. The correlation is not living in the architecture.

**Rung 3 — the co-failure lives deeper, in shared conventions.** The rungs nest for a reason: brand ⊂ architecture ⊂ convention, because each names a strictly *larger* set of shared causes a judge inherits — a shared brand is a subset of shared architecture, which is a subset of shared training conventions — so independence bought at a shallower rung cannot dissolve a common cause that lives at a deeper one. If the co-failure survives a change of brand *and* a change of architecture down to a non-LLM classifier, the common cause has to be something all of them share regardless of how they're built: the *scoring conventions* they learned. Annotation norms, rubric lineage, the labeling conventions baked into training data — the shared idea of "what a good answer looks like." That is the hidden common cause the ladder points at. Be precise about the epistemics here: this is a hypothesis, not a demonstrated mechanism. The evidence is *consistent with* shared conventions driving co-failure — the co-failure persists exactly where you'd expect if conventions were the culprit — but no one has run the ablation that would prove it. You could: vary the conventions, hold everything else fixed, watch the correlation move. Until someone does, treat rung 3 as the best-supported explanation on offer, not a settled fact. ("Shared conventions" is my framing of the mechanism, not a claim Rao & Callison-Burch make in those words.)

The ladder is the whole argument in one picture. Diversity is a real cure, bought on the right axis. Brand is the wrong axis. Architecture is a better axis that still doesn't reach bottom. The bottom is convention, and that's where a panel is most likely to be secretly one worldview wearing nine name tags.

That correlated-judge failure shows up at pipeline scale too, outside eval panels entirely. Two frontier labs — Anthropic and Meta — ran cyber-safety evaluations through the same third-party vendor, Irregular, and both failed through one shared misconfiguration. Two labs, one common cause, correlated failure — the panel problem at the level of an entire safety pipeline.

## Why judges *might* correlate by construction — the mechanism behind rung 3

The reason this isn't a bug you route around by shopping vendors: the correlation is structural. This section is the mechanism story for rung 3 — where the shared-latent, shared-confounder language of representation learning turns out to be another name for the "shared conventions" the ladder points at.

Start with a corroborating observation from outside eval panels, because it isolates the "before the task started" part of the claim. In August 2026 Anthropic published "Patterns and Problems in Emerging Multiagent Systems" (Zou et al., anthropic.com/research/multiagent-systems, 2026-08-13), documenting what they call low-variance or systemic failures across agent populations. Eighteen of thirty agents, asked to name a git branch, chose the *exact same* name. Pricing agents converged to the penny — and kept converging even after the authors removed all communication between them. No messages passed. They still agreed. That last detail is the whole point: when agents converge with the channel cut, the correlation was already inside them, baked in before the task started by the thing they have in common. The report describes this vividly and never once puts a number on it — no effective-sample-size figure, no correlation coefficient. Anthropic saw the phenomenon and reached for the vocabulary ("systemic," "low variance"); the instrument to quantify it — n_eff — wasn't in the drawer. That instrument is exactly what this piece is about.

There's a result from representation learning worth knowing here — the Platonic Representation Hypothesis (Huh et al., arXiv 2405.07987). Its claim is that as models get larger and more capable, their internal representations *converge* — different architectures, different training runs, different labs, drifting toward the same latent geometry. I want to be precise about what that paper does and does not say, because it's easy to overreach: it's about representational convergence, and it is silent on correlated *errors*. It does not measure judge co-failure. What it gives me is a candidate mechanism for rung 3 — why judges would share a latent view of the world in the first place, regardless of brand or architecture. Read alongside the ladder, "shared latent" is the representation-learning name for "shared convention." Keep in mind this remains the rung-3 hypothesis: a plausible mechanism, not a proven one.

The step from "shared latent" to "correlated errors" is my reasoning, not theirs, so take it as reasoning: if two judges have converged onto nearly the same internal representation of "what a good answer looks like," then the inputs that fool one will tend to fool the other, because they're reading the item through the same lens. Shared representation is a shared attack surface.

There's direct evidence that the shared component is real and separable, not just a story I'm telling — and it is another rung-3 candidate. CARE (Zhao et al., arXiv 2603.00039) models judge scores as a shared quality factor *Q* plus latent confounders — verbosity, style, training artifacts — via a sparse-plus-low-rank precision decomposition, pulling the confounders apart from genuine quality *label-free*, and reports up to 26.8% aggregation-error reduction on UltraFeedback. That's the shared-convention idea made measurable: judges share confounders, and you can peel them off without ground truth. One honest limit — its identifiability leans on distinct eigenvalues and orthogonal loadings, so it doesn't separate *all* confounders, only the ones that geometry can pry apart. And CARE demonstrates that a shared component *exists and is separable*; it does not prove that shared conventions are *the* driver of judge co-failure. That step is still rung 3's open hypothesis.

This is what the ladder was diagnosing. If the driver of correlation were *identity* — same company, same weights — then buying across vendors (rung 1) would fix it. But if the driver is a shared *framework* — comparable training data at web scale, convergent objectives, a common latent — then vendor is only a proxy for the mechanism, and a leaky one, which is exactly why rung 1 buys ≈ nothing. You can buy nine different logos and still be buying one worldview nine times.

## The honest number

I said "about two." Let me show you why I trust that, and be careful about *how* I'm trusting it, because the fast way to be wrong here is to chain three different measurements as if they were one.

Three groups, three different instruments, land in the same neighborhood:

- **Kohli (arXiv 2605.29800, Apple ML):** effective sample size **2.18** for nine frontier LLM judges — Kohli's 2.18, the number I opened with. It's a Kish-style effective-n computed on the judges' error correlation.
- **Vega-Barbas (arXiv 2608.00285):** effective-diversity number (Vendi / Hill-q1) **≈1.69** for sixteen LLMs. Different estimand, different math, batch setting.
- **Noonan (arXiv 2608.21262):** And there's a related but distinct penalty at the decision boundary. Noonan's Exceedance Design Effect shows that when you care about a pass/fail cutoff on a *score* — not the vote-agreement effective-n above, a different object — the effective sample size at that tail is lower still. Different estimand, same direction: redundancy is worse exactly where a threshold decision is made.

These are not the same quantity and I'm not going to pretend they are. Kish-on-agreement, a Vendi diversity number, and Noonan's score-threshold design effect are genuinely different quantities. The point is the *convergence*: three operationalizations, built by different people for different reasons, all say your double-digit panel is behaving like a low-single-digit one. When independent instruments agree, I believe the neighborhood even when I'd argue about the street address. Call it 2, maybe a shade under, and lower at the threshold.

## Three quantities nobody names cleanly

Here's a distinction I keep having to redraw in conversations, because collapsing it is how people talk past each other.

**The ceiling.** Given a fixed pairwise correlation ρ among your judges, adding more judges doesn't buy unbounded independence. Effective sample size saturates at 1/ρ. Twenty judges at ρ = 0.5 don't give you twenty, or even ten — they give you about two, and the twenty-first buys essentially nothing. The field now has a name for this saturation: the "Correlation Ceiling" (Bay & Yearick, arXiv 2606.28661). Guard: their setting is *within-model self-consistency* on GSM8K and MATH — one model resampled — not a cross-judge panel. So I cite them for the *concept* of the ceiling, not as a measurement of panel co-failure. The math of saturation is general; their experiment is a different object.

**The operating point.** Where you actually sit today: n_eff = n / (1 + (n−1)ρ). This is the standard Kish design-effect formula — it's not owned by anyone, don't let anyone attach a name to it. Plug in your n and your measured ρ and you get the honest count of judges you're paying for versus receiving.

**The drift monitor.** Whether that operating point is *silently sliding* over time. Vendors push new checkpoints. Your rubric evolves. The mix of items you're judging shifts. Any of these can quietly raise ρ and drop your effective-n, and a static measurement taken at deployment won't catch it. Watching that requires a sequential test that stays valid no matter when you look — more on that below.

The field named the ceiling. It computes the operating point when asked. Nobody is monitoring the drift.

## Why the vendor-diversity buy fails: the ladder pays off

Everything so far — the collapse to two, the ladder, the mechanism — comes to a head in one practical verdict: *this is why buying diversity along the vendor axis fails.* Rung 1 is the wrong axis, rung 2 is a better axis that still doesn't reach bottom, and the reason both fall short has a forty-year-old name from software safety, not machine learning.

In 1986, Knight and Leveson (IEEE TSE) ran the experiment everyone building redundant systems should know. They had twenty-seven programs written *independently* — different programmers, no communication, the textbook conditions for independent failures — and then tested whether the programs' failures were actually independent. They weren't. The programs co-failed on the same inputs far more than independence predicted. The teams hadn't colluded. They'd shared something more insidious than collusion: a *specification*. The same problem statement steered independent minds into the same corners.

That is rung 3, in 1986 clothing. The specification is the 1986 *analogue* of the shared convention — with one disanalogy worth stating plainly: Knight–Leveson's spec was a human-written formal document handed to every team, while a shared training convention is an emergent norm distilled from web-scale data. Not the same kind of object, even if they play the same role in the argument. Your judges didn't collude, and — as the ladder showed — they don't even need to share a vendor or an architecture to co-fail. They share a rubric and a training objective, and those would plausibly play the role the specification played in 1986: the common cause that independent *construction* doesn't dissolve, because it lives below construction.

Now the honest caveat, because this is exactly the place I could overclaim, and it is the same caveat that pins rung 3 to hypothesis rather than fact: I do **not** have evidence that the rubric *is* the common cause. That's a hypothesis, an untested lever. It's plausible and it's instrumentable — you could vary the rubric and watch ρ move — but nobody has done that experiment cleanly, so I'm flagging it as something worth building an instrument for, not something I can assert. Knight–Leveson is an *analogue* that motivates rung 3; it is not a measurement of it. And rung 2 (Nogueira's 0.43 vs 0.30 above) already told us architecture diversity is real but partial — so the correct reading is the ladder's: diversify across vendors and architectures, yes, but don't book the full independence benefit, because you're getting less than half of it, and the rest is stuck at rung 3.

## When correlation actually helps — the scoped concession

I owe you the other side, because "correlation is always bad" is false and you'd be right to distrust anyone who says it. There are two genuinely different ways the correlation stops hurting you, and it's worth being precise about both — including one framing mistake I want to head off.

Start with the case where the shared component is *noise*, not bias. If you are doing offline A/B comparison — model A versus model B, same judges scoring both — and each judge's error is *unbiased noise*, then correlation across judges is close to harmless. Noise averages out. You're taking a difference, and shared zero-mean wobble largely cancels in the difference. TensorZero has made a version of this argument and it's correct in that scope. If that's your entire use case, you can file this article under "interesting, not urgent."

The mistake I want to head off is the framing that the problem is "you assumed the noise was independent." That's not the problem. The problem is that you never modeled the *joint* distribution of the judges' verdicts on the *same item* at all. Independence was never a modeling assumption you made and could relax — it was a silent default in the arithmetic of averaging. And it stops being harmless the moment the shared component is *bias*, not noise, and the moment you're doing live gatekeeping rather than a symmetric comparison. On a hard item where the training distribution nudges every judge the same wrong way, averaging nine correlated wrong answers gives you a very confident wrong answer. The panel's agreement reads as certainty. It's actually just shared blind spots, voting. So the thesis is scoped: systematic shared bias, on hard items, in a gatekeeping decision. That's the regime. Inside it, the deficit is real.

The second case is the voting regime. Kaniovski and Zaigraev (Theory and Decision 71:439–459, 2011) worked out the jury case exactly. Above a super-majority quota, *positive* correlation among jurors can *increase* the panel's verdict accuracy. The sign of the effect flips with the decision rule. So there are voting regimes where your judges agreeing is a feature.

Two things keep this from being an endorsement of correlated panels. First, even in the best case they analyze — unanimity — a single competent juror beats the whole correlated panel. So we're talking about the sign of a marginal effect, not a reason to prefer the crowd. Second, and this is the operational sting: the benefit shows up under strict quotas, and the deficit is *worst* under simple majority vote — which is exactly what practitioners actually deploy. The regime where correlation helps is not the regime you're running.

And if the shared signal is reliably *right* — this is the Ross/Lo point (arXiv 2609.04373) — then judges agreeing is efficiency, not fragility. Conceded, fully. That's why the thesis is scoped to the miscalibrated-on-hard-items regime. When the panel is right, its agreement is free money. The problem is that agreement looks identical whether the panel is right or collectively fooled, and you can't tell which from the agreement alone.

## Production is a diversity amplifier in reverse

There's a gap between where you measure n_eff and where it bites, and it runs in the
direction that flatters you. You validate a panel the way everyone validates a panel: in
free-form chat, judges writing out verdicts in prose. You *deploy* it behind a structured
JSON API, because that's how software consumes a model — a schema, a field to fill, nothing
else. Those are not the same surface, and the switch is not cosmetic. Structured output
measurably collapses the diversity of what a model will say.

Tapan Parikh measured exactly this collapse ("Structured Output Collapses Answer Diversity
Across 44 Language Models," arXiv 2607.18476, 2026). On a simple "pick a word" task, moving
from free-form chat to a plain *"reply with JSON only"* instruction pushed the modal-answer
rate from 41% to 64% (p = 0.0002) and cut the number of distinct answers from 52 to 36.
Field-mean answer-choice surprisal fell from 1.80 bits to 1.58 bits — a 0.22-bit loss of
diversity. XML gave a similar effect (p = 0.002). And this is the lower bound on the
mechanism, not the upper: no schema enforcement and no constrained decoding were used. Just
the *instruction* to answer in JSON was enough to homogenize the models. Add grammar-constrained
decoding on top and you would expect the collapse to deepen, not ease.

Parikh draws the deployment conclusion himself, and I'll quote him because the bridge is his,
not mine: "structured output is how software consumes language models; that surface is served
by a measurably more homogeneous model than the chat surface on which models are evaluated,
compared, and chosen." You evaluate the chatty model and ship the homogeneous one.

Now the step that is *mine*, flagged as such because it is the load-bearing inference of this
whole section. Parikh measures answer-choice diversity on open-ended *naming* tasks. He does
**not** measure judge agreement, judge error-correlation, or n_eff on anything. The bridge from
"structured output lowers lexical diversity" to "structured output raises judge *error*
correlation and lowers n_eff on evaluation tasks" is my inference — it is not a measurement, and
Parikh's numbers do not demonstrate it. It is plausible on the mechanism this article has been
building: if two judges have converged onto nearly the same latent view of a good answer, and you
then narrow the channel they answer through — fewer distinct responses admissible, the modal
response more dominant — you are stripping out exactly the idiosyncratic variation that let their
errors *not* coincide. A narrower output surface is a smaller space in which to disagree. But
plausible is not proven. Nobody has run the panel: same judges, same items, measure φ̄ in chat
and again under the deployment schema. Until someone does, treat this as a directional claim —
production n_eff ≤ benchmark n_eff — not a figure.

And do not reach for arithmetic to close the gap. Parikh's 0.22-bit surprisal drop is a lexical
diversity measurement on a naming task; Kohli's n_eff ≈ 2.18 is a Kish effective-n on judge error
correlation. They are different estimands from different studies, and multiplying or chaining them
would manufacture a number neither study supports. The honest statement has no product in it: the
n_eff you measured in chat is an *over*-estimate of the n_eff you're running in production, and you
don't know by how much.

The practical takeaway is a one-line fix to the recipe later in this piece: **measure n_eff under
your deployment format.** Same JSON schema, same temperature, same decoding settings, same
constrained-generation backend — not in the chat playground where the model is at its most
diverse. The playground gives you the panel's best face. Your users get the other one.

## Three objections I have to meet head-on

**"More agents is all you need."** There's a well-known result (arXiv 2402.05120) that resampling *one* model many times and voting gives you real gains. True — and not a counterexample. Resampling one model draws near-i.i.d. samples *by construction*; the independence is manufactured by the sampling process. Cross-*model* panels are the opposite case: they don't get that independence, precisely because the models share the training specification the resampling trick doesn't have to worry about. Same voting math, opposite independence structure. The i.i.d. case is the one where the panel really is nine; the cross-model case is the one where it's two.

**"The market will differentiate the judges for you."** Competition should push producers to differentiate — Raghavan (arXiv 2412.08610) is the reference for that dynamic. But a judge panel is a *single-buyer* market. One team picks all nine judges. The differentiation incentive fires when many buyers pull producers in many directions; when a single buyer assembles the panel, nothing forces the members apart, and the shared-specification pull wins by default. The market can't decorrelate a panel one person shopped for.

**"Then skip the panel — just use one calibrated decision model."** This one deserves a fair hearing before it gets answered, because the strongest version of the objection is actually correct on one point.

The argument runs like this. If your nine judges collapse to two effective votes, you're already halfway to being one. If a single, well-calibrated decision model is more accurate than two noisy, correlated judges, you haven't lost anything — you've gained. The panel was supposed to be safer than a single judge; if it's functionally *two* judges, and those two judges are both noisier than your best single model, you're paying a reliability tax for safety you aren't receiving. On raw average accuracy, a single capable model may genuinely beat a panel with n_eff ≈ 2. Concede it: for a point verdict on a task you've validated, one strong well-calibrated model is *defensible*.

What the objection misses is what a jury is *for*.

A single decision model has n_eff = 1 not because it is weak but because there is exactly one error process and therefore zero observable disagreement. It hands you a verdict and nothing else. A panel hands you a verdict *and* a dissent rate — a running, observable signal of when the verdict is shaky. Calibration tells you whether a judge's confidence tracks its accuracy in aggregate; it cannot tell you whether *this* particular answer is one of the ones where it's wrong. Disagreement among judges can. When half the panel dissents, you know you're in contested territory even before you check the ground truth — and you have no ground truth at inference time. A single model gives you a confidence score that is calibrated on average but says nothing about the cases where every calibrated model would agree and all of them would be wrong. That's the shared blind spot problem the whole article is about, and calibration doesn't address it.

The real choice is between two different things you might want from a verdict system. One is the accuracy of the point estimate — the expected fraction of items the system gets right. The other is observability of reliability — whether you can see, in real time, when the verdict is untrustworthy. A single strong model can win on the first axis. Only a panel with n_eff > 1 gives you the second. If all you want is a point verdict and you fully trust your calibration across the whole item distribution, one model is defensible. If you need to know when to withhold the verdict — which is the entire premise of running a jury — then a panel, even a low-n_eff one, gives you something a single model structurally cannot: the disagreement signal. And raising n_eff (by decorrelating the judges, not by buying more vendors) is what buys you more of that signal.

One scope note, because the gauge has limits: as the article discusses later, n_eff tracks bulk co-failure — the shared variance of the panel's average — and is blind to the tail event where the whole panel fails together. So the disagreement signal is partial, not a guarantee. But a single model eliminates it entirely. That's the operative comparison.

## What's already known, and what isn't

I should say plainly what part of this is new, because most of it isn't. Correlated experts are a thirty-year-old problem, and three results — one historical, one from ensemble learning, one from forecasting — bound the thesis from three directions. Each answers a different objection, and together they draw the line between the prior art and the one thing I'm claiming is mine.

**"Someone must have solved correlated experts already."** They did — in 1991. Roger Cooke's *Experts in Uncertainty* scores each expert on calibration (a p-value against known-answer seed questions) times informativeness, then weights a linear pool by that score; correlated experts get downweighted implicitly, through poor calibration, rather than by any explicit model of their joint failures. The Classical Model has been validated across 45-plus real studies in nuclear safety, climate, and engineering — far deeper empirical backing than anything the LLM-eval field has assembled. So the problem has two classical answers: calibration-weighting (Cooke) and diversity-selection (pick a maximally varied panel up front). What's new here is neither. Cooke scores experts once, on a static set of seed questions; the instrument below monitors a *moving* panel — between-judge co-failure drift, anytime-valid and margins-free, firing when a panel that *was* diverse starts converging. That is a narrow addition on top of Cooke, not a replacement for him: he solved the static weighting problem, and did it well. What he left open is the panel that drifts after you've deployed it.

**"Isn't demanding difficulty-stratification overkill?"** No, and the reason comes from inside ensemble learning, not from me. Wood et al.'s *Unified Theory of Diversity in Ensemble Learning* (2301.03962) proves, in their Theorem 10, that for 0/1 loss there is *no* label-independent diversity term — the benefit a diverse panel delivers is provably dependent on the label distribution. The practical reading: under pass/fail scoring you cannot even *state* whether a diverse panel helps without conditioning on item difficulty. Stratifying by difficulty isn't a methodological nicety I'm adding to be safe; it's a precondition for the benefit being defined at all. A high-citation ensemble-learning paper reached that conclusion independently, from loss-decomposition theory, before this problem was about LLMs.

**"If the panel is that correlated, just reweight — downweight the redundant judges."** This is the one objection the diagnostic framing exists to answer, and the answer is forced, not chosen. Bates and Granger showed in 1969 that equal weights beat covariance-optimal weights out of sample, because estimation error in the covariance matrix swamps the theoretical gain from optimizing — the forecast-combination puzzle, now fifty-seven years old. The sting for us is structural: the very correlation that n_eff diagnoses is what drives the judges' covariance matrix toward singularity, and a near-singular matrix is exactly what makes its inverse — the optimal weights — wild and high-variance. So n_eff-based reweighting inherits the instability it's trying to fix. That is precisely why n_eff is sold here as a *diagnostic*, not a corrector: a 1969 result forces it. When the diagnostic fires, the honest move is to change the panel design — add genuine diversity at the right axis — not to post-hoc reweight your way out. The modesty isn't a hedge; it's a theorem.

## The missing instrument — and how to read it

So n_eff is not a cure and not a knob. Bates and Granger took reweighting off the table; the ladder took vendor-shopping off it. What's left is the one thing the field has somehow skipped: the *measurement itself.*

Notice how complete the convergence is on the diagnosis. The practitioner blogs, the eval platforms, the postmortems all say the same sentence now — *your LLM judges aren't independent, correlated judges are one judge billed N times.* The problem is named, out loud, everywhere. What nobody ships is the gauge. There is no column on anyone's dashboard that reads out how independent the panel actually is. The field has fully articulated the disease and built no thermometer. That gap is the whole opportunity, and it's smaller than it sounds — n_eff is a few lines of arithmetic, not a research program.

But a gauge is only honest if you read the right pair of numbers off it. The single most important rule here: **report n_eff and the panel's accuracy together, never n_eff alone.** Call them (p, φ̄) — *p* is how well the panel actually performs (accuracy, or agreement with your held-out labels), *φ̄* is the mean pairwise co-failure correlation that drives n_eff. Either number without the other hides the story, and in opposite directions. A panel with high *p* and low n_eff is a correlated panel that happens to be *right* — fine today, fragile the day the shared bias points the wrong way (this is the Ross/Lo case: shared signal, not shared blind spot). A panel with low *p* and low n_eff is the genuine failure: it's wrong *and* it has no independent read left to catch itself. Same n_eff, completely different risk. Report the co-failure number stripped of the accuracy and you can't tell a healthy panel from a doomed one; report the accuracy stripped of the co-failure and you're back to trusting consensus as certainty — the exact trap this piece opened on.

Which is why n_eff belongs on the dashboard as a quantity you *track over time*, not a one-time verdict. It's a drift gauge you watch, not a knob you turn. A panel that was genuinely diverse at deployment can quietly converge — a vendor ships a new checkpoint, two of your judges drift onto the same base model — and that erosion of independence is exactly what a single static accuracy snapshot will not show you. The needle creeping toward 1/φ̄ is the thing worth watching; it's the only read on the dashboard that answers *are these still separate opinions?* rather than *were they right this week?*

One honest caveat, because the gauge is not an oracle. n_eff is built from φ̄, the *average* pairwise co-failure — so it tracks bulk correlation and is blind to tail co-failure, the rare all-judges-wrong event that does the most damage. Two panels can share the same n_eff while their probability of failing *together* differs by orders of magnitude. So n_eff can sit flat while the joint-failure risk that actually tanks your accuracy climbs underneath it, and it carries no promise of moving before *p* does. Watch it for drift; do not read a steady n_eff as proof the panel is safe. It's one gauge on the dashboard, next to accuracy — not a substitute for it.

## The estimator that fills the hole

So how do you measure co-failure when you have no ground-truth labels — which, live, you almost never do? This is the monitor I've been building, and I'll keep it high-level: it's research-stage, not a shipped product.

The core trick is to pair judges' verdicts *across different items*. Two different items are independent by construction — whatever the panel's shared bias is, it can't correlate a verdict on item 5 with a verdict on item 200 the way it correlates two verdicts on item 5. So cross-item pairing gives you a *label-free, margins-free* baseline: the co-agreement you'd expect if the judges were independent, estimated without ever needing to know the right answer. Then you compare the same-item agreement against that baseline. Excess same-item agreement over the cross-item baseline is your co-failure signal.

This also sidesteps a confound that sinks the naive approach. Jo, Garg & Raghavan ("The Subjectivity of Monoculture", arXiv 2602.24086) show that item-exchangeable independence nulls — the p₁·p₂ product baseline — overstate correlation, because item *difficulty* induces agreement on its own: everyone gets the easy ones right and the hard ones wrong, and that shared response to difficulty looks like co-failure even under genuine independence. The objection applies here too: an error correlation measured across items still absorbs shared difficulty, so the raw φ̄ isn't a clean measure of genuine co-failure. But the construction handles this in the safe direction: difficulty *inflates* raw φ̄, so the n_eff computed from it *understates* how many independent judges you have rather than overstating it — the monoculture claim is conservative with respect to the difficulty objection, not manufactured by it. The residual co-failure that survives conditioning on the item is what a rigorous monoculture claim ultimately rests on; the raw φ̄ is an upper bound on that, and the n_eff from it errs on the cautious side. Which *kind* of effective-number you compute is a separate question, though, and there the arrow can reverse (see the worked example below).

One competitor I have to name, because I'm not the only one measuring judge correlation without labels. Sunkavalli (arXiv 2609.08826) gives a closed-form, *reference-free* estimator of judge error-correlation under a single-common-factor model. It's real prior art and I'll name the differences precisely, because the differences are the whole moat: (a) Sunkavalli needs a *second anchor-evaluator panel* — at least two judges *and* at least two anchor evaluators — where the approach here works from a single judge panel's own outputs; (b) it's batch, one-shot, where this is anytime-valid and sequential; (c) it pools covariances within the item set, with no cross-item pairing. Different information requirement, different validity regime, different estimator. But same honest goal, and worth knowing about.

Run the cross-item test as an *anytime-valid sequential test* — an e-process — and you get the drift monitor from three sections ago. Anytime-valid means you can watch the statistic continuously and stop or alarm whenever it crosses, without inflating your error rate by peeking. No fixed sample size, no p-hacking your stopping time. That's the property you need for a monitor that runs forever against a stream of judgments and a vendor that ships a new checkpoint on a Tuesday. The shape is what I'm confident about, and the shape is enough to build on.

One scope stake in the ground: this monitor assumes *non-interacting parallel panels* — judges scoring independently, votes pooled after. If your architecture is a *debate* — judges arguing across rounds, seeing each other's reasoning — you're in a different and worse regime, and this instrument's independence baseline doesn't apply. Ma et al. ("Judging with Many Minds", arXiv 2505.19477) show that debate sharply amplifies bias after the *first* round and sustains it thereafter — across position, verbosity, bandwagon, and chain-of-thought biases — while parallel meta-judge pools stay comparable to a single judge. I want to be careful about what that does and doesn't license: they compute no effective-sample-size and no correlation coefficient, so I can't tell you debate drives n_eff below anything. What they show is directional and it's enough for a design rule: interaction amplifies the shared bias rather than diluting it. Keep the panel parallel.

## Compute it yourself

I've been telling you to measure a number. Before I show you the code, here's the same computation done by hand — because doing it on a toy panel first makes the real-data version much easier to trust.

### By hand: a 5-judge × 6-item panel

You ran 5 LLM judges over 6 test items. It feels like 5 opinions. Here's how to find out how many it is.

Score each judge on each item: **1 = got it wrong**, **0 = got it right**. Each judge misses exactly 2 of the 6 items, so no single judge is worse than another; the only thing that varies is *who misses what*.

| Item | J1 | J2 | J3 | J4 | J5 |
|------|----|----|----|----|----|
| A    | 1  | 1  | 1  | 1  | 1  |
| B    | 1  | 1  | 0  | 0  | 0  |
| C    | 0  | 0  | 1  | 0  | 0  |
| D    | 0  | 0  | 0  | 1  | 0  |
| E    | 0  | 0  | 0  | 0  | 1  |
| **errors** | 2 | 2 | 2 | 2 | 2 |

(Item F is all-zeros — everyone got it right.) Notice everybody trips on item A, and J1 and J2 are carbon copies of each other. That's correlation, and it's about to cost us.

**Step 1 — pairwise φ.** For two 0/1 columns, φ is Pearson's correlation. With equal error rate *p* = 2/6 = 1/3, p(1−p) = 2/9, p² = 1/9.

- **J1 & J2** miss the *same* 2 items (A, B). Both-wrong fraction = 2/6. φ = (2/6 − 1/9)/(2/9) = **1**. Perfectly redundant.
- **Every other pair** shares exactly 1 item (A). φ = (1/6 − 1/9)/(2/9) = **0.25**.

There are 10 pairs total: 9 at φ = 0.25, one twin pair at φ = 1.

**Step 2 — average and plug into Kish.**

φ̄ = (9 × 0.25 + 1 × 1.0) / 10 = 3.25/10 = **0.325**

n_eff = k / (1 + (k−1)·φ̄) = 5 / (1 + 4 × 0.325) = 5/2.3 ≈ **2.17**

Five judges. Two and a bit independent opinions. The twin pair alone erased almost a whole vote, and the mild shared tendency to miss item A ate most of the rest.

The 2.17 here is pure arithmetic — it is what the formula returns on this fabricated five-judge table, chosen so the steps are checkable by hand. It is not Kohli's 2.18. That the two land a hundredth apart is coincidence: one is the output of a toy I built to show the mechanics, the other is a field measurement on a real nine-judge panel. The toy demonstrates how the number is computed; Kohli's 2.18 is independent evidence that real panels actually sit down there. Don't read the match as confirmation — read it as two unrelated things that happen to rhyme.

**Which "2"? And why it's the optimistic number.**

It's worth being precise about what "two effective votes" means, because there are two different effective-sample-size calculations hiding behind the same symbol, and they stop agreeing the moment your judges aren't all correlated to the same degree.

The number I computed — n_eff = N / [1 + (N−1)·φ̄] with the *average* pairwise co-failure φ̄ — is exact for one specific quantity: the variance of the panel's *average* score. That's a theorem, not an approximation. When you average judges with equal weight, only the mean pairwise correlation enters the variance, so heterogeneity across judge pairs doesn't change the answer at all (Kish, *Survey Sampling*, 1965, §8.2).

But "variance of the average" is the *friendliest* way to pose the question. If you instead ask how many *spectrally independent* judges you have — the participation-ratio count (Σλ)²/Σλ² of the correlation matrix, the same "effective number" used for portfolio diversification (Meucci, 2009) and for spatial degrees of freedom in climate fields — then heterogeneity works against you. Among all correlation matrices with a fixed *average* correlation, the one where every pair is *equally* correlated has the *most* spectral independence; any real panel, where some judge pairs run tighter than others, has less. (The one-liner: that count equals N² / (N + Σ ρ_ij²), and for a fixed mean the sum of squared correlations is smallest exactly when all the correlations are equal.)

So "two effective votes" is the optimistic reading. Measure independence the way a risk model or a tail-failure analysis would — on a panel whose judges don't all resemble each other to the same degree — and you get *fewer*, not more. That cuts the opposite way from how these numbers usually get waved around: nobody is accidentally *under*-counting their independence.

### Why not κ

Before moving to the real-data version: the natural instinct is to reach for Cohen's κ instead of φ. Here's exactly why that's wrong.

In the toy above, with perfectly balanced error rates, κ and φ happen to coincide (both = 0.25 for the typical pair — you can verify: p₀ = 4/6, pₑ = (1/3)²+(2/3)² = 5/9, κ = (4/6 − 5/9)/(1 − 5/9) = 1/4). So a balanced toy doesn't reveal the trap. Change the balance and it does.

Two judges, 6 items, *unequal* error rates: Judge X errs on 4 items {A, B, C, D}; Judge Y errs on 2 {A, B}; overlap = 2 (both wrong on A and B).

- **φ** = (ad − bc) / √((a+b)(c+d)(a+c)(b+d)) = (2·2 − 2·0) / √(4·2·4·2) = 4/8 = **0.50**.
- **κ**: p₀ = (2+2)/6 = 2/3, pₑ = (⅔·⅓) + (⅓·⅔) = 4/9, κ = (2/3 − 4/9)/(1 − 4/9) = **0.40**.

Same six items, same data — **φ = 0.50 but κ = 0.40**, because the marginals differ (4/6 vs 2/6). They're linked by κ = q·φ (Rao & Callison-Burch, arXiv 2606.00093), where q depends on the judges' error rates. The Kish formula wants φ. Plug κ in and your n_eff is wrong.

The 3-line takeaway: (1) For every pair, compute how often they err *together* beyond chance — that's φ. Average over all pairs → φ̄. (2) n_eff = k / (1 + (k−1)·φ̄). (3) For k = 9 judges with φ̄ ≈ 0.5: n_eff = 9 / (1 + 8·0.5) = 9/5 ≈ **1.8**. Nine judges, worth less than two.

That's the toy. Here's the same computation on real data — and the code that runs it at scale.

---

I've been telling you to measure a number. Here's how, with no dependency on my research-stage monitor — just your judge-score matrix and fifteen lines of numpy. There are two formulas, and naming both up front kills the "which one?" objection, because they answer different questions at different times.

**ESDOF / participation ratio — the design-time screen.** Before you commit to a panel, you want to know how many independent opinions its correlation structure can *possibly* deliver. Compute both of these on the judges' *errors*, not their raw scores — and the reason is identifiability, not mere consistency with the Kish formula. ESDOF on raw scores is just a reparametrisation of signal-to-noise, (v + τ²)/σ²: a panel of *perfect* judges — who all score every item correctly — would register ESDOF_raw = 1, maximal apparent agreement, exactly when the panel is best. A reliability statistic that is minimised by perfect judges is measuring the wrong thing. On errors the statistic is identifiable: perfect judges have zero error variance and the co-failure structure is undefined, not spuriously high. So: errors. Take the judge × judge *error* correlation matrix (the same error matrix `E` as the Kish check below), get its eigenvalues, and compute

    spectral_dimension = (Σ λ_i)² / Σ λ_i²

the ratio of the squared sum of eigenvalues to the sum of squared eigenvalues. This is the Hill q=2 number. It's not new — it's the effective-degrees-of-freedom formula from Bretherton et al. 1999 (*J. Climate*), operational at ECMWF for decades. It needs only the correlation matrix, which makes it the right pre-hoc screen: you can run it on a pilot before you've collected per-item labels. One caution: ESDOF is a participation-ratio statistic with ceiling 1/φ̄² ≈ 4.23, *not* on the same scale as the Kish n_eff (ceiling 1/φ̄ ≈ 2.06) — don't compare the two numbers directly or report ESDOF *as* n_eff; they answer different questions.

A design rule falls out of this. Since the cap is the item, not the judges, and a judge main effect barely registers, the marginal judge buys very little once you are near the ceiling. At a *fixed judgment budget* — a fixed total number of judge-item gradings you can afford — the better spend is fewer judges on more items rather than more judges on fewer items: extra judges on the same items are re-reading an item whose difficulty already determines the outcome, while extra items buy you genuinely new information. You can put numbers on it once you have φ̄. The equicorrelation error variance of a panel mean of size J is proportional to φ̄ + (1−φ̄)/J, so shrinking the panel from the measured baseline of thirty-two judges costs, at φ̄ = 0.486: cutting to 9 judges costs +8.2% error variance, to 5 costs +17.3%, to 2 costs +48.0%. (These compare each smaller panel against the real J = 32 baseline; a trade-off ratio between two sizes depends only on the two sizes and φ̄, never on the baseline.) Concretely, and importantly: the 9-to-2 trade-off — dropping from nine judges to two — costs +36.8% error variance, and that figure is invariant to the true panel size. The ratio v(a)/v(b) = [(1+(a−1)φ̄)/a] / [(1+(b−1)φ̄)/b] contains only a, b, and φ̄; the actual J does not appear. So the baseline-free trade-off survived the J = 32 correction untouched — only statements that named a single panel size were ever wrong.

**Kish — the validation-time check.** Once the panel is live and you have per-item judge agreement data, compute the mean pairwise co-failure correlation φ̄ across your items — but correlate the judges' *errors* (1 if a judge is wrong on an item, 0 if right), not their raw scores. To make this concrete I ran it on a separate empirical panel — not Kohli's nine-judge opening example but **ChaosNLI alphaNLI (995 items, 32 LLM judges)**. On that panel, correlating raw label indices gives n_eff ≈ 1.2 — lower, because raw scores co-move whenever both judges happen to pick the same answer, right or wrong. The error-based version gives ≈ 1.99 (φ̄ ≈ 0.486, so the Kish ceiling 1/φ̄ ≈ 2.06 is already 96.8% spent at thirty-two judges), and that is the number that matters for shared blind spots. Two judges that both correctly rate a good answer highly are shared *signal*, not a shared blind spot; only correlated *error* is co-failure. What caps the panel is the item, not the judges: judges fail together because hard items are hard — everyone finds the hard items hard — and a direct measurement of the judge-specific main effect finds it accounts for at most 2% of the item (difficulty) variance. The low n_eff is not the judges being redundant copies of each other; it is correlated *bias*, a shared response to difficulty. This φ̄ (the mean off-diagonal pairwise correlation) plays the role of ρ in the design-effect formula above. Plug it into the design-effect formula from the last section:

    n_eff = n / (1 + (n−1)·φ̄)

This is post-hoc panel validation: it uses the disagreement you actually observed rather than the correlation matrix's eigenstructure. ESDOF screens a design; Kish audits a deployment.

Both take a judge-error matrix `E` of shape (items × judges):

```python
import numpy as np

# E[i, j] = judge j's ERROR on item i:  1 if judge j is wrong on item i, else 0.
# Correlate errors, not raw scores. (If you have graded scores rather than
# right/wrong, use the residual: judge's score minus the correct score.)

def spectral_dimension(E):
    # design-time screen: participation ratio of the judge-judge correlation matrix.
    # NOT on the Kish n_eff scale (its ceiling is 1/phi_bar^2, not 1/phi_bar).
    keep = E.std(axis=0) > 0                   # drop judges with no error variance
    if keep.sum() == 0:                        # perfect panel: no error variance
        return float(E.shape[1])              # fully independent; nothing co-fails
    C = np.corrcoef(E[:, keep], rowvar=False)  # judges x judges, on errors
    eig = np.linalg.eigvalsh(C)
    eig = np.clip(eig, 0, None)               # guard tiny negative eigenvalues
    return eig.sum()**2 / np.square(eig).sum()

def n_eff_kish(E):
    # validation-time: Kish design effect from mean pairwise error correlation
    keep = E.std(axis=0) > 0                   # drop judges with no error variance
    if keep.sum() == 0:                        # perfect panel: no error variance
        return float(E.shape[1])              # fully independent; nothing co-fails
    C = np.corrcoef(E[:, keep], rowvar=False)  # judges x judges, on errors
    m = C.shape[0]
    iu = np.triu_indices(m, k=1)
    phi_bar = C[iu].mean()                     # mean off-diagonal pairwise corr
    return m / (1 + (m - 1) * phi_bar)

print("spectral_dimension:", spectral_dimension(E), "  Kish n_eff:", n_eff_kish(E))
```

One honest footnote to this recipe: correlating errors *across items* still absorbs shared item difficulty — everyone tends to miss the same hard items, and that co-movement is counted here as co-failure even under genuine independence. On some panels almost all of the measured φ̄ is difficulty rather than a shared blind spot. Separating the two requires conditioning on the item (comparing each judge's error against what independent judges with the same error rates would produce on *that* item); that is the sharper, harder measurement, and φ̄ here is best read as an upper bound on genuine co-failure.

As far as I can find, no open-source LLM-judge n_eff audit tool exists — the `judges` PyPI package, JudgeLM, and OpenCompass all measure per-judge quality and none of them measure panel independence. The closest precedent is ASSERT-KTH's Knight-Leveson-Redux (github.com/ASSERT-KTH/Knight-Leveson-Redux), which re-runs the 1986 N-version experiment on AI *coding* agents: a million test cases, per-version failure rate, a coincident-failure z-statistic, pairwise φ, a Bonferroni binomial test. Its domain is code generation, not judging, but the methodology transfers directly — swap "program fails a test case" for "judge misgrades an item" and it's the same audit.

## The one column to add

At the top of this piece I asked what column nobody adds to the eval dashboard. Here it is. Every practitioner guide I've read asks: is each judge calibrated? That's the κ question, and it's a good question. None of them ask: are your nine judges actually nine? That's the effective-sample-size question, and it's the one with your money in it.

So add the column. Run the Kish check from "Compute it yourself" on your panel and put n_eff on the same dashboard as your κ. One number. It will, I'd wager, embarrass your headcount.

One measurement note while you're at it. The "Why not κ" worked example above showed the identity κ = q·φ (Rao & Callison-Burch) with concrete numbers; the same point applies at scale. When your pass/fail split is skewed — and gatekeeping splits usually are, most things pass — that q factor drags κ down relative to φ, so κ *understates* the agreement structure you actually have. Report φ, not just κ, or you'll flatter yourself about how independent the panel is.

The thing to sit with: your LLM passes the tests and can still fail the audit. Calibration and independence are different properties, and every guide in the field checks the first and none check the second. You've been auditing whether each judge is honest. You haven't been auditing whether you have as many of them as you're paying for. Add the column.

## For the compliance officer: n_eff as an audit certificate

Everything above is written for the engineer building the panel. There's a second reader who
should care more, and usually hears about this last: the person who has to *document* that the
panel is fit for purpose. If an LLM-judge panel gates a high-risk system, that panel is not a
developer convenience — it is part of the measurement apparatus a regulator now expects you to
describe, and the description currently has a hole in it.

The obligations are concrete. Under the EU AI Act (Regulation (EU) 2024/1689), a provider of a
high-risk system must pass a conformity assessment before placing it on the market (Article 43),
run a quality management system across the lifecycle (Article 17), and operate post-market
monitoring once it ships (Article 72). None of these name a number; all three ask the same thing
of your evaluation pipeline — *show that it measures what you claim it measures, and keep
showing it.* ISO/IEC 42001:2023, the first AI management-system standard, and the NIST AI Risk
Management Framework (NIST AI 100-1, January 2023), with its Govern / Map / Measure / Manage
functions, ask it in different vocabulary but the same spirit: the evaluation that gates risk is
itself a control you have to characterize. And as of 15 October 2026 this has teeth in Europe —
EN 18286:2026, "AI — Quality management system for EU AI Act regulatory purposes," was published
in the OJEU as the first harmonised standard cited under the Act. Be precise about its reach: it
grants a presumption of conformity for the Article 17 QMS requirements only, not for the Act as a
whole. It raises the bar on documenting your quality system; it does not discharge the rest.

Here is where the panel becomes an audit problem. A team writes, truthfully, "quality is gated by
a five-judge LLM panel." On paper that reads as five independent checks — robust, defensible,
exactly the kind of redundancy an assessor likes to see. But if those five judges co-fail, the
effective number of independent checks may be one or two, and the artifact silently overstates
the reliability of the control. The document is not false — there really are five judges — but it
is *uninformative about the thing the assessor cares about*, which is how many genuinely
independent reads the panel performs. Agreement among the five, the number a team is tempted to
report as evidence of rigour, is precisely the number that hides the deficit: on the hard items,
consensus is the symptom, not the proof.

n_eff closes that gap, and it closes it in exactly the register an auditor works in — a single
number you can put on a control and check. It is the honest count of independent checks the panel
actually performs. None of the regimes above *require* you to report it; none of them name it, and
I won't pretend otherwise. What they require is measurement evidence — that your quality control
is characterized, monitored, and not silently degrading — and n_eff is precisely the kind of
evidence they ask for, sitting unmeasured in a place no platform currently instruments.

Report the pair, not the single number. As the dashboard section argued, the auditable artifact is
(p, φ̄) together — how well the panel performs and how correlated its failures are — or the n_eff
the two imply. The worked example earlier in this piece shows the shape of what that looks like: a
five-judge panel whose mean pairwise co-failure φ̄ ≈ 0.325 behaves like n_eff ≈ 2.17 — two and a
bit independent checks, not five. (Treat any specific low figure you might imagine for your own
panel — a five-judge panel landing at n_eff ≈ 1.3, say — as illustrative until you have measured
your own φ̄; the whole point is that the number is computed, not assumed.) An assessor can read
that pair and know what the control is worth. "Five judges" alone tells them nothing, and now that
EN 18286 has made the quality-management documentation load-bearing, "nothing" is a worse place to
be standing than it was a year ago.

The thing to leave with: the drift-monitoring obligation and the audit-certificate framing are the
same instrument pointed at two readers. The engineer watches n_eff to know when the panel is
quietly converging. The compliance officer reports it to show the control is characterized and
still holds. One gauge, one number, two reasons to have built it — and it is, still, the column
nobody adds.
