---
name: dev
description: Project-agnostic development framework for any repository. Use for repository orientation, TODO audits, feature and fix work, frontend-backend or cross-layer contract changes, UI/style work, verification, and minimal Git commits. Enforces direct-evidence completion, style gates, reference routing, and a mandatory skill/reference currency check before every commit. Ships with reference templates that a new project fills in with its own facts.
---

# Project Development Framework

This skill is a framework, not a knowledge base. It contains the stable
workflow; the project-specific facts live in `references/` and are filled in
by the adopting project. Until a reference is filled in, treat it as a
template placeholder — do not invent facts to fill it.

## Adopting this skill

1. Copy this skill into the target repository (for example
   `.claude/skills/dev/`, `.agents/skills/dev/`, or `.opencode/skills/dev/`).
2. Fill in `references/project-structure.md` first — routes, directories,
   runtime surfaces, and the authoritative entry points.
3. Fill in the remaining templates as their subsystems stabilize:
   `architecture.md`, `data-contracts.md`, `ui-style-guide.md`,
   `verification.md`, `niche_ui_style.md`.
4. Replace the placeholders in "Verification commands" and "Commit message
   format" below with the project's real commands and convention.
5. Delete any template section the project does not need; do not keep empty
   scaffolding that pretends to be knowledge.

## Start every task

1. Read [references/maintenance-workflow.md](references/maintenance-workflow.md) completely before changing the repository.
2. Inspect `git status --short --branch`, recent commits, the project's TODO/roadmap file, and the exact source and tests in scope. Preserve unrelated user changes.
3. Select the relevant references from the routing table below and read each selected file completely before editing its subsystem. A template reference means the project has not filled it in yet — verify against source instead.
4. Treat current source, tests, configuration, and rendered/runtime behavior as authoritative. References are navigation aids and must be corrected when evidence disagrees.
5. Define one independently verifiable feature, fix, audit, style pass, or documentation update for the next commit.

## Non-negotiable principles

- Check a TODO only when direct implementation evidence and proportionate verification cover its full wording. A stub, setting, UI shell, similarly named symbol, or untested platform file is not completion.
- Preserve the approved visual language of the project's primary surface. Do not redesign it unless the task explicitly requests a redesign.
- Apply the project's style gate before any UI/CSS change. Reuse project-wide semantic variables and shared primitives; never copy a local exception.
- Protect user data first. Be conservative around migrations, cleanup, and derived or cached data.
- Keep parallel ownership non-overlapping. The primary agent owns shared integration files and final verification.
- Commit one verified minimal unit at a time; never mix unrelated cleanup into the same commit.

## Mandatory documentation currency gate — every commit

Before **every** commit, inspect the staged diff and decide whether `SKILL.md` or any file under `references/` must change. This gate is required even when the answer is "no documentation update needed."

Update the matching reference in the same commit when the change affects any of these:

- routes, components, services, utilities, backend modules, or ownership boundaries;
- APIs, events, types, database/config schemas, defaults, or serialization;
- lifecycle, data-safety, background work, platform, or verification invariants;
- theme variables, project-wide styles, shared primitives, layout hierarchy, or an approved pattern;
- a recurring pitfall, workflow rule, or stable project preference.

Keep stable workflow and routing rules in `SKILL.md`. Put module-specific facts, signatures, examples, and style details in the relevant reference. Do not edit documentation merely to create churn, but never commit a known-stale skill or reference.

## Pre-commit hooks

If the project ships Git hooks (for example in `.githooks/`), document here which checks they enforce and how to enable them. The hooks watch the mechanical rules; they do not replace the judgement ones — TODO evidence, one verified unit per commit, the documentation decision itself, and rendered/runtime/platform verification remain human work.

## Reference router

| Task | Read before editing |
| --- | --- |
| Any repository change, TODO audit, verification, or commit | [maintenance-workflow.md](references/maintenance-workflow.md) |
| Repository orientation, routes, directories, runtime surfaces | [project-structure.md](references/project-structure.md) |
| Component/UI module behavior or ownership | [architecture.md](references/architecture.md) |
| Frontend/backend service layer, state, or API wrappers | [architecture.md](references/architecture.md) |
| API/IPC/event/type/database/config contract changes | [data-contracts.md](references/data-contracts.md) |
| Backend/background workers/storage/platform internals | [architecture.md](references/architecture.md) |
| Any UI or CSS change | [ui-style-guide.md](references/ui-style-guide.md) |
| Reviewing a local/niche UI exception | [niche_ui_style.md](references/niche_ui_style.md); treat it as a review queue, never as an approved pattern |
| Test, build, lint, or release commands | [verification.md](references/verification.md) |

Also read the focused project documents when relevant (for example `docs/PITFALLS.md` or equivalent).

## Cross-cutting change gates

When a change crosses a boundary, keep every surface of the contract aligned. Typical gates — enable the ones the project has, delete the rest:

- **API/IPC contract:** command/endpoint name, arguments, result, client wrapper, serialization casing, error handling, and tests move together.
- **Settings/config contract:** type, defaults, normalization/ranges, persistence, UI, cross-surface application, i18n, tests, and references as applicable.
- **Database contract:** schema/migration, row mapping, repository behavior, derived-data cleanup, recovery expectations, and tests.
- **i18n contract:** update every locale file and the type definitions together unless the string is intentionally non-localized and documented.
- **Worker/listener contract:** retain stop signals, join handles, unlisten functions, and the unified shutdown path.
- **Platform contract:** separate shared behavior from per-platform implementation. Code behind platform `#[cfg]` or build tags is not compiled locally on another OS — the matching CI job is the only real gate.
- **Visual contract:** type/build checks do not prove appearance. Use structural comparison and, when available, rendered/runtime inspection at the target window size and theme.
- **Async hydration contract:** a control bound to backend-loaded state must hydrate before it renders — never a placeholder default that the fetch later overwrites.

## Verification commands

<!-- FILL IN: replace with the project's real commands and delete the rest. -->

```powershell
# <type check>
# <frontend tests>
# <backend tests>
# <lint>
# <format check>
# <full verify gate>
```

During bug remediation, verify each minimal fix with only its relevant unit tests. After all requested fixes are complete, run the full verify gate once. If an environment prevents a required runtime, visual, platform, packaging, or performance check, report the missing evidence and leave the corresponding TODO unverified.

## Commit message format

<!-- FILL IN: keep the convention the project actually uses. The gitmoji contract below is one proven option. -->

Follow the project's established convention. A proven default is gitmoji:

```
<gitmoji> <type>[<scope>]: <message>
```

- **gitmoji**: single emoji indicating the change category.
- **type**: lowercase change type matching the emoji (`feat`, `fix`, `docs`, `refactor`, `style`, `perf`, `test`, `chore`).
- **scope**: optional, lowercase, in square brackets.
- **message**: concise imperative description. Pick one language policy and enforce it (the gitmoji table maps emoji to type; extend it per project).

## Commit discipline

1. Review `git diff` and `git diff --cached`; stage only the intended unit.
2. Run the relevant verification and the mandatory documentation currency gate.
3. Update matching TODO evidence in the same commit only when completion is directly proven.
4. Write the commit message in the documented format.
5. Recheck `git status` after committing and report verification plus any evidence gaps.
