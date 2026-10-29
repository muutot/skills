---
name: branch-diff-review
description: >
  Reviews the diff between the current branch and a base ref
  (branch or tag, e.g. main, v1.2.3) for introduced bugs,
  optimization opportunities, and missed modifications. Triggered
  by keywords like 'branch review', 'diff review', 'review branch',
  'compare branch', 'tag review', 'diff tag', 'compare tag'.
compatibility: opencode, claude, codex
---

# Branch / Tag Diff Review

Review the current branch's changes against a base ref (a branch **or** a tag). `<base-ref>` below refers to whichever ref the user specified or was auto-detected — branches and tags are interchangeable for every git command used here.

## 1. Determine Base Ref

1. **User-specified**: use it directly (`main`, `develop`, `v1.2.3`, `release/2024-09`, ...).
2. **Auto-detect**, in order:
   - `git remote show origin` → default `HEAD` branch.
   - Fall back to `main`, then `master`.
   - On a release/hotfix branch where none of the above resolve: pick the most recent stable semver tag via `git tag --sort=-version:refname` (skip prereleases), and state this choice explicitly in the report.
3. Run `git merge-base HEAD <base-ref>`.
   - If it succeeds, that commit is the review base. Note: when `<base-ref>` is an ancestor of `HEAD` (e.g. reviewing against an older tag on the same lineage), merge-base returns `<base-ref>` itself — expected behavior, not an error.
   - If it fails, verify the ref exists: `git rev-parse --verify <base-ref>`.

### 1.1 Edge Cases

- **Detached HEAD** (`git symbolic-ref -q HEAD` fails): there is no "current branch". Ask the user which ref to review against; if they don't answer, use the ref that `HEAD` was detached from (check `git reflog -1` for `checkout: moving from <ref>`) and say so in the report.
- **No origin remote** (`git remote show origin` fails): skip step 2's first probe, fall back to `main`/`master`, then tags as usual. Never invent a remote.
- **Shallow clone** (`git rev-parse --is-shallow-repository` returns `true`): merge-base may fail with "refusing to work" or return a wrong base because history is truncated. Attempt `git fetch origin --unshallow <base-ref>` once; if that fails (offline/permission), tell the user the base may be inaccurate and mark the finding set with a caveat in §8 Notes.
- **Base ref not local** but exists on origin (e.g. fresh clone of a feature branch): resolve via `git fetch origin <base-ref>` then use `origin/<base-ref>` as `<base-ref>` throughout.

## 2. Gather Change Information

Run once, reuse everywhere:

```
git log --oneline <base-ref>..HEAD          # commits + commit-message conventions
git diff --shortstat <base-ref>...HEAD      # insertions / deletions totals (for §8)
git diff --name-status <base-ref>...HEAD    # changed files + A/M/D status (new files → read fully)
git diff <base-ref>...HEAD                  # full diff (triple-dot = merge base → HEAD)
```

> Tag-vs-tag reviews (e.g. `v1.0.0..v1.1.0`) use identical syntax with the second tag in place of `HEAD`.

### 2.0 Scope Restriction

If the user restricts the review scope (e.g. "只审 `transformer_engine/pytorch/module`", "only tests/"), apply the filter to the `--name-status` list **before** batching:

```
git diff --name-status <base-ref>...HEAD -- <scope-path>
```

Rules:
- Only files under the scope path enter the findings checklist (§3–5).
- Cross-file checks (§5) may still read files **outside** the scope when a scoped change references them (e.g. renamed symbol called from an unscoped file) — but report the finding anchored to the in-scope file.
- State the effective scope and excluded file count in the §8 Summary Notes so out-of-scope silence is not mistaken for a clean bill.

### 2.1 Large-Diff Batching

If the diff exceeds **~50 files or ~3000 changed lines**, do NOT feed it through whole — review in batches:

1. Group changed files by top-level module (e.g. `transformer_engine/pytorch/module/`, `tests/`, `docs/`).
2. Review one group at a time, highest-risk first: `pytorch/` core modules > `recipe/` > `tests/` > docs/config.
3. Cross-file checks (§5 incomplete refactoring / cross-file inconsistency) run only after all batches complete, using the collected `--name-status` list.
4. State the batching plan (groups + order) before starting so the user can interrupt or reprioritize.

## 3–5. Findings Checklist

Review every changed line against these three categories.

### 3. Bugs

- **Undefined symbols**: variables/functions/classes referenced but nonexistent or unimported — including removed code still referenced elsewhere.
- **Type / shape mismatches**: wrong argument types, mismatched tensor shapes.
- **API misuse**: incorrect PyTorch / transformer_engine usage (wrong kwargs, missing required args, deprecated APIs).
- **Device / dtype**: tensors on wrong device or dtype; `.to(device)` / `.cuda()` calls that should be NPU-aware (`npu()`).
- **Async bugs**: missing `.wait()` / `.synchronize()`, incorrect stream handling.
- **Resource leaks**: files, streams, or handles not closed.
- **Error handling**: bare `except:` or overly broad `except Exception`; missing `finally` cleanup.
- **Race conditions**: shared state without synchronization across streams/processes.
- **Boundary errors**: loop bounds, slice indices, shape arithmetic.
- **Hardcoded values**: NPU paths, device IDs, or constants that should be configurable.
- **Conflict markers**: leftover `<<<<<<<` / `=======` / `>>>>>>>`.

### 4. Optimizations

- **Redundant ops**: needless `.clone()` / `.detach()`, repeated host↔device transfers.
- **In-place variants**: `.add_()` vs `.add()` where memory matters.
- **Vectorization**: Python loops over tensor elements replaceable with tensor ops.
- **Fusion**: sequential elementwise ops that can be combined into one.
- **Gradient overhead**: tensors with `requires_grad=True` that never need gradients.
- **Dead computation**: computed-but-unused values; unused or deferrable imports.
- **Recompute vs cache**: values recomputed in loops that could be hoisted/cached (or vice versa for memory).
- **NPU-specific**: ops replaceable with NPU-fused kernels; avoidable host-device syncs.

### 5. Missed Modifications

- **Incomplete refactoring**: old names still referenced after a rename (check across all changed files).
- **Missing exports**: new public functions/classes absent from `__init__.py`.
- **Missing tests**: new functionality without test updates.
- **Leftovers**: TODO/FIXME/HACK markers, debug `print()` / `breakpoint()` / debug asserts, skeleton `pass` / `raise NotImplementedError` / `...`.
- **Forgotten artifacts**: `__pycache__/`, `.pyc`, `.o`, etc. that belong in `.gitignore`.
- **Cross-file inconsistency**: config change without schema update, API change without caller update.
- **Convention violations**: naming (snake_case), missing type hints, missing copyright headers on new files, commit messages off-convention (from §2 log).

## 6. NVTE / Upstream Cross-Reference Check

This Ascend fork derives from NVIDIA Transformer Engine (NVTE). For each new/modified symbol under `transformer_engine/pytorch/`, `transformer_engine/common/recipe/`, or `transformer_engine/jax/`, fetch the upstream counterpart and compare. Upstream is a reference, not gospel — the fork legitimately diverges for NPU behavior. Flag only:

- **Omitted hook/attribute**: NVTE defines something the fork drops entirely (e.g. `_persistent_state_buffers`, `inherit_state_from`).
- **Silent loosening**: fork skips validation NVTE performs, or accepts `None` where NVTE rejects — without documented rationale.
- **Carried-over upstream bug**: fork faithfully mirrors an upstream bug instead of fixing or documenting it.
- **Divergence regression**: fork diverges from upstream and the divergence is strictly worse.

Useful entry points: `transformer_engine/pytorch/quantization.py` (consolidated state/manager/utils), `transformer_engine/pytorch/module/base.py` (`RecipeState.create`, `set_meta_tensor`), `transformer_engine/common/recipe/` (`Recipe` subclasses). These reflect the fork layout at authoring time — re-verify they exist before citing them; if a path has moved, locate the counterpart by symbol name instead of trusting this list.

### 6.1 Fetch Fallback Order

Try each source in order; stop at the first that works:

1. **Raw GitHub**: `https://raw.githubusercontent.com/NVIDIA/TransformerEngine/main/<path>`.
2. **Tagged release**: same URL with a known tag (e.g. `v2.16.1`) if `main` 404s or the fork targets an older API.
3. **Local upstream clone**: check for a sibling clone of NVTE (e.g. `../TransformerEngine`) or any local checkout, and read files from it.
4. **Give up gracefully**: if none are reachable (offline / rate-limited), skip §6 entirely, mark every would-be cross-reference finding as `[nvte-unverified — offline]`, and note "§6 skipped: upstream unreachable" in the §8 Summary. Findings whose only validation gate would have been `nvte-ref` cannot pass §7 in this state — downgrade them to `⚠️ Likely pseudo` unless another gate covers them. Do not fabricate upstream behavior from memory.

If the divergence rationale is already documented in code comments, leave it alone; otherwise recommend aligning.

### 6.2 Known-Divergences Ledger

Before flagging any divergence, check `known-divergences.md` (this skill's directory). If the symbol/file has an entry there, **skip it entirely** — the divergence is already confirmed intentional.

When a review concludes that a divergence IS intentional (via author-intent doc or user confirmation), append it to the ledger in the required format so future reviews never re-flag it. The ledger turns one-off review conclusions into a cumulative asset; keep entries atomic and dated.

## 7. Pseudo-Finding Identification (CRITICAL)

Every BUG / Optimization finding must pass at least one gate before being reported; otherwise downgrade to `⚠️ Likely pseudo` or withdraw.

### 7.1 Validation Gates

| Gate | How to satisfy |
|---|---|
| **Empirical repro** | ≤30-line Python stub demonstrating the bug (no pytest/torch dep preferred) |
| **Direct cross-reference** | Upstream shows different implementation, or a test asserts the opposite |
| **Caller trace** | Repo-wide `grep` proves the affected path is actually invoked |
| **Test enforcement** | A test fails now, or would fail after applying the suggested fix |
| **Author intent doc** | Comment/docstring/commit states current behavior is intended |

No gate satisfiable within ~2 minutes → `⚠️ Likely pseudo`.

### 7.2 False-Positive Signals

- **Dead path**: symbol never called (verify with grep before reporting)
- **Contract illusion**: behavior actually comes from base class / decorator / metaclass
- **Zero-benefit optimization**: no measurable impact at any real call site
- **Comment-only match**: hit exists only inside `#` comments or docstrings
- **Pre-existing on base ref**: issue predates this diff → out of scope
- **Already tested**: `tests/` already asserts the "missing" behavior

### 7.3 Worked Examples

**✅ Valid finding (passes gates):**

> `transformer_engine/pytorch/module/linear.py:212` — `_quantizer.update_scale()` is called after the early-return when `x.requires_grad=False`, so inference-mode tensors never update their scale. **[caller-trace]** `update_scale` is invoked from `Linear.forward` on every call site found in repo (12 hits, all live); **[test enforcement]** removing the early-return makes `tests/test_quantization.py::test_inference_scale_update` pass.

*Why valid*: two independent gates, concrete file/line, and a test that proves the fix.

**❌ Pseudo finding (must be downgraded or withdrawn):**

> "Missing validation for `None` input in `RecipeState.create` — upstream NVTE raises."

*Why pseudo*: no caller trace showing `create` is ever called with `None` (**dead path / contract illusion** — a base-class factory may already reject it); no repro; upstream claim not verified against a fetched source (**comment-only match if based on memory**). Downgrade to `⚠️ Likely pseudo` unless a ≤30-line repro or a fetched upstream diff confirms it.

The pattern to internalize: a finding states *what*, *where*, *why it breaks*, and *which gate(s) prove it* — anything less is speculation.

## 8. Summary Statistics

Before the detailed report:

```
## Summary
- Base ref: <base> (branch: <name> / tag: <name>)
- Commits: <count>
- Files changed: <count>
- Insertions: <+N> deletions: <-N>
- **BUGS**: <count>
- **Optimizations**: <count>
- **Missed Modifications**: <count>
- **Withdrawn after validation**: <count> (see §7)
- Notes: <e.g. "§6 skipped: upstream unreachable"; "reviewed in N batches: <groups>">
```

## 9. Report

Group findings by category, prioritized **BUG > Optimization > Missed Modification**. Within **Bugs**, further order by severity so the author can fix top-down first:

| Severity | Criteria | Examples |
|---|---|---|
| **P0** | Data corruption, crash, silent wrong results in a live code path | wrong dtype silently truncates quantized weights; missing sync corrupts stream output |
| **P1** | Functional error on a reachable path — wrong behavior but no corruption | validation skipped that lets bad config through; renamed symbol still referenced |
| **P2** | Robustness / boundary hardening on unlikely paths | off-by-one on degenerate input; bare `except:` masking errors |

Each finding must include: file path, line number, concrete fix suggestion, severity tag for bugs (`[P0]`/`[P1]`/`[P2]`), and its validation-gate tag (e.g. `[repro]`, `[caller-trace]`, `[nvte-ref]`). Pseudo findings get `[⚠️ Likely pseudo — see §7]` so the author can triage quickly.

**Language**: output in Chinese (中文) by default — headings, findings, and fix suggestions included. Code identifiers, file names, and English-only technical terms (e.g. `Linear`, `forward_dw`, `fsdp_group`) stay as-is.
