---
name: context-mirror
description: >
  脉络镜: 深入分析某个模块在项目中的位置、调用链、参数详情、
  类继承关系、前后端依赖，并与指定目标仓库（如 NVTE）最新实现进行
  对标，识别实现缺漏和优化机会。接受两个参数：module（必填，要分析
  的模块名）和 target_repo（可选，对比仓库）；未指定 target_repo 时
  跳过差异对比。触发词包括 '脉络镜', 'context-mirror', '分析模块',
  '模块脉络', '对标分析', 'gap analysis', 'NVTE', 'trace module',
  'module analysis'.
compatibility: opencode, claude, codex
---

# 脉络镜 — Module Context Insight

When asked to analyze a module's context in the project, perform the following steps.

## Parameters

- **`module`** (required): Module/class name to analyze, e.g. `GroupedLinear`, `LayerNormLinear`, `fp8_autocast`, `Transformer`.
- **`target_repo`** (optional): GitHub repository to compare against, in `owner/repo` format (e.g. `NVIDIA/TransformerEngine`). When provided, the skill fetches the corresponding source file from that repo and performs a structural comparison. When omitted, sections 8-9 are skipped entirely.
- **`target_ref`** (optional): Branch or tag on `target_repo` to compare against. Defaults to `main`. Honor whatever `target_ref` the user gives — never silently substitute `main` for `stable` or vice versa.

## 1. Locate Module Source

1. Take the `module` parameter value (module/class name).
2. Search the source tree for the definition: search `class <Name>` or `def <name>` in all `*.py` files under the project source root.
3. Read the primary definition file (the one with the class/function body).
4. If the file contains multiple classes/functions, list all of them with their line ranges in a table for an overview.

## 2. Trace Import Chain

Map how the module reaches the public API:

1. Find all `__init__.py` files that export the symbol. If no `__init__.py` exists (flat project), trace direct imports.
2. Trace step by step from the definition file up to the top-level entry point.
3. List the full import path chain, showing each hop.

## 3. Analyze Class Hierarchy

1. Read the `class` definition line to get all base classes.
2. For each base class, find its definition file and list key responsibilities.
3. Present the inheritance chain.

## 4. Detail Constructor Parameters

1. Read the `__init__` method and extract every parameter with its type annotation and default value.
2. For each parameter, add a concise explanation in Chinese of its purpose (derived from docstrings or code context).
3. Identify which parameters affect forward behavior, memory usage, parallel strategy, etc.
4. Present in a table: `| 参数 | 类型 | 默认值 | 说明 |`
5. If the module has a dataclass config (`ModelArgs`-like), also list its key fields in a separate table.

## 5. Map Key Methods and Call Flow

1. List all public methods on the class (from reading the file).
2. For the `forward` method:
   - Read the full signature.
   - Summarize the forward logic flow (preprocessing → core computation → postprocessing) in Chinese.
   - Identify the `torch.autograd.Function` subclass that implements the actual forward/backward (if applicable).
   - **Generate a detailed Mermaid flowchart** that covers **all code branches** in the forward pass:
     * Top-level subgraph for the entry module; separate subgraphs for each sub-module (Attention, MoE, Block, Compressor, etc.).
     * Every conditional branch (`if/else`, shape/dtype checks, feature flags). Label edges with `-- 是 -->` / `-- 否 -->`.
     * Every tensor transformation (reshape, permute, split, cat, slice).
     * All kernel/operator invocations (GEMM, RMSNorm, softmax, activation, all-reduce, etc.).
     * Fused ops: break into logical steps, annotate with kernel name.
     * Error/early-return paths.
     * In-place mutations (`.copy_()`, `.add_()`, etc.) marked with `[原地修改]`.
     * All node/edge labels in Chinese (code identifiers and file paths stay English).
     * Every important node annotated with source location `(file.py:nnn)`.
     * Connect subgraphs via edges to show data flow.
     * **Validate Mermaid syntax** after generation (no unquoted spaces in node IDs, balanced subgraph brackets, correct direction declaration).
3. For the `backward` method (if inside an `autograd.Function`): list gradient computations; optionally add a backward subgraph.
4. For other key methods: one-line Chinese summary each.

## 6. Identify Related Modules and Dependencies

1. Search for imports of this module across the codebase: search for `from.*import.*<Name>` and `import.*<Name>` in all `*.py` files under the project root. Also search in `tests/`.
2. Identify:
   - **调用方**: which modules use this class.
   - **内部依赖**: what ops/layers this module imports and uses (including custom CUDA/TileLang kernels from sibling files).
   - **测试文件**: corresponding test files and key test functions.
   - **备选实现**: alternative code paths (e.g. BF16 vs FP8 vs FP4 quantization paths, different routing strategies).

## 7. Identify Distant Relatives (跨文件/模块关联)

1. Search for the module's key method names being called from other files. Refine queries to avoid false positives: use word boundaries (`\b`) and exclude comment-only/docstring matches.
2. Search for configuration/constant references related to this module.
3. Look for any `isinstance` checks or type dispatch that references this class.
4. If the module is the top-level model (e.g. `Transformer`), note all external entry points (e.g. `generate.py` calling `model.forward()`).
5. Group results by strength:
   - **真实调用**: actual call sites.
   - **类型判定**: `isinstance` / `type(...).__name__` references.
   - **配置引用**: CONFIG / DEFAULT / SETTING / MODE constants.
   - **注释/文档**: matches only in comments or docstrings — list separately, do not count as call sites.

## 8. Reference & Gap Analysis (与目标仓库对标分析)

If `target_repo` was not provided, **skip this section and section 9 entirely** — the analysis ends at section 7.

Otherwise, compare the local implementation against the specified target repository to identify missing features, implementation gaps, and optimization opportunities.

### 8.1 Locate Reference Path

1. Read the module file's docstring / header comments for a `Reference:` line.
2. If no reference is found, infer the equivalent path by matching the module name against the target repo's source tree via GitHub API.

### 8.2 Fetch Remote Source

1. Fetch the corresponding source file from `https://raw.githubusercontent.com/<target_repo>/<target_ref>/<reference-path>`.
2. If the exact file doesn't exist, search the target repo structure via GitHub API to find the closest equivalent.
3. If the remote fetch fails (no network, rate limit), note this limitation and skip to manual comparison.

### 8.3 Structural Comparison

Compare the local and remote versions across these dimensions:

1. **Class hierarchy**: Same base classes? Different MRO?
2. **Constructor parameters**: Compare every `__init__` param side by side — feature gaps, divergent defaults, type mismatches.
3. **Public methods**: List remote methods not present locally.
4. **Forward signature**: Same input/output contract? Different return types?
5. **Advanced features**: Newer features in remote (quantization modes, kernel variants) not yet ported.
6. **Autograd function**: Compare inner `torch.autograd.Function` implementations.

### 8.4 Categorize Deltas

| Category | Label | Description |
|----------|-------|-------------|
| **Missing Feature** | 🔴 GAP | Remote has a feature/param/method that local lacks |
| **Behavior Divergence** | 🟡 DIVERGE | Same interface but different logic or defaults |
| **Local Adaptation** | 🔵 ADAPT | Intentional change for local hardware/requirements |
| **Optimization Opportunity** | 🟢 OPT | Remote uses a more efficient approach to adopt |
| **Deprecated / Removed** | ⚪ CLEANUP | Remote removed something local still carries |

### 8.5 Optimization Suggestions

Based on the comparison, recommend specific actions: port missing features, align divergent behavior, adopt better patterns, remove dead code.

## 9. Pseudo-finding Defense (MANDATORY)

Every GAP / DIVERGE / OPT / CLEANUP claim (and any assertion of "missing / buggy / optimizable" in sections 4-7) must pass at least one validation gate before being reported. Unvalidated claims must be downgraded to `⚠️ Likely pseudo` or withdrawn.

### 9.1 Validation Gates

| Gate | How to satisfy |
|------|----------------|
| **Empirical repro** | ≤30-line stub reproducing the gap (no pytest dependency preferred) |
| **Direct cross-reference** | Remote file shows a different implementation for the same thing |
| **Caller trace** | Search proves the affected code path is actually called |
| **Test enforcement** | Tests already assert or would assert the opposite behavior |
| **Author intent doc** | Comment / docstring / commit message confirms intentional behavior |
| **Docstring / spec quote** | Remote README or docstring describes the missing behavior |

### 9.2 Common False-Positive Signals

Watch for: dead paths (symbol is never called), contract illusions (behavior from base class/decorator/metaclass), zero-benefit micro-optimizations, wrong `target_ref` mismatch, treating comment-only references as call sites, pre-existing differences outside this review's scope, and "missing" paths already tested or acknowledged.

### 9.3 Output Tagging

Tag each finding with its validation gate: `[repro]` / `[caller-trace]` / `[nvte-ref]` / `[test]` / `[author-intent]` / `[doc]`. If no gate can be satisfied within two minutes → `⚠️ Likely pseudo`.

## Report Format

Present findings using these Chinese section headers (code identifiers and technical terms remain in English). Use the specific formats (tables, trees, mermaid) prescribed in each numbered section above. When `target_repo` was not provided, omit sections 8 and 9 from the report.

```
## 脉络镜: <ModuleName>

### 1. 源文件定位
### 2. 导入链
### 3. 类继承关系
### 4. 构造参数详情
### 5. 核心方法 & 调用流程
#### 5.1 方法总览
#### 5.2 forward 数据流
#### 5.3 其他关键方法
### 6. 关联模块 & 依赖
### 7. 跨文件关联
### 8. 对标分析 (仅当指定 target_repo)
#### 8.1 参考源
#### 8.2 结构对比
#### 8.3 参数差异明细
#### 8.4 方法差异明细
#### 8.5 优化建议
### 9. 总结
```
