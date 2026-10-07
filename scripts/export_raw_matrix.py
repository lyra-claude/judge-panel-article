#!/usr/bin/env python3
"""
export_raw_matrix.py — Deterministic re-serialization of the Li-Yu-Li
32-judge vote/error matrices for all three ChaosNLI subsets.

PROVENANCE: Public dataset — Li, Yu, Li (2024) "32judges-votes", arXiv
2609.21277, CC BY 4.0.  This script is a convenience re-serialization of
the disaggregated JSONL vote files in the chaosnli-neff repository; it
introduces no new data and no randomness.

OUTPUT (written to data/raw-judge-matrix/<subset>/):
  votes_matrix.csv  — rows=items, columns=[item_uid, gold, j01, ..., j32]
                       where jNN is the judge's raw label vote (1 or 2 for
                       alphanli; e/n/c for snli/mnli_m).
  error_matrix.csv  — same shape, entries are binary: 1 if judge's label
                       != gold (judge wrong), 0 if correct.

ERROR DEFINITION (matches judge_main_effect.py exactly):
  - failure_policy = "drop-items": any item with at least one parse_fail=true
    across any judge is dropped from the matrix entirely.
  - gold = majority_label from the ChaosNLI upstream JSONL (gold_field="majority_label").
  - error[i,j] = 1 iff panel.idx[j,i] != panel.gold[i]  (i.e. label index mismatch).

JUDGE COLUMN ORDERING: sorted lexicographically by source filename stem
(same order votes_io.load_panel uses internally: sorted(glob("*.jsonl"))).
The filename→column mapping is recorded in data/raw-judge-matrix/README.md.

Usage:
    /home/lyra/projects/chaosnli-neff/.venv/bin/python \\
        /home/lyra/projects/judge-panel-article/scripts/export_raw_matrix.py
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
CHAOSNLI_PROJECT = Path("/home/lyra/projects/chaosnli-neff")
REPO = CHAOSNLI_PROJECT / "repo"
sys.path.insert(0, str(REPO / "src"))

import votes_io  # noqa: E402  (third-party, repo-local)

SUBSETS = {
    "alphanli": CHAOSNLI_PROJECT / "chaosNLI_v1.0" / "chaosNLI_alphanli.jsonl",
    "snli":     CHAOSNLI_PROJECT / "chaosNLI_v1.0" / "chaosNLI_snli.jsonl",
    "mnli_m":   CHAOSNLI_PROJECT / "chaosNLI_v1.0" / "chaosNLI_mnli_m.jsonl",
}

OUT_ROOT = Path(__file__).parent.parent / "data" / "raw-judge-matrix"


# ---------------------------------------------------------------------------
# Export one subset
# ---------------------------------------------------------------------------

def export_subset(dataset_key: str, human_path: Path, out_dir: Path) -> dict:
    """Load panel via votes_io, write votes_matrix.csv and error_matrix.csv.

    Returns a summary dict for the README.
    """
    panel = votes_io.load_panel(
        REPO, dataset_key, human_path, failure_policy="drop-items"
    )
    # panel.idx  shape: (n_judges, n_items)  — label indices (0-based)
    # panel.gold shape: (n_items,)            — gold label index
    # panel.judges: list of judge stem names, in sorted(glob) order
    # panel.labels: tuple of canonical label strings
    # panel.uids:   list of retained item UIDs

    n_judges, n_items = panel.idx.shape
    labels = panel.labels  # e.g. ("1","2") or ("e","n","c")
    judges = panel.judges  # already sorted lexicographically by votes_io

    # --- Build votes matrix (raw label strings) ----------------------------
    # panel.idx[j, i] = label index; map back to label string
    votes = np.array([[labels[panel.idx[j, i]] for j in range(n_judges)]
                      for i in range(n_items)])
    # gold label strings
    gold_strs = [labels[g] for g in panel.gold]

    # --- Build error matrix (binary) ---------------------------------------
    # error[i, j] = 1 iff judge j erred on item i
    error = (panel.idx != panel.gold[None, :]).T.astype(int)  # (n_items, n_judges)

    # --- Write votes_matrix.csv --------------------------------------------
    out_dir.mkdir(parents=True, exist_ok=True)
    judge_cols = [f"j{str(k+1).zfill(2)}" for k in range(n_judges)]
    header = ["item_uid", "gold"] + judge_cols

    votes_path = out_dir / "votes_matrix.csv"
    with votes_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        for i, uid in enumerate(panel.uids):
            w.writerow([uid, gold_strs[i]] + list(votes[i]))

    # --- Write error_matrix.csv --------------------------------------------
    error_path = out_dir / "error_matrix.csv"
    with error_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        for i, uid in enumerate(panel.uids):
            w.writerow([uid, gold_strs[i]] + list(error[i]))

    # --- Build filename→column mapping for README --------------------------
    judge_map = {f"j{str(k+1).zfill(2)}": judges[k] for k in range(n_judges)}

    prov = panel.provenance
    n_parse_fail_items = prov["parse_fail_items"]
    n_parse_fail_cells = prov["parse_fail_cells"]
    n_original = prov["n_original_items"]

    print(f"  {dataset_key}: {n_items} items × {n_judges} judges "
          f"(dropped {n_parse_fail_items} items with ≥1 parse_fail; "
          f"{n_parse_fail_cells} parse_fail cells total)")
    print(f"    votes → {votes_path}")
    print(f"    error → {error_path}")

    return {
        "dataset_key": dataset_key,
        "n_items": n_items,
        "n_judges": n_judges,
        "n_original_items": n_original,
        "n_parse_fail_items_dropped": n_parse_fail_items,
        "n_parse_fail_cells": n_parse_fail_cells,
        "labels": list(labels),
        "gold_field": prov["gold_field"],
        "judge_map": judge_map,  # j01 -> filename stem
        "judges_in_order": judges,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    summaries = {}
    for dataset_key, human_path in SUBSETS.items():
        if not human_path.exists():
            print(f"ERROR: human file not found: {human_path}", file=sys.stderr)
            sys.exit(1)
        print(f"\nExporting {dataset_key} ...")
        out_dir = OUT_ROOT / dataset_key
        summaries[dataset_key] = export_subset(dataset_key, human_path, out_dir)

    # Write README.md
    _write_readme(summaries)
    print(f"\nREADME written: {OUT_ROOT / 'README.md'}")
    print("\nDone.")


def _write_readme(summaries: dict) -> None:
    lines = [
        "# Raw Judge Vote/Error Matrices",
        "",
        "## Provenance",
        "",
        "**Source:** Li, Yu, Li (2024), \"32judges-votes\",",
        "arXiv [2609.21277](https://arxiv.org/abs/2609.21277), **CC BY 4.0**.",
        "",
        "This is NOT Lyra's data. These files are a convenience",
        "re-serialization of the disaggregated JSONL vote files in the",
        "chaosnli-neff repository, regenerated deterministically (no",
        "randomness). The canonical source files are the per-judge JSONL",
        "files under `chaosnli-neff/repo/datasets/chaosnli-{subset}/votes/baseline/`.",
        "",
        "## Subsets",
        "",
    ]

    for key, s in summaries.items():
        lines += [
            f"### {key}",
            "",
            f"- Final matrix shape: **{s['n_items']} items × {s['n_judges']} judges**",
            f"- Original item count: {s['n_original_items']}",
            f"- Items dropped (parse_fail): {s['n_parse_fail_items_dropped']} "
            f"({s['n_parse_fail_cells']} parse_fail cells)",
            f"- Labels: {s['labels']}",
            "",
        ]

    lines += [
        "## Files",
        "",
        "Each subset directory contains two CSVs:",
        "",
        "- **votes_matrix.csv** — rows = items, columns =",
        "  `[item_uid, gold, j01, j02, ..., j32]`. The `jNN` columns contain",
        "  the judge's raw label vote (the label string, e.g. `\"1\"` / `\"2\"`",
        "  for alphaNLI, or `\"e\"` / `\"n\"` / `\"c\"` for SNLI/MNLI-m).",
        "",
        "- **error_matrix.csv** — same shape, but entries are binary: `1` if",
        "  the judge's label differs from the gold label (judge is wrong),",
        "  `0` if correct.",
        "",
        "## Error entry definition",
        "",
        "Error is defined as: `judge_label_index != gold_label_index`, where:",
        "",
        "- Gold = `majority_label` field from the upstream ChaosNLI JSONL",
        "  (Li et al.'s recorded tie-breaking; never recomputed from argmax).",
        "- Items with at least one `parse_fail=true` entry across any judge",
        "  are **dropped entirely** (`failure_policy=\"drop-items\"`), matching",
        "  the definition used in `scripts/judge_main_effect.py` and the",
        "  existing analysis pipeline.",
        "",
        "## Judge filename → column mapping",
        "",
        "Columns `j01`–`j32` correspond to the baseline vote files sorted",
        "lexicographically by filename stem (the ordering `votes_io.load_panel`",
        "uses internally).",
        "",
    ]

    for key, s in summaries.items():
        lines.append(f"### {key} judge mapping")
        lines.append("")
        lines.append("| Column | Filename stem |")
        lines.append("|--------|---------------|")
        for col, stem in s["judge_map"].items():
            lines.append(f"| {col} | `{stem}` |")
        lines.append("")

    lines += [
        "## Reproducibility",
        "",
        "Run `scripts/export_raw_matrix.py` from the `judge-panel-article`",
        "repository root to regenerate these files from the JSONL sources.",
        "The script has no randomness and is fully deterministic.",
        "",
        "## What is NOT in these files",
        "",
        "These matrices are raw input data only. No conclusions about n_eff,",
        "correlation, statistical independence, or any derived quantities are",
        "stated here. Those analyses are in the paper and the scripts.",
        "",
    ]

    readme_path = OUT_ROOT / "README.md"
    readme_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
