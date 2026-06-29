# Changelog

## [Unreleased]

- :recycle: [skills]: streamline all skill documentation — collapse verbose
  output templates into cross-section references (author-contrib-review),
  restructure pseudo-bug identification into validation gates + false-positive
  signals table (branch-diff-review), strip detailed report template in favor
  of section headers (context-mirror), and prune example-heavy hash placement
  docs (commit-skill); each change reduces maintenance surface without
  sacrificing the information users need
- :memo: [context-mirror]: comprehensive skill revamp — Chinese-language
  output, generic project support (removed hardcoded NVTE paths), exhaustive
  Mermaid flowcharts with sub-module decomposition and file:line annotations,
  flowchart syntax validation checklist, and dataclass config documentation;
  deduplicate 205-line embedded flowchart example into a short skeleton
- :recycle: [release]: split into `rust_release`, `python_release`, and
  `generic_release` — each tailored to its language ecosystem with appropriate
  build and publish steps
- :art: [skills]: add `compatibility: opencode, claude, codex` frontmatter to
  all 9 skills and update README compatibility documentation
- :wrench: [project]: add `pyproject.toml` — declare project name, version,
  and Python 3.12+ requirement
- :wrench: [license]: add MIT LICENSE file

## [0.1.0] - 2026-06-27

### Features
- (export) add Python CLI script that discovers SKILL.md files and deploys
  them into opencode / claude / codex directory structures with copy, symlink,
  or hardlink modes — [`c4b9a7c`](https://github.com/muutot/skills/commit/c4b9a7c)
- (skills) add opencode skill definitions for author-contrib-review,
  branch-diff-review, commit-message-gen, context-mirror, commit, release,
  and pre-commit-review workflows — [`22fbdfa`](https://github.com/muutot/skills/commit/22fbdfa)

### Chores
- (config) fix `.agnets` typo in `.gitignore` and add `.claude` / `.agents`
  entries — [`c4b9a7c`](https://github.com/muutot/skills/commit/c4b9a7c)
- (docs) add README with skill catalog, export script usage, and cross-tool
  compatibility notes — [`c4b9a7c`](https://github.com/muutot/skills/commit/c4b9a7c)
