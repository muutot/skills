# Skills

Reusable AI agent skill definitions compatible with [opencode](https://opencode.ai), [Claude Code](https://code.claude.com), and [OpenAI Codex](https://developers.openai.com/codex).

## Skills

| Skill | Description |
|---|---|
| [author-contrib-review](author-contrib-review/SKILL.md) | Analyze Git commit history for one or more authors |
| [branch-diff-review](branch-diff-review/SKILL.md) | Review branch/tag diffs for bugs, optimizations, and missed changes |
| [commit-message-gen](commit-message-gen/SKILL.md) | Generate structured Git commit messages from staged/unstaged diffs |
| [context-mirror](context-mirror/SKILL.md) | Deep module analysis: call chain, class hierarchy, NVTE gap comparison |
| [pre-commit-review](pre-commit-review/SKILL.md) | Pre-commit diff review: bug check, optimization, missed modifications |
| [commit](github_workflow/commit/SKILL.md) | Emoji commit with CHANGELOG [Unreleased] management |
| [release](github_workflow/release/SKILL.md) | Bump version, tag, and update CHANGELOG for releases |

## Usage

### Auto-discovery

Each agent discovers skills automatically from their respective project directories:

| Tool | Directory |
|---|---|
| opencode | `.opencode/skills/<name>/SKILL.md` |
| Claude Code | `.claude/skills/<name>/SKILL.md` |
| OpenAI Codex | `.agents/skills/<name>/SKILL.md` |

### Export script

```bash
python skill-export.py                  # export to all three tools
python skill-export.py -t claude codex  # export to specific tools
python skill-export.py -t opencode -m symlink  # use symbolic links
python skill-export.py -f               # overwrite existing files
```

Options:

| Flag | Default | Description |
|---|---|---|
| `-t` / `--target` | all three | Tools: `opencode`, `claude`, `codex` |
| `-o` / `--output-dir` | `.` | Output root directory |
| `-s` / `--source-dir` | `.` | Scan directory for `SKILL.md` files |
| `-m` / `--mode` | `copy` | `copy`, `symlink`, or `hardlink` |
| `-f` / `--force` | — | Overwrite existing files |

## Structure

```
skills/
├── <skill-name>/
│   └── SKILL.md          # skill definition (YAML frontmatter + markdown body)
├── github_workflow/
│   ├── commit/SKILL.md   # workflow-grouped skills
│   └── release/SKILL.md
├── skill-export.py        # export script
└── README.md
```

Each `SKILL.md` uses standard YAML frontmatter with `name` and `description` (required), plus optional fields like `license`, `compatibility`, and `metadata`. All skills declare `compatibility: opencode, claude, codex` in their frontmatter.

## Compatibility

Skills are loadable by all three tools with zero modifications — all read the same `<name>/SKILL.md` structure. Use `skill-export.py` to deploy them to the appropriate directory for each tool.
