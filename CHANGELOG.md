# Changelog

## [Unreleased]

- :bug: [branch-diff-review]: remove leading blank lines and stray character
  before YAML frontmatter that could cause parsing issues
- :wrench: [license]: add MIT LICENSE file and reference in README
- :art: [skills]: add `compatibility: opencode, claude, codex` to all 9 skill
  definitions and update README compatibility docs
- :recycle: [github_workflow]: rename `release` skill to `rust_release`; add
  `python_release` and `generic_release` skills

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
