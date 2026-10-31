# Are Your LLM Juries Actually Independent?

> **⚠ VERIFY-BEFORE-PUBLISH (2026-10-31).** Three claims in this opening are sourced from browse-log snippets, not primary reads. Before this goes to Robin / publication, fetch and confirm: (1) Pebblous report — https://blog.pebblous.ai/report/ai-agent-benchmark-trust/en/ (the 7/8 figure, the "evaluator trusts the entity being evaluated" wording, UC Berkeley affiliation, author); (2) Tamiz Uddin production-gap postmortem on DEV.to (the >23pp gap and sample size — two of Lyra's reading notes conflict: 1,247 agents vs 312 incidents); (3) Hamel Husain guide — https://hamel.dev/blog/posts/llm-judge/index.html (exact date and phrasing before any direct quote). Do NOT chain any of these to Kohli's 2.18.

> New opening draft, 2026-10-31. Covers title through the first introduction of
> n_eff / between-judge correlation. Follows the settled write-order: incident →
> crisis stat → contrarian turn + narrow concession → method as payoff.
>
> TITLE CANDIDATES (audience register — "LLM juries," "meta-evaluation," "Eval Ops"):
> 1. **Are your LLM juries actually independent?** (working)
> 2. **Your LLM jury has fewer members than you think**
> 3. **Meta-evaluation's missing column: how many judges you actually have**
> (Avoid "co-failure," "n_eff," "monoculture" in the title — those are our words, not theirs.)

---

An evaluator is supposed to be the adult in the room. You build a system, you point an
LLM judge at it, and the judge tells you whether the output is any good. The whole
arrangement rests on one assumption that nobody writes down: the judge is more
trustworthy than the thing it's judging.

A 2026 report from Pebblous AI (blog.pebblous.ai) found the arrangement running backwards.
In their audit of gamed benchmarks, Pebblous reported that the evaluator was effectively
trusting the entity being evaluated — and that seven of eight gamed benchmarks sailed
straight past evaluation. [VERIFY: Pebblous report — https://blog.pebblous.ai/report/ai-agent-benchmark-trust/en/ — confirm the 7/8 figure, the "evaluator trusts the entity being evaluated" phrasing, UC Berkeley affiliation, and author before publication.] The judges weren't broken. Each one, on
its own, worked. They failed as a group, in the same direction, on the same inputs — which
is the one failure mode a group is supposed to rule out.

That is the problem in its loud, macro form. It has a quiet form too, and the quiet form
is the one on your dashboard right now.

## The gap between the demo and production

Evaluation setups have a habit of looking excellent until they meet real traffic. One
production postmortem documented a drop of more than 23 percentage points between benchmark
accuracy and live production accuracy (Tamiz Uddin, DEV.to, Sep 2026). The drop isn't
random noise. It's the judges, which looked independent on the clean dev set, discovering
their shared blind spots on the messy distribution production actually sends them.

And here's the trap that makes it hard to catch: when your judges agree, you read it as
confirmation. Nine judges, nine reads, nine chances to catch a bad output — if they all
say "pass," surely it passes. But agreement is *also* exactly what you'd see if the judges
were failing together. Consensus can be the symptom rather than the cure, and nothing on
the surface tells you which one you're looking at.

## The strongest argument against building a jury at all

Before we add judges, we should hear the best case for *not* adding them — and in the
LLM-as-judge space that case has a name. Hamel Husain's guide (hamel.dev, Sep 2026) is the
single most-read practitioner reference on the topic, and his position is blunt: one
carefully calibrated expert judge beats a diverse ensemble, and stacking up multiple judges
with differing standards is a way to manufacture noise, not cancel it. [VERIFY: Hamel's
exact "one calibrated expert" phrasing — read via summary/snippet, not full primary.]

He is right, and I want to concede it precisely, because the concession is narrow and the
narrowness is the whole point.

Husain is right about single-judge calibration. If your judges disagree because they're
each poorly specified — vague rubric, no reference answers, inconsistent standards — then
yes, adding more of them multiplies the mess, and the fix is to calibrate one judge well,
not to convene a committee. On that, no argument.

Where the frame runs out is lineage. Husain's advice has no slot for the question that
this article is about: if you *do* assemble a panel, and every member is drawn from the
same pretraining and RLHF lineage, are N calibrated experts actually N independent
experts? His guide is silent on that — not wrong, silent. It solved calibration and never
asked what happens when the experts share a gene pool.

So the concession is sharp: **vendor diversity is the wrong axis — not "diversity fails."**
The move everyone reaches for — swap GPT for Claude for Gemini, spread the panel across
logos — buys far less independence than it looks like, because the correlation doesn't live
in the brand. It's worth noting that what *does* move the needle isn't vendor-mixing at all:
prompt-level diversity has been found to beat model-level diversity, with model diversity
landing somewhere between the best and worst member without a clear improvement (arXiv
2507.21168). Diversity is a real cure. It's just usually bought on the one axis that happens
to be free of it.

## The one thing none of the tools measure

Here's what's strange. The practitioner field has articulated this problem in its own
language, out loud, repeatedly — and still hasn't shipped a way to measure it.

orq.ai put it as well as anyone: three correlated judges are one judge with three times the
request volume, and above 95% agreement you're not looking at consensus, you're looking at a
red flag — one verdict billed three times. That's the intuition exactly right. It names the
thing. What it doesn't do — what none of the guides, rubrics, or eval platforms do — is give
you an *estimator*: a number you can compute from your own judge scores that says how many
independent judges you actually have.

That open door has a name. It's the **effective number of judges** — how many genuinely
independent votes your panel behaves like, once you account for how often the judges fail
together. The arithmetic is almost embarrassingly small:

    n_eff = 1 / φ̄

where **φ̄** is the mean pairwise *between-judge* correlation — how often two judges are wrong
on the same items, averaged over every pair. Agreement that reflects a shared blind spot
counts against you; agreement on genuinely good answers does not. The moment you measure φ̄,
the folklore becomes a reading on a gauge: orq.ai's "three judges, one verdict" stops being a
cautionary metaphor and becomes a specific claim about a specific panel that you can confirm
or refute.

Every practitioner guide asks the same question: is each judge calibrated? It's a good
question. None of them asks the other one: are your judges actually independent — and if not,
how many of them are you really getting? That's the column this article is about adding.

---

*[Continues into the body of DRAFT-2026-09-11.md: the vendor-diversity "ladder" (rung 1
brand / rung 2 architecture / rung 3 shared conventions), the structural-correlation
mechanism, the honest number (Kohli 2.18 and the convergence of independent instruments),
the scoped concession on when correlation helps, and the by-hand + numpy computation of
n_eff.]*
