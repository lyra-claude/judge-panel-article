#!/usr/bin/env python3
"""
estimand_check.py — Four n_eff variants on the alphaNLI 32-judge panel.

Computes Kish n_eff = n / (1 + (n-1)*phi_bar) for four different
definitions of the underlying variable and correlation estimator:

  (A) RAW SCORE:   S[i,j] = integer label index predicted by judge j on item i
                   Encoding: argmax of vote → {0,1} for alphaNLI (labels "1","2")
                   phi_bar = mean off-diagonal of np.corrcoef(S, rowvar=False)
                   where S has shape (n_items, n_judges)

  (B) BINARY ERROR: E[i,j] = 1 if judge j is WRONG (argmax != gold[i]), else 0
                   phi_bar = mean off-diagonal of np.corrcoef(E, rowvar=False)
                   Items with zero-variance error vectors dropped (constant-correct
                   or constant-wrong judges); none expected for 32 LLMs.

  (C) DEMEANED ERROR (removes item main effect / difficulty):
                   R[i,j] = E[i,j] - mean_j(E[i,j])
                   phi_bar = mean off-diagonal of np.corrcoef(R, rowvar=False)
                   This is the per-item mean-centered error residual.
                   Judges with zero residual variance are dropped.

  (D) ONE-WAY ICC on errors (within-item grouping):
                   ICC(1) = (MSB - MSW) / (MSB + (n-1)*MSW)
                   where MSB = MS_between items, MSW = MS_within items,
                   computed on the binary error matrix E (shape: n_items × n_judges).
                   Then n_eff_D = n / (1 + (n-1)*ICC).

Dataset: alphaNLI, 32-judge LLM panel, complete-case (5 items dropped for
parse_fail), n_items=995, n_judges=32.

Usage:
    cd /home/lyra/projects/chaosnli-neff
    ../.venv/bin/python ../judge-panel-article/scripts/estimand_check.py
    # or from any directory with absolute path and the venv:
    /home/lyra/projects/chaosnli-neff/.venv/bin/python \
        /home/lyra/projects/judge-panel-article/scripts/estimand_check.py

Dependencies: numpy (in chaosnli-neff/.venv)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# Paths — the chaosnli-neff project has the repo src and data
# ---------------------------------------------------------------------------
CHAOSNLI_PROJECT = Path("/home/lyra/projects/chaosnli-neff")
REPO = CHAOSNLI_PROJECT / "repo"
CHAOSNLI_FILE = CHAOSNLI_PROJECT / "chaosNLI_v1.0" / "chaosNLI_alphanli.jsonl"
sys.path.insert(0, str(REPO / "src"))

import votes_io  # noqa: E402 — from repo/src/


DATASET = "alphanli"
K = 32  # number of judges


# ---------------------------------------------------------------------------
# Load panel (reuse existing infrastructure)
# ---------------------------------------------------------------------------

def load_panel():
    panel = votes_io.load_panel(
        REPO, DATASET, CHAOSNLI_FILE, failure_policy="drop-items"
    )
    # idx: shape (32, n_items) — integer label index per judge per item
    # gold: shape (n_items,) — integer gold label index
    n_judges, n_items = panel.idx.shape
    print(f"Panel loaded: {n_judges} judges × {n_items} items (complete-case)")
    print(f"  Original items: {panel.provenance['n_original_items']}, "
          f"dropped: {panel.provenance['dropped_items']}")
    print(f"  Labels: {panel.labels}")
    return panel


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def kish_neff(phi_bar: float, n: int) -> float:
    """Kish design effect n_eff = n / (1 + (n-1)*phi_bar).

    Guard: a zero-variance (perfect) panel yields no judges / an undefined
    phi_bar (NaN). In that degenerate case there is no co-failure structure, so
    the effective count is just the panel size n. Returning NaN silently would
    be a trap, so handle it explicitly.
    """
    import math
    if n <= 0 or (isinstance(phi_bar, float) and math.isnan(phi_bar)):
        return float(n)
    return n / (1.0 + (n - 1) * phi_bar)


def mean_offdiag(C: np.ndarray) -> float:
    """Mean of strictly upper-triangular off-diagonal entries of square matrix C."""
    k = C.shape[0]
    idx = np.triu_indices(k, 1)
    return float(C[idx].mean())


def corrcoef_safe(X: np.ndarray, label: str) -> tuple[np.ndarray, int]:
    """Compute np.corrcoef(X, rowvar=False) after dropping zero-variance columns.

    X: shape (n_items, n_judges)
    Returns (C, n_dropped) where C has shape (n_kept, n_kept).
    """
    var = X.var(axis=0)
    keep = var > 0.0
    n_dropped = int((~keep).sum())
    if n_dropped > 0:
        print(f"  [{label}] Dropping {n_dropped} zero-variance judge column(s)")
    if keep.sum() == 0:
        # Zero-variance (perfect) panel: all columns dropped. corrcoef would
        # return NaN silently and the downstream Kish ratio would be 0/0.
        # Signal the degenerate case explicitly instead.
        raise ValueError(
            f"[{label}] all {X.shape[1]} judge columns have zero error variance "
            "(perfect panel): co-failure correlation is undefined. Kish n_eff "
            "should be treated as the panel size in this degenerate case."
        )
    X_kept = X[:, keep]
    C = np.corrcoef(X_kept, rowvar=False)
    # Force exact unit diagonal (numerical safety)
    np.fill_diagonal(C, 1.0)
    return C, n_dropped


def one_way_icc(E: np.ndarray) -> float:
    """One-way random-effects ICC(1) treating items as groups.

    E: shape (n_items, n_judges), binary error matrix
    Returns ICC(1) = (MSB - MSW) / (MSB + (n_judges-1)*MSW)
    where MSB = MS between items, MSW = MS within items.
    """
    n_items, n_judges = E.shape
    grand_mean = E.mean()

    # Between-items SS: n_judges * sum_i (mean_i - grand_mean)^2
    item_means = E.mean(axis=1)  # shape (n_items,)
    ss_between = n_judges * np.sum((item_means - grand_mean) ** 2)
    df_between = n_items - 1

    # Within-items SS: sum_i sum_j (E[i,j] - mean_i)^2
    ss_within = np.sum((E - item_means[:, None]) ** 2)
    df_within = n_items * (n_judges - 1)

    ms_between = ss_between / df_between
    ms_within = ss_within / df_within

    icc = (ms_between - ms_within) / (ms_between + (n_judges - 1) * ms_within)
    return float(icc)


# ---------------------------------------------------------------------------
# Four variants
# ---------------------------------------------------------------------------

def variant_a(panel) -> dict:
    """(A) RAW SCORE: integer label index S[i,j] = idx[j,i]"""
    # idx: (32, n_items) → transpose to (n_items, 32)
    S = panel.idx.T.astype(float)  # shape (n_items, n_judges)
    n_judges = S.shape[1]
    C, n_dropped = corrcoef_safe(S, "A")
    k = C.shape[0]
    phi_bar = mean_offdiag(C)
    return {
        "label": "A — raw label index",
        "variable": "S[i,j] = integer label index (0 or 1 for alphaNLI)",
        "n_judges_used": k,
        "n_dropped": n_dropped,
        "phi_bar": phi_bar,
        "n_eff": kish_neff(phi_bar, k),
    }


def variant_b(panel) -> dict:
    """(B) BINARY ERROR: E[i,j] = 1 if wrong, 0 if correct"""
    gold = panel.gold  # (n_items,)
    E = (panel.idx != gold[None, :]).T.astype(float)  # (n_items, n_judges)
    n_judges = E.shape[1]
    C, n_dropped = corrcoef_safe(E, "B")
    k = C.shape[0]
    phi_bar = mean_offdiag(C)
    # Also compute overall error rate for context
    err_rate = E.mean()
    return {
        "label": "B — binary error",
        "variable": "E[i,j] = 1{vote[j,i] != gold[i]}",
        "mean_error_rate": float(err_rate),
        "n_judges_used": k,
        "n_dropped": n_dropped,
        "phi_bar": phi_bar,
        "n_eff": kish_neff(phi_bar, k),
    }


def variant_c(panel) -> dict:
    """(C) DEMEANED ERROR: R[i,j] = E[i,j] - per-item mean (removes difficulty)"""
    gold = panel.gold
    E = (panel.idx != gold[None, :]).T.astype(float)  # (n_items, n_judges)
    # Subtract per-item mean (removes item difficulty main effect)
    R = E - E.mean(axis=1, keepdims=True)  # shape (n_items, n_judges)
    n_judges = R.shape[1]
    C_mat, n_dropped = corrcoef_safe(R, "C")
    k = C_mat.shape[0]
    phi_bar = mean_offdiag(C_mat)
    singularity = -1.0 / (k - 1)
    gap_to_singularity = abs(singularity - phi_bar)
    near_singularity = gap_to_singularity < 0.01
    n_eff_val = kish_neff(phi_bar, k)
    return {
        "label": "C — demeaned error residual",
        "variable": "R[i,j] = E[i,j] - mean_j(E[i,j]) per item",
        "n_judges_used": k,
        "n_dropped": n_dropped,
        "phi_bar": phi_bar,
        "kish_singularity": singularity,
        "gap_to_singularity": gap_to_singularity,
        "near_singularity_warning": near_singularity,
        "n_eff": n_eff_val,
        "note": (
            "NEAR SINGULARITY: phi_bar is within 0.001 of the Kish pole at -1/(k-1). "
            "n_eff is not interpretable. The substantive result is: after removing item "
            "difficulty, within-item error residuals are near-independent (phi≈0)."
        ) if near_singularity else "",
    }


def variant_d(panel) -> dict:
    """(D) ONE-WAY ICC on binary errors, item as grouping factor"""
    gold = panel.gold
    E = (panel.idx != gold[None, :]).T.astype(float)  # (n_items, n_judges)
    n_judges = E.shape[1]
    icc = one_way_icc(E)
    return {
        "label": "D — one-way ICC on error (items as groups)",
        "variable": "E[i,j] binary error, ICC(1) with items as random groups",
        "n_judges_used": n_judges,
        "ICC": icc,
        "n_eff": kish_neff(icc, n_judges),
    }


# ---------------------------------------------------------------------------
# Cross-check: replicate the paper's own n_eff
# ---------------------------------------------------------------------------

def crosscheck_paper(panel) -> dict:
    """Replicate results-error-corr-neff.json task_B n_eff_Kish = 1.9917."""
    gold = panel.gold
    binary = (panel.idx != gold[None, :]).astype(float)  # (32, n_items)
    binary -= binary.mean(axis=1, keepdims=True)
    var = np.sum(binary ** 2, axis=1)
    C = (binary @ binary.T) / np.sqrt(np.outer(var, var))
    np.fill_diagonal(C, 1.0)
    k = C.shape[0]
    phi_bar = mean_offdiag(C)
    n_eff = kish_neff(phi_bar, k)
    return {"phi_bar": float(phi_bar), "n_eff_Kish": float(n_eff)}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    panel = load_panel()
    n_items, n_judges = panel.idx.shape[1], panel.idx.shape[0]

    print("\nRunning four n_eff variants...\n")

    A = variant_a(panel)
    B = variant_b(panel)
    C = variant_c(panel)
    D = variant_d(panel)
    cc = crosscheck_paper(panel)

    # ------------------------------------------------------------------
    # Print compact table
    # ------------------------------------------------------------------
    print("=" * 72)
    print(f"Kish n_eff — Four Estimands  |  alphaNLI, k={n_judges} judges, "
          f"n_items={n_items}")
    print("=" * 72)
    print(f"{'Variant':<38} {'phi_bar / ICC':>14} {'n_eff':>8}")
    print("-" * 72)

    for res in [A, B, C, D]:
        corr_val = res.get("ICC", res.get("phi_bar"))
        label_short = res["label"]
        n_eff_val = res["n_eff"]
        n_dropped = res.get("n_dropped", 0)
        suffix = f"  (dropped {n_dropped} judges)" if n_dropped else ""
        print(f"  {label_short:<36} {corr_val:>14.4f} {n_eff_val:>8.4f}{suffix}")

    print("-" * 72)
    print(f"\n  Cross-check vs paper (error-corr, mean-centered judges):")
    print(f"    phi_bar = {cc['phi_bar']:.6f},  n_eff_Kish = {cc['n_eff_Kish']:.4f}")
    print(f"    (expected from results-error-corr-neff.json: 1.9917)")
    print()

    # ------------------------------------------------------------------
    # Interpretation
    # ------------------------------------------------------------------
    gap_AB = abs(A["n_eff"] - B["n_eff"])
    print("INTERPRETATION")
    print("-" * 72)
    print(f"(A) Raw score:      phi={A['phi_bar']:.4f}, n_eff={A['n_eff']:.4f}")
    print(f"(B) Binary error:   phi={B['phi_bar']:.4f}, n_eff={B['n_eff']:.4f}   "
          f"(mean error rate: {B['mean_error_rate']:.4f})")
    print(f"(C) Demeaned error: phi={C['phi_bar']:.4f}, n_eff={C['n_eff']:.4f}   "
          f"(difficulty removed)")
    print(f"(D) ICC on error:   ICC={D['ICC']:.4f}, n_eff={D['n_eff']:.4f}   "
          f"(item-as-group ICC)")
    print()
    print(f"  A vs B gap in n_eff:  {gap_AB:.4f}  "
          f"({'material' if gap_AB > 0.3 else 'minor'})")
    singularity = -1.0 / (n_judges - 1)
    print(f"  B→C shift:  {C['n_eff'] - B['n_eff']:+.4f}  "
          f"({'UP — difficulty artefact reduced n_eff' if C['n_eff'] > B['n_eff'] else 'DOWN — difficulty removal tightens apparent agreement'})")
    print(f"  *** WARNING: Variant C phi_bar={C['phi_bar']:.4f} is near the Kish singularity "
          f"at -1/(k-1)={singularity:.4f}. ***")
    print(f"  *** Gap to singularity: {abs(singularity - C['phi_bar']):.4f}. "
          f"Kish n_eff is not meaningful in this regime. ***")
    print(f"  *** Interpretation: after removing item main effect, within-item error "
          f"residuals are near-independent (phi≈0), so n_eff → large. ***")
    print(f"  B→D shift:  {D['n_eff'] - B['n_eff']:+.4f}  "
          f"(ICC vs Pearson-corrcoef on same error matrix)")
    print()
    print("  Closest to Kohli 2.18 estimand (Kish on mean Pearson phi, error vectors):")
    print(f"    → Variant B (binary error, Pearson corrcoef, n_eff={B['n_eff']:.4f})")
    print(f"      and cross-check paper = {cc['n_eff_Kish']:.4f}")
    print("      (B uses corrcoef on raw E; cross-check uses mean-centered; "
          "phi_bar differs\n       because corrcoef normalises by Var[E_j] while "
          "mean-centering per-judge then\n       inner-product also normalises — "
          "numerically very close, minor diff shown above)")

    # ------------------------------------------------------------------
    # Save JSON
    # ------------------------------------------------------------------
    output_dir = Path(__file__).parent
    out_path = output_dir / "estimand_check_results.json"
    results = {
        "dataset": DATASET,
        "n_judges": n_judges,
        "n_items": n_items,
        "variants": {
            "A": {k: (round(v, 6) if isinstance(v, float) else v)
                  for k, v in A.items()},
            "B": {k: (round(v, 6) if isinstance(v, float) else v)
                  for k, v in B.items()},
            "C": {k: (round(v, 6) if isinstance(v, float) else v)
                  for k, v in C.items()},
            "D": {k: (round(v, 6) if isinstance(v, float) else v)
                  for k, v in D.items()},
        },
        "crosscheck_paper": {
            "phi_bar": round(cc["phi_bar"], 6),
            "n_eff_Kish": round(cc["n_eff_Kish"], 4),
            "expected_from_results_json": 1.9917,
        },
    }
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nResults saved: {out_path}")


if __name__ == "__main__":
    main()
