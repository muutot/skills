---
name: author-contrib-review
description: >
  Analyzes Git commits from one or more authors in the current repository.
  Summarizes what they did: commit count, file scope, key modules, feature
  types (feat/fix/refactor), and impact metrics. Triggered by keywords like
  '看看 xxx 做了什么', '提交者分析', 'author review', '谁写了什么', '贡献分析'.
---

# Author Contribution Review

When asked to review what a specific author (or multiple authors) has done in the repo, perform the following steps.

## 1. Identify Authors

1. If the user provides author names (e.g. "Muu", "Muuyo"), use them directly.
2. If the user says "看看最近的提交者" or similar, run:

```
git log --format="%an" --all | Select-Object -Unique
```

to see all distinct authors, then pick the relevant ones.

3. Support multiple authors by comma/space separation (e.g. "Muu, Muuyo").

## 2. Gather Contribution Data

Run the following queries (replace `$authors` with the actual author names):

### 2.1 Basic Stats

```
git log --author="<author1>" --author="<author2>" --format="%H" --all | Measure-Object | Select-Object -ExpandProperty Count
```

### 2.2 Commit Timeline & Messages

```
git log --author="<author1>" --author="<author2>" --format="%H %ai %s" --all
```

### 2.3 File & Line Stats

```
$total_files=0; $total_plus=0; $total_minus=0;
git log --author="<author>" --format="%H" --all | %{
  $h=$_; $s=git show --format="" --shortstat $h;
  if ($s -match '(\d+) file[s]? changed'){$f=[int]$matches[1]}else{$f=0};
  if ($s -match '(\d+) insertions?\(\+\)'){$p=[int]$matches[1]}else{$p=0};
  if ($s -match '(\d+) deletions?\(-\)'){$m=[int]$matches[1]}else{$m=0};
  $total_files+=$f; $total_plus+=$p; $total_minus+=$m
};
Write-Output "Commits: $count | Files changed: $total_files | Insertions: $total_plus | Deletions: $total_minus | Net: $($total_plus-$total_minus)"
```

Repeat for each author, then sum for multi-author queries.

### 2.4 Commit Type Breakdown

```
git log --author="<author>" --format="%s" --all |
  Select-String -Pattern "^(feat|refactor|fix|perf|test|docs|chore|style|revert)" |
  ForEach-Object { if ($_ -match "^(feat|refactor|fix|perf|test|docs|chore|style|revert)") { $matches[1] } } |
  Group-Object | Sort-Object Count -Descending
```

### 2.5 Affected Modules / File Paths

```
git log --author="<author>" --format="%H" --all |
  %{ git log --format="" --name-only -1 $_ } | Select-Object -Unique | Sort-Object
```

### 2.6 Active Days of Week

```
git log --author="<author>" --since="<first_commit_date>" --until="<last_commit_date>" --format="%ai" --all |
  ForEach-Object { ([DateTime]$_.Substring(0,10)).DayOfWeek } |
  Group-Object | Sort-Object Count -Descending
```

## 3. Analyze & Summarize

### 3.1 Identify Key Modules

Group touched files by top-level directory or subsystem (e.g. `module/`, `tensor/`, `quantization/`, `ops/gemm.py`, `common/recipe/`, `tests/`). Identify which areas received the most attention.

### 3.2 Identify Work Themes

Based on commit messages and file changes, categorize contributions:

- **New features**: commits with `feat:` prefix, introducing new capabilities
- **Refactoring**: commits with `refactor:` prefix, structural improvements
- **Bug fixes**: commits with `fix:` prefix, issue resolution
- **Performance**: commits with `perf:` prefix, optimization
- **Infrastructure**: CI, linting, tooling changes
- **Tests**: test additions/modifications

### 3.3 Quantify Impact

- Total net lines contributed (insertions - deletions)
- Number of files touched
- Primary modules owned
- Feature areas delivered

## 4. Output Format

Present the result in Chinese (中文) with the following structure:

```markdown
### 提交者：<author_name> | <total_commits> commits

**时间范围：** <first_date> ~ <last_date>
**影响规模：** <files_changed> 个文件，净增 <net_lines> 行代码（+<ins> / -<del>）

**提交类型分布：**
- 功能开发 (feat): <n> 次
- 重构 (refactor): <n> 次
- 问题修复 (fix): <n> 次
- 性能优化 (perf): <n> 次
- 其他: <n> 次

**涉及主要模块：**
- <模块1>：<简述改动内容>
- <模块2>：<简述改动内容>
- ...

**主要工作内容：**
1. <要点1>
2. <要点2>
3. ...

**活跃规律：** 以周<x>最为活跃，共 <n> 次提交
```

If there are multiple authors, present each individually and optionally provide a combined summary.

## 5. Batch Mode (Multiple Authors)

For multiple authors, also show a side-by-side or merged view of total contributions across the team.

## 6. Language

Output in Chinese (中文) by default. File paths, technical identifiers, and English-only terms (e.g. `Linear`, `FP8`, `GEMM`) may be kept as-is.
