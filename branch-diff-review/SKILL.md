
.

---
name: branch-diff-review
description: >
  Reviews the diff between the current branch and a base ref
  (branch or tag, e.g. main, v1.2.3) for introduced bugs,
  optimization opportunities, and missed modifications. Triggered
  by keywords like 'branch review', 'diff review', 'review branch',
  'compare branch', 'tag review', 'diff tag', 'compare tag'.
---

# Branch / Tag Diff Review

When asked to review the current branch's changes against a base ref (a branch **or** a tag), perform the following steps. Throughout this skill the variable `<base-ref>` refers to whichever ref the user (or auto-detection) picked — branches and tags are interchangeable for the git commands used below.

## 1. Determine Base Ref

1. If the user specified a base ref (e.g. `main`, `master`, `develop`, or a tag like `v1.2.3`, `release/2024-09`), use that directly. Detect tag-vs-branch by running `git show-ref --verify refs/tags/<base-ref>` or `git rev-parse --verify <base-ref>` — both refs work identically with the diff commands in step 2, so no further branching is needed.
2. Otherwise, auto-detect. Try each of the following in order and use the first that resolves:
   - Run `git remote show origin` to find the default branch (`HEAD` branch).
   - Try `main`, then `master`.
   - If the user is on a release/hotfix branch and none of the above match, check `git tag --sort=-version:refname | head -5` and pick the most recent semver tag (skip prereleases) as the base ref. Mention this choice explicitly in the report.
3. Run `git merge-base HEAD <base-ref>` to find the merge base. This works for both branches and tags.
4. If `git merge-base HEAD <base-ref>` fails because `<base-ref>` is an **ancestor** of `HEAD` (i.e. `HEAD` is ahead of `<base-ref>` on the same lineage — common when reviewing against an older tag), the merge base is `<base-ref>` itself. Verify with `git merge-base --is-ancestor <base-ref> HEAD` and use `<base-ref>` directly in that case.

## 2. Gather Change Information

1. Run `git log --oneline <base-ref>..HEAD` to see all commits on the current branch since `<base-ref>`.
2. Run `git diff <base-ref>...HEAD` (triple-dot: diff from merge base to HEAD) to get the full diff.
3. List changed files: `git diff --name-only <base-ref>...HEAD`.
4. For new files, read them directly.

> Note: For tag-vs-tag reviews (e.g. comparing `v1.0.0..v1.1.0`), the same `git diff <tag-a>...<tag-b>` syntax applies — adapt `HEAD` to the second tag.

## 3. Bug Check

Review every changed line for:

- **Undefined variables / name errors**: references to variables, functions, or classes that don't exist or aren't imported. Check both new code and any removed references to existing symbols.
- **Type mismatches**: function calls with wrong argument types or mismatched shapes in PyTorch tensor operations.
- **Missing imports**: any symbol used but not imported; check the existing imports in the file.
- **API misuse**: incorrect usage of PyTorch / transformer_engine APIs (e.g., wrong argument names, missing required arguments, deprecated APIs).
- **Device / dtype issues**: tensors on wrong device or with wrong dtype, especially `.to(device)` or `.cuda()` calls that should be NPU-aware (`npu()`).
- **Async / sync bugs**: missing `.wait()`, `.synchronize()`, or incorrect stream handling.
- **Resource leaks**: opened files, streams, or handles not properly closed.
- **Error handling**: bare `except:`, overly broad `except Exception`, missing `finally` for cleanup.
- **Race conditions**: shared state without synchronization in multi-stream or multi-process code.
- **Off-by-one / boundary errors**: loop bounds, slice indices, tensor shape mismatches.
- **Hardcoded NPU-specific values**: paths, device IDs, or constants that should be configurable.
- **Merge conflicts**: leftover conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`) in the diff.

## 4. Optimization Check

Review changed code for:

- **Redundant operations**: unnecessary `.clone()`, `.detach()`, or repeated tensor-to-device transfers.
- **In-place opportunity**: operations that could use in-place variants (`.add_()` vs `.add()`) to reduce memory.
- **Recomputation vs memory tradeoff**: operations that are recomputed but could be cached, or vice versa.
- **Unnecessary Python loops**: loops over tensor elements that could be vectorized with PyTorch operations.
- **Gradient computation**: tensors that don't need gradients but have `requires_grad=True`.
- **Sequential vs fused ops**: multiple sequential operations that could be fused (e.g., `scale + add` instead of separate ops).
- **Unused computation**: variables computed but never used.
- **Import optimization**: unused imports or imports that could be deferred to reduce startup time.
- **NPU-specific optimization**: operations that could use NPU-specific kernels or avoid host-device synchronization.
- **Repeated work**: same computation performed across multiple commits or in a loop that could be hoisted.

## 5. Missed Modification Check

- **Incomplete refactoring**: old function/variable names still referenced after renaming. Compare across all changed files.
- **Missing stubs**: new public functions/classes without corresponding `__init__.py` exports.
- **Missing test coverage**: new functionality without corresponding test changes. Check if test files exist for the changed modules.
- **TODO / FIXME / HACK left in code**: markers left behind that should be addressed.
- **Debug code**: left-in `print()`, `breakpoint()`, or debug assertions.
- **Missing type hints**: public APIs without type annotations when the project convention uses them.
- **Forgotten files**: `__pycache__/`, `.pyc`, `.o`, or other build artifacts that should be in `.gitignore`.
- **Inconsistent naming**: naming that doesn't follow project conventions (snake_case for Python, etc.).
- **Missing copyright headers**: new files without the project's standard copyright header.
- **Skeleton / placeholder code**: `pass`, `raise NotImplementedError`, or `...` left in place unintentionally.
- **Cross-file inconsistencies**: changes in one file that should have corresponding changes in related files (e.g., config changes without schema updates, API changes without caller updates).
- **Commit message issues**: commits that don't follow project conventions (check `git log` output from step 2.1).

## 6. NVTE / Upstream Cross-Reference Check

The Ascend fork derives from NVIDIA Transformer Engine (NVTE). For each new or modified symbol under `transformer_engine/pytorch/`, `transformer_engine/common/recipe/`, or `transformer_engine/jax/`, fetch the corresponding file from `https://raw.githubusercontent.com/NVIDIA/TransformerEngine/main/<path>` (or a tagged release like `v2.16.1` if `main` does not resolve) and diff against the local implementation. Treat the upstream version as a reference, not as gospel — the Ascend fork legitimately diverges for NPU-specific behavior — but flag:

- **Missing attribute / method**: NVTE defines a hook the fork omits (e.g. `_persistent_state_buffers`, `inherit_state_from`, `_handle_delayed_scaling_requests` validation, `_has_delayed_scaling_state`).
- **Behavior divergence without rationale**: the fork silently loosens a precondition check (e.g. skips `dtype` / `shape` validation, accepts `None` where NVTE rejects).
- **NVTE bug that was carried over**: when the upstream itself is buggy, the fork should still mirror the fix path (or document why not).
- **NVTE bug that was newly introduced**: when the fork diverges from upstream and the divergence is worse, not better.

Useful entry points:

- `transformer_engine/pytorch/quantization.py` (NVTE consolidated `state.py` + `manager.py` + `utils.py` + `__init__.py`).
- `transformer_engine/pytorch/module/base.py` for `RecipeState.create` call sites and `set_meta_tensor`.
- `transformer_engine/common/recipe/` for `Recipe` subclasses.

If the fork has its own divergence rationale documented in code comments, leave it alone; otherwise recommend aligning.

## 7. Pseudo-Bug / Pseudo-Optimization Identification (CRITICAL)

Before finalizing any **BUG** / **Optimization** finding, validate it against the checklist below. Past reviews have surfaced recurring false positives that waste author time and erode trust in the review. Every finding MUST pass at least one of the "real signal" gates; otherwise, mark it `⚠️ Likely pseudo` and either downgrade or retract.

### 7.1 Markers that often indicate a pseudo finding

- **The code path is unreachable / dead**: e.g. recommending "fix" for a class attribute that no caller ever reads (verify with `grep` over the whole repo before reporting "missing `self.foo = bar`").
- **The "fix" violates a documented contract**: e.g. asserting that a `__post_init__` does not run, when the base class defines one and the dataclass auto-calls it (verify with a 5-line `exec`-based stub rather than reasoning from memory).
- **The behavior is intentionally lazy / deferred and the test suite enforces it**: e.g. `qfactory=None` being accepted at `Recipe(...)` time but rejected at `CustomRecipeState(...)` time — if `tests/` cover this exact path with `# type: ignore[arg-type]`, it is by design, not a bug.
- **The optimization has no measurable impact at the call site**: e.g. suggesting O(N) -> O(N²) -> set dedup when `num_quantizers` is bounded at 6-9 by the framework's GEMM contract.
- **The "missing call" is unreachable in the current control flow**: e.g. a hook designed for a feature flag that defaults off, or a method only called when `_persistent_state_buffers` is non-empty.
- **The finding duplicates an existing test assertion**: check `tests/` for the symbol before claiming "no test coverage".
- **The finding relies on a guess about library internals**: e.g. "Python dataclass subclasses don't inherit `__post_init__`" — verify the exact `@dataclass` semantics empirically with a minimal repro before publishing.
- **The diff line was already present on the base ref**: blame the line. Pre-existing bugs in untouched code are out of scope unless the PR explicitly modifies adjacent code (and even then, mark as `MISS` not `BUG`).

### 7.2 Validation gates — every finding MUST pass at least one

| Gate | How to satisfy |
|---|---|
| **Empirical repro** | Write a ≤30-line Python stub that demonstrates the bug (no pytest, no torch dep where avoidable). Examples: build a fake `_D` namespace, exec the dataclass body, assert the behavior. |
| **Direct cross-reference** | The upstream NVTE file shows the same line working differently, or the test suite asserts the opposite behavior. |
| **Caller trace** | `grep -rn '<symbol>'` over the whole repo shows the affected code path is actually invoked. |
| **Test enforcement** | A test in `tests/` already fails or would fail after the suggested fix. |
| **Author intent doc** | A code comment / docstring / commit message explicitly states the current behavior is intended. |

If none of the gates can be satisfied in under two minutes of investigation, the finding is almost certainly pseudo. Downgrade to `⚠️ Likely pseudo` or retract.

### 7.3 Workflow for high-risk claims

1. **State assumption**: write down what you believe happens (e.g. "`MXFP4BlockScaling.__post_init__` does not call `super().__post_init__()` so the base assertion is skipped").
2. **Pick the cheapest validation**: usually a `python -c` stub using `types.SimpleNamespace` for torch.
3. **Run it. Do not skip this step.**
4. **Record the output verbatim** in the report — readers must be able to reproduce.
5. **Revise the finding** based on what the validation actually showed.

The 2026-06-26 review of `custom_recipe` PR caught three pseudo-bugs this way (dataclass `__post_init__` inheritance, `qfactory=None` "delayed" validation, `state.device` "missing" attribute). Documenting the validation steps prevents the same mistakes recurring.

## 8. Summary Statistics

Before the detailed report, provide a Chinese summary:

```
## Summary
- Base ref: <base> (branch: <name> / tag: <name>)
- Commits: <count>
- Files changed: <count>
- Insertions: <+, -> deletions: <-, ->
- **BUGS**: <count>
- **Optimizations**: <count>
- **Missed Modifications**: <count>
- **Withdrawn after validation**: <count> (see §7)
```

## 9. Report

Summarize findings grouped by category. For each issue, include the file path, line number, and a concrete suggestion. Prioritize by severity: **BUG** > **Optimization** > **Missed Modifications**. Tag every finding with the validation gate(s) that satisfied it (e.g. `[repro]`, `[caller-trace]`, `[nvte-ref]`), and tag pseudo findings as `[⚠️ Likely pseudo — see §7]` so the author can triage quickly.

**Language**: Output the report in Chinese (中文) by default. The summary statistics, section headings, BUG / Optimization / Missed Modifications entries, file paths, line numbers, and concrete fix suggestions should all be written in Chinese. Code identifiers, file names, line numbers, and English-only technical terms (e.g. `Linear`, `forward_dw`, `quantize_weight`, `fsdp_group`) may be kept as-is in their original form.
