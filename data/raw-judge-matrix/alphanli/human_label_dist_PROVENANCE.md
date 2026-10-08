# Provenance: human_label_dist.csv

## What this file contains

Per-item human annotation label distributions for the 995 alphaNLI items
in the complete-case panel used in this article's analysis.

- **995 rows** — exactly the items in `votes_matrix.csv` / `error_matrix.csv`,
  in the same order.
- **100 human annotations per item** — every item has exactly 100 annotations.
- Labels are `"1"` and `"2"` (the two alphaNLI answer hypotheses).

## Fields

| Field | Description |
|-------|-------------|
| `item_uid` | ChaosNLI item UID; matches `item_uid` in `votes_matrix.csv` |
| `majority_label` | Human majority vote label (integer); this is the gold label used in `error_matrix.csv` |
| `n_annotations` | Total human annotations per item (always 100 in this dataset) |
| `count_label_1` | Human annotators who chose label "1" |
| `count_label_2` | Human annotators who chose label "2" |
| `frac_label_1` | `count_label_1 / 100` |
| `frac_label_2` | `count_label_2 / 100` |
| `entropy_nats` | Shannon entropy of the label distribution in nats, taken directly from ChaosNLI's `entropy` field |

## Source

**ChaosNLI v1.0** (Nie et al. 2020, arXiv 2010.03532).  
Fields `label_count`, `label_dist`, `majority_label`, `entropy` extracted directly from  
`chaosNLI_alphanli.jsonl` (the full 1532-item file; 995 of those are the complete-case panel).

The `entropy` field in ChaosNLI is Shannon entropy computed as `-sum(p * log(p))` over the
label distribution (nats, base-e). For a binary distribution with fractions (p, 1-p), this
equals `-p*ln(p) - (1-p)*ln(1-p)`.

Note: `majority_label` in ChaosNLI is the human-vote majority and may differ from
`old_label` (the original aNLI dataset label) for ~163/995 items (16%). The gold label
used throughout this article's error analysis is `majority_label`.

## Purpose

These distributions let Clio (and any reviewer) bound the gold-label-noise share of φ̄.
Items where humans disagree (high entropy) are items where the ChaosNLI "gold" is itself
uncertain, and this uncertainty inflates τ² (the between-item variance share), making the
reported φ̄ ≈ 0.486 an upper estimate of true judge co-failure correlation.

## Statistics (all 995 items)

- `entropy_nats`: mean = 0.3949, min = 0.0000, max = 1.0000 (log 2 ≈ 0.693 nats = max for binary)
- Items with entropy > 0.5 nats: 329 / 995 (33%)
- Items with entropy = 0 (unanimous): check count_label_1=0 or count_label_2=0

## Reproducibility

Extracted by `scripts/export_human_label_dist.py` (or the inline extraction
in the commit that added this file) from the canonical ChaosNLI JSONL.
No randomness. Deterministic given the same source JSONL.
