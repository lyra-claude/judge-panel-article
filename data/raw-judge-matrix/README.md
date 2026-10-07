# Raw Judge Vote/Error Matrices

## Provenance

**Source:** Li, Yu, Li (2024), "32judges-votes",
arXiv [2609.21277](https://arxiv.org/abs/2609.21277), **CC BY 4.0**.

This is NOT Lyra's data. These files are a convenience
re-serialization of the disaggregated JSONL vote files in the
chaosnli-neff repository, regenerated deterministically (no
randomness). The canonical source files are the per-judge JSONL
files under `chaosnli-neff/repo/datasets/chaosnli-{subset}/votes/baseline/`.

## Subsets

### alphanli

- Final matrix shape: **995 items × 32 judges**
- Original item count: 1000
- Items dropped (parse_fail): 5 (5 parse_fail cells)
- Labels: ['1', '2']

### snli

- Final matrix shape: **1000 items × 32 judges**
- Original item count: 1000
- Items dropped (parse_fail): 0 (0 parse_fail cells)
- Labels: ['e', 'n', 'c']

### mnli_m

- Final matrix shape: **999 items × 32 judges**
- Original item count: 1000
- Items dropped (parse_fail): 1 (1 parse_fail cells)
- Labels: ['e', 'n', 'c']

## Files

Each subset directory contains two CSVs:

- **votes_matrix.csv** — rows = items, columns =
  `[item_uid, gold, j01, j02, ..., j32]`. The `jNN` columns contain
  the judge's raw label vote (the label string, e.g. `"1"` / `"2"`
  for alphaNLI, or `"e"` / `"n"` / `"c"` for SNLI/MNLI-m).

- **error_matrix.csv** — same shape, but entries are binary: `1` if
  the judge's label differs from the gold label (judge is wrong),
  `0` if correct.

## Error entry definition

Error is defined as: `judge_label_index != gold_label_index`, where:

- Gold = `majority_label` field from the upstream ChaosNLI JSONL
  (Li et al.'s recorded tie-breaking; never recomputed from argmax).
- Items with at least one `parse_fail=true` entry across any judge
  are **dropped entirely** (`failure_policy="drop-items"`), matching
  the definition used in `scripts/judge_main_effect.py` and the
  existing analysis pipeline.

## Judge filename → column mapping

Columns `j01`–`j32` correspond to the baseline vote files sorted
lexicographically by filename stem (the ordering `votes_io.load_panel`
uses internally).

### alphanli judge mapping

| Column | Filename stem |
|--------|---------------|
| j01 | `doubao18` |
| j02 | `doubao20pro` |
| j03 | `dsv32` |
| j04 | `dsv4flash` |
| j05 | `dsv4pro` |
| j06 | `gem25pro` |
| j07 | `gem31pro` |
| j08 | `gem36flash` |
| j09 | `gem37flash` |
| j10 | `glm5` |
| j11 | `glm51` |
| j12 | `glm52` |
| j13 | `glm53` |
| j14 | `gpt41` |
| j15 | `gpt54` |
| j16 | `gpt56sol` |
| j17 | `gpt56terra` |
| j18 | `grok45` |
| j19 | `grok46` |
| j20 | `haiku45` |
| j21 | `kimik25` |
| j22 | `kimik26` |
| j23 | `kimik27code` |
| j24 | `kimik3` |
| j25 | `minimaxm3` |
| j26 | `o4mini` |
| j27 | `opus5` |
| j28 | `qwen35plus` |
| j29 | `qwen37plus` |
| j30 | `qwen38max` |
| j31 | `qwen3max` |
| j32 | `sonnet46` |

### snli judge mapping

| Column | Filename stem |
|--------|---------------|
| j01 | `doubao18` |
| j02 | `doubao20pro` |
| j03 | `dsv32` |
| j04 | `dsv4flash` |
| j05 | `dsv4pro` |
| j06 | `gem25pro` |
| j07 | `gem31pro` |
| j08 | `gem36flash` |
| j09 | `gem37flash` |
| j10 | `glm5` |
| j11 | `glm51` |
| j12 | `glm52` |
| j13 | `glm53` |
| j14 | `gpt41` |
| j15 | `gpt54` |
| j16 | `gpt56sol` |
| j17 | `gpt56terra` |
| j18 | `grok45` |
| j19 | `grok46` |
| j20 | `haiku45` |
| j21 | `kimik25` |
| j22 | `kimik26` |
| j23 | `kimik27code` |
| j24 | `kimik3` |
| j25 | `minimaxm3` |
| j26 | `o4mini` |
| j27 | `opus5` |
| j28 | `qwen35plus` |
| j29 | `qwen37plus` |
| j30 | `qwen38max` |
| j31 | `qwen3max` |
| j32 | `sonnet46` |

### mnli_m judge mapping

| Column | Filename stem |
|--------|---------------|
| j01 | `doubao18` |
| j02 | `doubao20pro` |
| j03 | `dsv32` |
| j04 | `dsv4flash` |
| j05 | `dsv4pro` |
| j06 | `gem25pro` |
| j07 | `gem31pro` |
| j08 | `gem36flash` |
| j09 | `gem37flash` |
| j10 | `glm5` |
| j11 | `glm51` |
| j12 | `glm52` |
| j13 | `glm53` |
| j14 | `gpt41` |
| j15 | `gpt54` |
| j16 | `gpt56sol` |
| j17 | `gpt56terra` |
| j18 | `grok45` |
| j19 | `grok46` |
| j20 | `haiku45` |
| j21 | `kimik25` |
| j22 | `kimik26` |
| j23 | `kimik27code` |
| j24 | `kimik3` |
| j25 | `minimaxm3` |
| j26 | `o4mini` |
| j27 | `opus5` |
| j28 | `qwen35plus` |
| j29 | `qwen37plus` |
| j30 | `qwen38max` |
| j31 | `qwen3max` |
| j32 | `sonnet46` |

## Reproducibility

Run `scripts/export_raw_matrix.py` from the `judge-panel-article`
repository root to regenerate these files from the JSONL sources.
The script has no randomness and is fully deterministic.

## What is NOT in these files

These matrices are raw input data only. No conclusions about n_eff,
correlation, statistical independence, or any derived quantities are
stated here. Those analyses are in the paper and the scripts.

