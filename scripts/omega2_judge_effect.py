#!/usr/bin/env python3
"""
omega2_judge_effect.py — Clio's §6 judge main-effect estimator omega^2.

Model: E_ij = mu + a_i (item, Var=tau^2) + w_j (judge, Var=omega^2)
             + eps_ij (idiosyncratic, Var=sigma^2).
Factor = JUDGES (columns); replicates = ITEMS (rows). E is (I items, J judges).

Clio's estimator:
    omega_hat^2 = Var_j( column_mean_j(E) )  -  (tau_hat^2 + sigma_hat^2) / I
where
    column_mean_j = mean error of judge j across all I items (J of them)
    Var_j(...)    = empirical variance across the J column means (ddof=0)
    I             = number of items
    tau_hat^2, sigma_hat^2 from error-correlation decomposition:
        phi_bar = tau^2 / (tau^2 + sigma^2),  tau^2 + sigma^2 = Var(E_ij) pooled entry var
        => tau_hat^2 = phi_bar * Var(E_ij),  sigma_hat^2 = (1-phi_bar) * Var(E_ij)

Also reports the standard EMS-unbiased estimator
    sigma2_judge = (MS_judges - MS_resid) / I
for reconciliation, and a two-way ANOVA cross-check.

Does NOT modify any existing script. Does NOT commit.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

CHAOSNLI_PROJECT = Path("/home/lyra/projects/chaosnli-neff")
REPO = CHAOSNLI_PROJECT / "repo"
sys.path.insert(0, str(REPO / "src"))

import votes_io  # noqa: E402

SUBSETS = {
    "alphanli": CHAOSNLI_PROJECT / "chaosNLI_v1.0" / "chaosNLI_alphanli.jsonl",
    "snli":     CHAOSNLI_PROJECT / "chaosNLI_v1.0" / "chaosNLI_snli.jsonl",
    "mnli_m":   CHAOSNLI_PROJECT / "chaosNLI_v1.0" / "chaosNLI_mnli_m.jsonl",
}


def mean_offdiag(C: np.ndarray) -> float:
    k = C.shape[0]
    idx = np.triu_indices(k, 1)
    return float(C[idx].mean())


def phi_bar_variantB(E: np.ndarray) -> tuple[float, float, int]:
    """Variant B: Pearson corrcoef on raw binary error matrix, drop zero-var cols."""
    var = E.var(axis=0)
    keep = var > 0.0
    n_dropped = int((~keep).sum())
    if keep.sum() == 0:
        # Perfect panel (zero error variance everywhere): corrcoef -> NaN and the
        # Kish ratio becomes 0/0. There is no co-failure structure, so n_eff is
        # just the panel size. Return it explicitly rather than a silent NaN.
        return 0.0, float(E.shape[1]), n_dropped
    E_k = E[:, keep]
    k = E_k.shape[1]
    C = np.corrcoef(E_k, rowvar=False)
    np.fill_diagonal(C, 1.0)
    phi_bar = mean_offdiag(C)
    n_eff = k / (1.0 + (k - 1) * phi_bar)
    return phi_bar, n_eff, n_dropped


def analyse(E: np.ndarray) -> dict:
    I, J = E.shape

    # --- Sanity: Variant B phi_bar and Kish n_eff
    phi_bar, n_eff, n_dropped = phi_bar_variantB(E)

    # --- Column means (per-judge error rates)
    col_means = E.mean(axis=0)              # (J,)
    var_colmeans = float(np.var(col_means, ddof=0))

    # --- Pooled per-entry variance Var(E_ij) (population, over all I*J cells)
    var_entry = float(np.var(E, ddof=0))    # = pbar*(1-pbar) for binary

    # --- Clio's tau^2, sigma^2 from the error-correlation decomposition
    tau2 = phi_bar * var_entry
    sigma2 = (1.0 - phi_bar) * var_entry

    # --- Clio's omega^2 estimator (bias correction = (tau^2+sigma^2)/I = var_entry/I)
    bias_correction_clio = (tau2 + sigma2) / I          # = var_entry / I
    omega2_clio = var_colmeans - bias_correction_clio
    ratio_clio = omega2_clio / tau2

    # --- Standard EMS-unbiased two-way ANOVA (for reconciliation)
    grand = E.mean()
    row_means = E.mean(axis=1)
    ss_total  = float(np.sum((E - grand) ** 2))
    ss_items  = float(J * np.sum((row_means - grand) ** 2))
    ss_judges = float(I * np.sum((col_means - grand) ** 2))
    ss_resid  = ss_total - ss_items - ss_judges
    ms_items  = ss_items  / (I - 1)
    ms_judges = ss_judges / (J - 1)
    ms_resid  = ss_resid  / ((I - 1) * (J - 1))
    sigma2_judge_ems = (ms_judges - ms_resid) / I        # unbiased EMS judge component
    sigma2_item_ems  = (ms_items  - ms_resid) / J
    # EMS correction relates to Var(col means): Var_j(colmean)=SS_judges/(I*J)=ms_judges*(J-1)/(I*J)
    ratio_ems = sigma2_judge_ems / sigma2_item_ems       # omega^2/tau^2 in EMS world

    return {
        "I": I, "J": J, "n_dropped": n_dropped,
        "phi_bar": phi_bar, "n_eff": n_eff,
        "col_mean_min": float(col_means.min()),
        "col_mean_max": float(col_means.max()),
        "col_mean_mean": float(col_means.mean()),
        "var_colmeans": var_colmeans,
        "var_entry": var_entry,
        "tau2": tau2, "sigma2": sigma2,
        "bias_correction_clio": bias_correction_clio,
        "omega2_clio": omega2_clio,
        "ratio_clio": ratio_clio,
        # EMS reconciliation
        "ms_items": ms_items, "ms_judges": ms_judges, "ms_resid": ms_resid,
        "sigma2_judge_ems": sigma2_judge_ems,
        "sigma2_item_ems": sigma2_item_ems,
        "ratio_ems": ratio_ems,
    }


def classify(omega2: float, tau2: float) -> str:
    r = omega2 / tau2
    if omega2 <= 0 or abs(omega2) < 1e-6:
        return "(a) omega^2 ~ 0 : re-attribution clean; item is the unit of replication unconditionally"
    if r < 0.05:
        return f"(b) 0 < omega^2 << tau^2 (ratio={r:.4f}) : holds with small stated remainder; J* slightly > 1"
    if r < 0.5:
        return f"(b/borderline) omega^2 modest fraction of tau^2 (ratio={r:.4f}) : small remainder"
    return f"(c) omega^2 >~ tau^2 (ratio={r:.4f}) : ceiling SHARED across judges, not relocated to item"


def main():
    print("=" * 90)
    print("Clio's omega^2 judge main-effect estimator — ChaosNLI")
    print("=" * 90)
    for key, path in SUBSETS.items():
        panel = votes_io.load_panel(REPO, key, path, failure_policy="drop-items")
        gold = panel.gold
        E = (panel.idx != gold[None, :]).T.astype(float)   # (I, J)
        r = analyse(E)
        print(f"\n[{key}]  I={r['I']} items, J={r['J']} judges, dropped={r['n_dropped']}")
        print(f"  SANITY  phi_bar = {r['phi_bar']:.5f}   Kish n_eff = {r['n_eff']:.4f}")
        print(f"  col-means: min={r['col_mean_min']:.6f} max={r['col_mean_max']:.6f} "
              f"mean={r['col_mean_mean']:.6f}")
        print(f"  Var_j(col means)      = {r['var_colmeans']:.8f}")
        print(f"  Var(E_ij) pooled      = {r['var_entry']:.8f}")
        print(f"  tau_hat^2             = {r['tau2']:.8f}")
        print(f"  sigma_hat^2           = {r['sigma2']:.8f}")
        print(f"  bias corr (var/I)     = {r['bias_correction_clio']:.8f}")
        print(f"  >>> omega_hat^2 (Clio)= {r['omega2_clio']:.8g}")
        print(f"  >>> omega^2 / tau^2   = {r['ratio_clio']:.6g}")
        print(f"  CLASSIFICATION: {classify(r['omega2_clio'], r['tau2'])}")
        print(f"  --- EMS reconciliation ---")
        print(f"  sigma2_judge (EMS)    = {r['sigma2_judge_ems']:.8g}")
        print(f"  sigma2_item  (EMS)    = {r['sigma2_item_ems']:.8g}")
        print(f"  omega^2/tau^2 (EMS)   = {r['ratio_ems']:.6g}")
        print(f"  omega2 Clio / omega2 EMS = {r['omega2_clio']/r['sigma2_judge_ems']:.4f}")


if __name__ == "__main__":
    main()
