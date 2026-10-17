## Worked example: counting your *real* number of judges

You ran 5 LLM judges over 6 test items. It feels like 5 opinions. It isn't. When
judges make *correlated* mistakes — they tend to flunk the same items — those 5
votes carry the information of far fewer independent ones. Here's how to put a
number on it, by hand, in about five minutes.

### Step 0 — the error matrix

Score each judge on each item: **1 = got it wrong**, **0 = got it right**. Not the
label, not the rationale — just the error indicator. Here's our toy panel. Each
judge happens to miss exactly 2 of the 6 items, so no single judge is worse than
another; the only thing that varies is *who misses what*.

| Item | J1 | J2 | J3 | J4 | J5 |
|------|----|----|----|----|----|
| A    | 1  | 1  | 1  | 1  | 1  |
| B    | 1  | 1  | 0  | 0  | 0  |
| C    | 0  | 0  | 1  | 0  | 0  |
| D    | 0  | 0  | 0  | 1  | 0  |
| E    | 0  | 0  | 0  | 0  | 1  |
| **errors** | 2 | 2 | 2 | 2 | 2 |

(Item F is all-zeros — everyone got it right.) Notice everybody trips on item A,
and J1 and J2 are carbon copies of each other. That's correlation, and it's about
to cost us.

### Step 1 — pairwise φ (the phi coefficient)

For two 0/1 columns, φ is just Pearson's correlation. The shortcut: with equal
error rate *p* per judge, φ = (fraction of items both got wrong − p²) / (p(1−p)).
Here p = 2/6 = 1/3, so p(1−p) = 2/9 and p² = 1/9.

- **J1 & J2** both miss the *same* 2 items (A, B). Both-wrong fraction = 2/6.
  φ = (2/6 − 1/9) / (2/9) = (2/9)/(2/9) = **1**. Perfectly redundant — one is a free copy.
- **Every other pair** (e.g. J1 & J3) shares exactly 1 item (A). Both-wrong fraction = 1/6.
  φ = (1/6 − 1/9) / (2/9) = (1/18)/(2/9) = **1/4 = 0.25**.

There are 10 pairs total: 9 of them at φ = 0.25, and the one twin pair at φ = 1.

### Step 2 — average and plug into Kish

$$\bar\varphi = \frac{9(0.25) + 1(1.0)}{10} = \frac{3.25}{10} = 0.325$$

$$n_{\text{eff}} = \frac{k}{1 + (k-1)\,\bar\varphi} = \frac{5}{1 + 4(0.325)} = \frac{5}{2.3} \approx \mathbf{2.17}$$

Five judges. Two and a bit independent opinions. The twin pair alone erased almost
a whole vote, and the mild shared tendency to miss item A ate most of the rest.

### Step 3 — why NOT κ (read this twice)

Here's the trap. People reach for Cohen's **κ**, the chance-corrected agreement
score, because it's familiar. Let's compute it for the J1–J3 pair.

- Observed agreement p₀ = (both-wrong + both-right)/6 = (1 + 3)/6 = **2/3**.
- Chance agreement pₑ = (⅓·⅓) + (⅔·⅔) = 1/9 + 4/9 = **5/9**.
- κ = (p₀ − pₑ)/(1 − pₑ) = (2/3 − 5/9)/(1 − 5/9) = (1/9)/(4/9) = **1/4**.

Here κ = 0.25 = φ — but *only* because this toy is perfectly balanced (every judge
errs at exactly 1/3, so their marginals match). The moment two judges err at
*different* rates, κ and φ split apart. The next section shows exactly that.

### Why you can't just use κ

Take two judges over 6 items with *unequal* error rates. Judge X errs on 4 items
{A, B, C, D}; Judge Y errs on 2 {A, B}; they overlap on 2 (both wrong on A and B).
The 2×2 contingency: both-wrong = 2, X-wrong/Y-right = 2, Y-wrong/X-right = 0,
both-right = 2.

- **φ** = (ad − bc) / √((a+b)(c+d)(a+c)(b+d)) = (2·2 − 2·0) / √(4·2·4·2) = 4/8 = **0.50**.
- **κ**: p₀ = (2+2)/6 = 2/3, pₑ = (⅔·⅓) + (⅓·⅔) = 4/9, κ = (2/3 − 4/9)/(1 − 4/9) = (2/9)/(5/9) = **0.40**.

Same six items, same data — **φ = 0.50 but κ = 0.40**, because the marginals differ
(4/6 vs 2/6). They're linked by κ = q·φ (here q = 4/5), where q depends on the
judges' error rates (Rao & Callison-Burch). **The Kish formula wants φ; κ is a
different quantity.** Plug κ in and your n_eff is simply wrong. φ in, κ stays out.

### The 3-line takeaway

1. For every pair of judges, measure how often they err *together* beyond chance — that's **φ** (plain correlation of the 0/1 "got-it-wrong" columns). Average over all pairs → **φ̄**.
2. Then **n_eff = k / (1 + (k−1)·φ̄)**.
3. For k = 9 judges with φ̄ ≈ 0.5: n_eff = 9 / (1 + 8·0.5) = 9/5 ≈ **1.8**. Nine judges, worth less than two.
