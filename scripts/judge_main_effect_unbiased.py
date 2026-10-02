#!/usr/bin/env python3
"""
judge_main_effect_unbiased.py — Unbiased random-effects ANOVA variance components
for the ChaosNLI two-way crossed no-replication error matrix.

WHY THIS SCRIPT EXISTS
----------------------
The descriptive estimator Var_judges = SS_judges / (I * J) = Var(column means) is
BIASED (inflated) for the true judge main-effect variance component sigma2_judge.

Each column mean carries sampling noise of order sigma2_resid / I (i.e. MS_resid / I),
which is the same order as the estimand.  The expected-mean-square analysis gives the
correct unbiased estimator:

    E[MS_judges] = sigma2_resid + I * sigma2_judge
    => sigma2_judge = (MS_judges - MS_resid) / I

MODEL
-----
E[i,j] = mu + a_i + b_j + resid_ij      (I items, J judges, no replication)

  a_i ~ iid(0, sigma2_item)
  b_j ~ iid(0, sigma2_judge)
  resid_ij ~ iid(0, sigma2_resid)

SS AND MEAN SQUARES
-------------------
SS_items  = J * sum_i (rowmean_i - mu)^2        df = I - 1
SS_judges = I * sum_j (colmean_j - mu)^2        df = J - 1
SS_resid  = SS_total - SS_items - SS_judges      df = (I-1)*(J-1)

MS_items  = SS_items  / (I - 1)
MS_judges = SS_judges / (J - 1)
MS_resid  = SS_resid  / ((I - 1) * (J - 1))

EXPECTED MEAN SQUARES (random-effects two-way no-replication)
-------------------------------------------------------------
E[MS_resid]  = sigma2_resid
E[MS_judges] = sigma2_resid + I * sigma2_judge
E[MS_items]  = sigma2_resid + J * sigma2_item

=> sigma2_judge = (MS_judges - MS_resid) / I    [KEY: unbiased, may be negative]
=> sigma2_item  = (MS_items  - MS_resid) / J
=> sigma2_resid = MS_resid

NULL-EXPECTED COLUMN-MEAN VARIANCE
-----------------------------------
If b_j = 0 for all j (no judge effect), the column means vary only by sampling noise:
    Var(colmean_j) ≈ sigma2_resid / I ≈ MS_resid / I
This is the "null-expected" descriptor.  Comparing naive Var_judges to it shows
how many times above pure noise the descriptive estimator sits.

Usage:
    /home/lyra/projects/chaosnli-neff/.venv/bin/python \
        /home/lyra/projects/judge-panel-article/scripts/judge_main_effect_unbiased.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
CHAOSNLI_PROJECT = Path("/home/lyra/projects/chaosnli-neff")
REPO = CHAOSNLI_PROJECT / "repo"
sys.path.insert(0, str(REPO / "src"))

import votes_io  # noqa: E402

SUBSETS = {
    "alphanli": CHAOSNLI_PROJECT / "chaosNLI_v1.0" / "chaosNLI_alphanli.jsonl",
    "snli":     CHAOSNLI_PROJECT / "chaosNLI_v1.0" / "chaosNLI_snli.jsonl",
    "mnli_m":   CHAOSNLI_PROJECT / "chaosNLI_v1.0" / "chaosNLI_mnli_m.jsonl",
}


# ---------------------------------------------------------------------------
# Core computation
# ---------------------------------------------------------------------------

def unbiased_variance_components(E: np.ndarray) -> dict:
    """Unbiased random-effects ANOVA variance components for two-way crossed design.

    E: shape (I, J) = (n_items, n_judges), binary float.

    Returns a dict with all MS, unbiased sigma2_*, descriptive Var_judges,
    null-expected column-mean variance, and the ratio naive/null.
    """
    I, J = E.shape

    grand_mean = E.mean()
    row_means = E.mean(axis=1)   # shape (I,)
    col_means = E.mean(axis=0)   # shape (J,)

    # Sums of squares
    ss_total  = float(np.sum((E - grand_mean) ** 2))
    ss_items  = float(J * np.sum((row_means - grand_mean) ** 2))
    ss_judges = float(I * np.sum((col_means - grand_mean) ** 2))
    ss_resid  = float(ss_total - ss_items - ss_judges)

    # Degrees of freedom
    df_items  = I - 1
    df_judges = J - 1
    df_resid  = df_items * df_judges

    # Mean squares
    ms_items  = ss_items  / df_items
    ms_judges = ss_judges / df_judges
    ms_resid  = ss_resid  / df_resid

    # Unbiased random-effects variance components (may be negative)
    sigma2_judge = (ms_judges - ms_resid) / I
    sigma2_item  = (ms_items  - ms_resid) / J
    sigma2_resid = ms_resid

    # Sum of components for fraction computation
    # (use raw values including negatives for fraction; note: if negative, interpret carefully)
    total_sigma2 = sigma2_item + sigma2_judge + sigma2_resid

    if total_sigma2 > 0:
        frac_judge_pct = 100.0 * sigma2_judge / total_sigma2
    else:
        frac_judge_pct = float("nan")

    # Descriptive (biased) estimator: population variance of column means
    var_judges_naive = float(np.var(col_means, ddof=0))  # = ss_judges / (I * J)

    # Null-expected: Var(colmean_j) under b_j = 0
    null_expected_colmean_var = ms_resid / I

    # Ratio: naive / null-expected
    if null_expected_colmean_var > 0:
        ratio_naive_to_null = var_judges_naive / null_expected_colmean_var
    else:
        ratio_naive_to_null = float("nan")

    return {
        "n_items":  I,
        "n_judges": J,
        # Mean squares
        "ms_items":  float(ms_items),
        "ms_judges": float(ms_judges),
        "ms_resid":  float(ms_resid),
        # Unbiased variance components
        "sigma2_item":  float(sigma2_item),
        "sigma2_judge": float(sigma2_judge),   # KEY: may be negative
        "sigma2_resid": float(sigma2_resid),
        "sigma2_judge_negative": float(sigma2_judge) < 0,
        "sigma2_judge_truncated": max(0.0, float(sigma2_judge)),
        # Judge fraction of total variance
        "frac_judge_pct": float(frac_judge_pct),
        # Descriptive comparison
        "var_judges_naive":           float(var_judges_naive),
        "null_expected_colmean_var":  float(null_expected_colmean_var),
        "ratio_naive_to_null":        float(ratio_naive_to_null),
        # Grand mean for context
        "grand_mean": float(grand_mean),
    }


# ---------------------------------------------------------------------------
# Process one subset
# ---------------------------------------------------------------------------

def process_subset(dataset_key: str, human_path: Path) -> dict:
    panel = votes_io.load_panel(
        REPO, dataset_key, human_path, failure_policy="drop-items"
    )
    gold  = panel.gold
    E = (panel.idx != gold[None, :]).T.astype(float)   # (n_items, n_judges)
    return unbiased_variance_components(E)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    results = {}
    for key, path in SUBSETS.items():
        if not path.exists():
            print(f"ERROR: data file not found: {path}")
            sys.exit(1)
        results[key] = process_subset(key, path)

    # ------------------------------------------------------------------
    # Print compact table
    # ------------------------------------------------------------------
    W = 130
    print("=" * W)
    print("UNBIASED RANDOM-EFFECTS ANOVA VARIANCE COMPONENTS — ChaosNLI (3 subsets)")
    print("=" * W)
    print()
    print("Model:  E[i,j] = mu + a_i + b_j + resid_ij")
    print("        sigma2_judge = (MS_judges - MS_resid) / I   [unbiased, EMS derivation]")
    print("        null_expected = MS_resid / I                [colmean variance if b_j=0]")
    print()

    # Header
    hdr = (
        f"{'Subset':<10} {'I':>6} {'J':>4} "
        f"{'MS_items':>10} {'MS_judges':>10} {'MS_resid':>10}  "
        f"{'s2_item':>10} {'s2_judge':>10} {'s2_resid':>10}  "
        f"{'judge%':>7}  "
        f"{'Var_j(naive)':>13} {'null_exp':>10} {'naive/null':>10}"
    )
    print(hdr)
    print("-" * W)

    for key, r in results.items():
        neg_flag = " [NEG]" if r["sigma2_judge_negative"] else ""
        print(
            f"  {key:<8} "
            f"{r['n_items']:>6} {r['n_judges']:>4}  "
            f"{r['ms_items']:>10.6f} {r['ms_judges']:>10.6f} {r['ms_resid']:>10.6f}  "
            f"{r['sigma2_item']:>10.6f} {r['sigma2_judge']:>10.6f}{neg_flag} {r['sigma2_resid']:>10.6f}  "
            f"{r['frac_judge_pct']:>6.2f}%  "
            f"{r['var_judges_naive']:>13.8f} {r['null_expected_colmean_var']:>10.6f} {r['ratio_naive_to_null']:>10.4f}x"
        )

    print()
    print("Columns:")
    print("  I, J            : n_items, n_judges")
    print("  MS_*            : mean squares (SS / df)")
    print("  s2_item         : sigma2_item  = (MS_items  - MS_resid) / J   [unbiased]")
    print("  s2_judge        : sigma2_judge = (MS_judges - MS_resid) / I   [unbiased, KEY]")
    print("                    [NEG] = raw negative value, conventional truncated estimate = 0")
    print("  s2_resid        : sigma2_resid = MS_resid                     [unbiased]")
    print("  judge%          : sigma2_judge / (sigma2_item + sigma2_judge + sigma2_resid) * 100")
    print("                    (computed from raw, not truncated, values)")
    print("  Var_j(naive)    : SS_judges / (I*J) = Var(col means) — descriptive BIASED estimator")
    print("  null_exp        : MS_resid / I — expected Var(col means) if all b_j = 0")
    print("  naive/null      : ratio of naive to null-expected (how many × above pure sampling noise)")
    print()

    # Per-subset detail block
    print("=" * W)
    print("PER-SUBSET DETAIL")
    print("=" * W)
    for key, r in results.items():
        print()
        print(f"  [{key}]")
        print(f"    n_items={r['n_items']}, n_judges={r['n_judges']}, grand_mean={r['grand_mean']:.6f}")
        print(f"    MS_items  = {r['ms_items']:.8f}")
        print(f"    MS_judges = {r['ms_judges']:.8f}")
        print(f"    MS_resid  = {r['ms_resid']:.8f}")
        print(f"    sigma2_item  (unbiased) = {r['sigma2_item']:.8f}")
        print(f"    sigma2_judge (unbiased) = {r['sigma2_judge']:.8f}"
              + ("  <-- NEGATIVE (truncate to 0)" if r["sigma2_judge_negative"] else "  <-- KEY"))
        print(f"    sigma2_resid (= MS_resid)= {r['sigma2_resid']:.8f}")
        print(f"    judge fraction          = {r['frac_judge_pct']:.4f}%")
        print(f"    Var_judges (naive/biased)= {r['var_judges_naive']:.8f}")
        print(f"    null-expected col-mean   = {r['null_expected_colmean_var']:.8f}")
        print(f"    naive / null-expected    = {r['ratio_naive_to_null']:.4f}x")

    # Save JSON
    out_path = Path(__file__).parent / "judge_main_effect_unbiased_results.json"
    out_path.write_text(
        json.dumps(results, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print()
    print(f"Results saved: {out_path}")


if __name__ == "__main__":
    main()
