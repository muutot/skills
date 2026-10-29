# Project Maintenance Workflow

Generic workflow. It needs no project-specific facts and is ready to use as
soon as the skill is adopted; examples marked `<!-- FILL IN -->` should be
replaced with the project's real artifacts.

## 1. Establish the baseline

1. Read `SKILL.md`, this workflow, and the references selected for the task completely.
2. Read the project's TODO/roadmap file (`<!-- FILL IN: e.g. TODO.md -->`) as UTF-8 and inspect `git status --short --branch`, recent commits, relevant source, tests, and generated/runtime artifacts.
3. Preserve unrelated user changes. Never reset, overwrite, reformat, or stage them to simplify the task.
4. Prefer `rg`/`rg --files` and exact symbol searches. Do not trust file names, comments, stale counts, or roadmap intent as implementation evidence.

## 2. Audit TODOs from evidence

Classify every audited item as one of:

- `complete`: direct implementation evidence plus verification covers the full wording.
- `partial`: meaningful behavior exists, but at least one named requirement, failure path, or platform is missing.
- `unverified`: implementation may exist, but required runtime, visual, platform, performance, packaging, or release evidence is absent.
- `not started`: no meaningful implementation evidence exists.

Only change `[ ]` to `[x]` for `complete`. Tests prove only what they exercise. A placeholder, mock, configuration field, optimistic UI update, compiled stub, or unconnected module is not completion.

When an item is broad, retain it as a parent and add independently verifiable child checkboxes. Merge duplicates by keeping the clearest canonical wording and preserving unique acceptance criteria underneath it. If completed work has no matching item, add a concise checked item whose wording can be verified directly.

## 3. Choose the next minimal unit

Prefer this order unless direct evidence justifies another order:

1. data loss, privacy, corruption, lifecycle leaks, and broken core flows;
2. persistence errors and cross-layer contract mismatches;
3. exposed UI whose backend/platform behavior is absent or misleading;
4. configuration consistency, accessibility, and interaction reliability;
5. performance, packaging, documentation, and optional enhancements.

Choose the smallest end-to-end behavior that makes one requirement objectively better and can be committed independently.

## 4. Trace contracts before editing

For each affected value or action, trace the complete path that exists in scope. Adapt the shape to the project; the principle is: every surface a value crosses must stay aligned.

```text
UI → component callback/state store → service/API wrapper
   → backend command/handler → repository/storage/worker/platform adapter
   → database/files/external service → event/result → rendered state
```

List all contract surfaces that must remain aligned: types, defaults, validation, serialization names, migrations, events, cleanup, shutdown, i18n, tests, and references. Do not expand the implementation beyond the selected minimal unit.

## 5. Apply the UI style gates

For any UI/CSS change, read `ui-style-guide.md`.

Before changing styles:

1. inspect the project's primary surface only to understand the approved visual language;
2. compare all surfaces that use the same primitive;
3. identify whether the rule belongs in the theme tokens, shared CSS, parent shell, or one component;
4. reuse semantic variables and established patterns;
5. make one narrow consistency pass and verify it structurally and, when possible, visually.

Do not promote a niche exception into a general rule. Record newly discovered local exceptions in `niche_ui_style.md` for review instead of copying them or silently "standardizing" them during unrelated work.

## 6. Isolate parallel work

- Assign non-overlapping subsystems or read-only audits.
- State explicit file ownership for every editing agent.
- Do not let two agents modify shared files concurrently: the TODO file, root entry points, translations, shared CSS, or the same component.
- Let the primary agent integrate shared files, resolve contract edges, and run final verification.

## 7. Verify in proportion to risk

- During bug remediation, run only the unit tests relevant to each minimal fix; do not run full suites between fixes.
- After all requested fixes are complete, run the full verify gate once (`<!-- FILL IN: the project's verify command -->`). Do not repeat it unless later edits or failures require revalidation.
- Keep per-commit formatting, Git hooks, and the documentation currency gate.
- Inspect rendered/runtime behavior for layout, theme, focus, multi-window, platform, or OS integration claims; static checks alone are insufficient.
- Treat platform-gated code as unverified locally. Anything behind a platform `#[cfg]`/build tag is not compiled by a local run on another OS; after touching such code, the matching CI job is the only real gate — read its result, and do not treat a green local run as coverage.
- Prefer a runnable harness over manual steps when a claim (format handling, integration behavior) recurs; keep harness scripts in the repository and document what they do and do not cover.

Report skipped checks and why. Do not convert missing evidence into a passing claim.

## 8. Run the documentation currency gate before every commit

1. Inspect `git diff --cached --name-only` and `git diff --cached`.
2. Compare the staged change with every reference category listed in `SKILL.md`.
3. Update the matching reference in the same commit when architecture, contracts, defaults, patterns, styles, verification, or known limitations changed.
4. Update `SKILL.md` only when stable workflow, routing, or non-negotiable principles changed; keep module detail in references.
5. If no documentation file needs a change, explicitly record that conclusion in the pre-commit/handoff summary. Do not mechanically touch a file.
6. Validate that newly documented facts are based on current source rather than intent, TODO wording, or a previous reference.

A commit is not ready while its skill/reference guidance is knowingly stale.

## 9. Commit a minimal verified unit

1. Stage only the intended files or hunks.
2. Review the staged diff for unrelated changes, secrets, generated artifacts, accidental formatting, and stale reference claims.
3. Commit one independently explainable feature, fix, style pass, audit update, or skill/reference update.
4. Update matching TODO checkboxes in the same feature commit when practical and fully evidenced; use a separate audit commit for broad historical corrections.
5. Recheck status after the commit. Do not postpone a safe minimal commit merely because the roadmap remains unfinished.
