# Changelog

## [Unreleased]

- :memo: [context-mirror]: comprehensive skill revamp — Chinese-language
  output, generic project support (removed hardcoded NVTE paths), exhaustive
  Mermaid flowcharts with sub-module decomposition and file:line annotations,
  flowchart syntax validation checklist, and dataclass config documentation;
  deduplicate 205-line embedded flowchart example into a short skeleton
- :recycle: [skills]: streamline documentation across 4 skills — collapse
  verbose templates, add validation gates, deduplicate examples, restructure
  pseudo-bug identification into a false-positive signals table
- :recycle: [release]: split monolithic workflow into `rust_release`,
  `python_release`, and `generic_release` — each tailored to its language
  ecosystem with appropriate build and publish steps
- :wrench: [export]: harden export script — validate skill names in
  frontmatter against a strict regex, detect broken symlinks in copy_file,
  prevent path traversal writes with resolve + is_relative_to checks, and
  add usage documentation
- :bug: [branch-diff-review]: fix YAML frontmatter parsing — strip leading
  non-YAML noise before the first `---` marker so the skill loads correctly
- :wrench: [license]: add MIT LICENSE file
- :art: [skills]: add `compatibility: opencode, claude, codex` frontmatter to
  all 9 skills

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
