# Are Your LLM Juries Actually Independent?

> **✓ VERIFIED (2026-11-01).** Verification pass complete on the three snippet-sourced claims.
> - **tianpan.co war-story** — VERIFIED verbatim (Tian Pan, June 3 2026, https://tianpan.co/blog/2026/06/03/the-llm-judge-ensemble-that-agreed-because-all-judges-were-the-same-family). Now the cold-open. ⚠ BARRED: do NOT convert its 0.83 / 0.64 Krippendorff's α into any n_eff or "≈1.3 effective judges" — α is an agreement coefficient, not φ̄; that conversion is an estimand substitution. Use the war-story qualitatively; introduce n_eff later as the instrument.
> - **Hamel Husain + Shreya Shankar** — VERIFIED (https://hamel.dev/blog/posts/evals-faq/, Sep 18 2026, mod. Sep 21). Attribution corrected to BOTH authors. Framed as the NARROW contrarian: validate judges against human labels (TPR/TNR), silent on lineage correlation. Do NOT imply they argue for lineage independence.
> - **Pebblous AI** — quote VERIFIED but CONTEXT MISMATCH (benchmark gaming/manipulation, not judge-panel independence). DEMOTED to a one-line secondary nod, clearly in its own context. Not the cold-open.
> - Do NOT chain any of these to Kohli's 2.18.

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

That is the problem in the form you'll actually meet it: not a dramatic blowup, but a panel
that looks excellent on every dashboard until someone breaks the family and the agreement
evaporates. (It has a louder, macro cousin — the broader eval-trust crisis, where Pebblous AI's
audit of *gamed benchmarks* concluded the root problem is that "the evaluator trusts the
entity being evaluated" (blog.pebblous.ai, April 2026). Different setting — benchmark
manipulation, not panel independence — but the same shape: the evaluator is not the
independent check it was assumed to be.)

## The gap between the demo and production

Evaluation setups have a habit of looking excellent until they meet real traffic. One
production postmortem documented a drop of more than 23 percentage points between benchmark
accuracy and live production accuracy (Tamiz Uddin, DEV.to, Sep 2026). [VERIFY: Tamiz Uddin
DEV.to postmortem — confirm the >23pp gap and sample size before publication; not yet read
against primary.] The drop isn't
random noise. It's the judges, which looked independent on the clean dev set, discovering
their shared blind spots on the messy distribution production actually sends them.

And here's the trap that makes it hard to catch: when your judges agree, you read it as
confirmation. Nine judges, nine reads, nine chances to catch a bad output — if they all
say "pass," surely it passes. But agreement is *also* exactly what you'd see if the judges
were failing together. Consensus can be the symptom rather than the cure, and nothing on
the surface tells you which one you're looking at.

## The strongest argument against building a jury at all

Before we add judges, we should hear the best case for *not* worrying about where they come
from — and the most-read practitioner reference says exactly that. Hamel Husain and Shreya
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
