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

- **`module`** (required): Module/class name to analyze, e.g.
  `GroupedLinear`, `LayerNormLinear`, `fp8_autocast`.
- **`target_repo`** (optional): GitHub repository to compare against, in
  `owner/repo` format (e.g. `NVIDIA/TransformerEngine`). When provided, the
  skill fetches the corresponding source file from that repo and performs a
  structural comparison. When omitted, sections 8-9 (gap analysis) are
  skipped entirely.

## 1. Locate Module Source

1. Take the `module` parameter value (module/class name).
2. Search the source tree for the definition:
   - `grep -r "class <Name>" --include="*.py" transformer_engine/`
   - `grep -r "def <name>" --include="*.py" transformer_engine/`
3. Read the primary definition file (the one with the class/function body).

## 2. Trace Import Chain

Map how the module reaches the public API:

1. Find all `__init__.py` files that export the symbol:
   - Search for the name in all `__init__.py` files under `transformer_engine/`.
2. Trace step by step from the definition file up to top-level `__init__.py`.
3. List the full import path chain, e.g.:
   ```
   transformer_engine/pytorch/module/linear.py  (definition)
   └→ transformer_engine/pytorch/module/__init__.py  (re-export)
     └→ transformer_engine/pytorch/__init__.py  (public API)
   ```

## 3. Analyze Class Hierarchy

1. Read the `class` definition line to get all base classes.
2. For each base class, find its definition file and list key responsibilities.
3. Present the inheritance chain:
   ```
   GroupedLinear
   └→ TransformerEngineBaseModule  (base.py: config mgmt, FP8 metadata)
     └→ nn.Module  (PyTorch base)
   ```

## 4. Detail Constructor Parameters

1. Read the `__init__` method and extract every parameter with its type annotation and default value.
2. For each parameter, add a concise explanation in Chinese of its purpose (derived from docstrings or code context).
3. Identify which parameters affect forward behavior, memory usage, parallel strategy, etc.
4. Present in a table format:

   | Parameter | Type | Default | Description |
   |-----------|------|---------|-------------|
   | `num_gemms` | `int` | — | 专家/分组数量 |
   | `in_features` | `int` | — | 输入特征维度 |
   | ... | ... | ... | ... |

## 5. Map Key Methods and Call Flow

1. List all public methods on the class (from reading the file).
2. For the `forward` method:
   - Read the full signature.
   - Summarize the forward logic flow (preprocessing → autograd function →
     postprocessing).
   - Identify the `torch.autograd.Function` subclass that implements the
     actual forward/backward.
    - Trace every operation: gemm, norm, cast, quantization, dequantization,
      activation functions, residual add, etc.
    - **Generate a detailed Mermaid flowchart** that covers **all code
      branches** in the forward pass. This must include:
      - **Every conditional branch**: `if/else`, `torch.where`, tensor shape
        checks, dtype checks, device checks, feature flag gates (e.g. FP8
        enabled / disabled, tensor parallelism on / off, sequence parallel
        on / off). Each branch must be a distinct path in the flowchart with
        its label on the edge.
      - **Every tensor transformation**: each cast, reshape, permute,
        transpose, split, cat, and slice along the data path.
      - **All kernel / operator invocations**: GEMM, layernorm, softmax,
        activation (ReLU, GELU, SwiGLU, etc.), residual add, all-reduce,
        reduce-scatter, all-gather.
      - **Subgraph decomposition for fused ops**: if multiple operations are
        fused into one kernel (e.g. QKV projection, fusing bias+gelu),
        break the subgraph into nodes for each logical step and annotate
        "fused" on the container subgraph.
      - **Error / early-return paths**: guard clauses that return early
        (shape mismatch, empty tensor, skipped computation).
      - **In-place mutation**: mark nodes where tensors are modified in-place
        (`.add_()`, `.copy_()`, etc.) with a distinct style.
      - **Autograd.Function boundary**: clearly delineate where the code
        enters and exits the custom autograd function, and show both forward
        and backward data flow if the backward method is non-trivial.
    - **Node labels and edge labels must be in Chinese** — all descriptions
      within the flowchart must use Chinese. Code identifiers, type names,
      and file paths remain in English.
    - **Annotate critical code with file location**: for important nodes
      (kernel calls, branch conditions, tensor transformations), append the
      source file path and line number in parentheses, e.g.
      `[量化 (ops/fp8.py:42)]`. This helps readers jump directly to the
      relevant code.
      Example (your flowchart must be significantly more detailed):
      ```mermaid
      flowchart TD
          subgraph 输入
              A[hidden_states: shape, dtype]
              W[weight: shape, dtype]
              B[bias 或 None]
          end
          subgraph 前置检查
              C{FP8 启用? (quant.py:88)}
              C -- 是 --> D[初始化 fp8_meta]
              C -- 否 --> E[跳过 FP8 初始化]
              F{张量并行?}
              F -- 是 --> G[切分权重 (linear.py:120)]
              F -- 否 --> H[使用完整权重]
          end
          subgraph 预处理
              I[转成计算精度]
              J[reshape 适配 grouped gemm]
          end
          subgraph AutogradFn
              K[FP8 量化 (fp8.py:42)]
              L[GEMM: MxK x KxN (cublas)]
              M[反量化]
              N{有 bias?}
              N -- 是 --> O[加 bias (linear.py:150)]
              N -- 否 --> P[跳过 bias]
          end
          subgraph 后处理
              Q[all-reduce (TP 时)]
              R[转成输出精度]
              S[输出激活]
          end
          输入 --> 前置检查
          前置检查 --> 预处理
          预处理 --> AutogradFn
          AutogradFn --> 后处理
      ```
    - **Validate the generated Mermaid syntax**: after writing the flowchart
      code block, check that node IDs, edge definitions, subgraph boundaries,
      and direction declarations are all syntactically valid. Common pitfalls:
      node IDs with spaces (must be quoted), mismatched subgraph brackets,
      missing direction declaration (`TD` / `LR` / `BT`). Fix any issues found.
3. For the `backward` method (if inside an `autograd.Function`):
   - List all gradient computations (dgrad, wgrad, act grad).
   - Note any gradient accumulation, gradient scaling, or sparse gradient
     handling.
   - Optionally add a backward subgraph to the flowchart if the logic is
     sufficiently complex to warrant it.
4. For other key methods (`reset_parameters`, `backward_dw`,
   `make_grouped_weights`, `set_tensor_parallel_group`, etc.):
   - List them with a one-line summary of what they do.

## 6. Identify Related Modules and Dependencies

1. Search for imports of this module across the codebase:
   ```
   grep -r "from.*import.*<Name>" --include="*.py" transformer_engine/
   grep -r "import.*<Name>" --include="*.py" transformer_engine/
   ```
2. Also search in `tests/` to find test files.
3. Identify:
   - **Callers**: which modules use this class.
   - **Dependencies**: what ops/layers this module imports and uses.
   - **Tests**: corresponding test files and key test functions.
   - **Parallel implementations**: alternative code paths (e.g. `performance_grouped_linear_impl.py`).

## 7. Identify Distant Relatives (跨文件/模块关联)

1. Search for the module's key method names being called from other files:
   ```
   grep -r "\.forward_dw\|\.backward_dw\|\.need_backward_dw\|\.make_grouped_weights" --include="*.py" transformer_engine/
   ```
2. Search for configuration/constant references related to this module.
3. Look for any `isinstance` checks or type dispatch that references this class.

## 8. Reference & Gap Analysis (与目标仓库对标分析)

If `target_repo` was not provided, **skip this section and section 9 entirely**
— the analysis ends at section 7.

Otherwise, compare the local implementation against the specified target
repository to identify missing features, implementation gaps, and optimization
opportunities.

### 8.1 Locate Reference Path

1. Read the module file's docstring / header comments for a `Reference:` line,
   e.g.:
   ```
   Reference: transformer_engine/pytorch/module/grouped_linear.py
   ```
2. If no reference is found, infer the equivalent path using the same relative
   path from the project root.

### 8.2 Fetch Remote Source

1. Fetch the corresponding source file from the target repository:
   ```
   https://raw.githubusercontent.com/<target_repo>/main/<reference-path>
   ```
   - Try `main` branch first; if that fails (404), try `stable` or the latest
     release tag.
   - Use `webfetch` to retrieve the raw content.
2. If the exact file doesn't exist at the expected path, search the target
   repo structure:
   ```
   https://api.github.com/repos/<target_repo>/contents/<directory>
   ```
   to find the closest equivalent.
3. If the remote fetch fails (no network, rate limit), note this limitation
   and skip to section 8.4 (manual comparison based on codebase knowledge).

### 8.3 Structural Comparison

Compare the local and remote versions across these dimensions:

1. **Class hierarchy**: Same base classes? Different MRO?
2. **Constructor parameters**: Compare every `__init__` param side by side:
   - Parameters present in remote but missing locally → **feature gap**
   - Parameters with different defaults → **behavior divergence**
   - Parameters with different types → **porting issue**
3. **Public methods**: List remote methods not present locally → **missing
   implementation**
4. **Forward signature**: Same input/output contract? Different return types?
5. **Advanced features**: The remote repo may have newer features (e.g.
   quantization modes, kernel variants) not yet ported.
6. **Autograd function**: Compare inner `torch.autograd.Function`
   implementations — the forward/backward logic differences reveal the core
   porting delta.

### 8.4 Categorize Deltas

Classify each difference into:

| Category | Label | Description |
|----------|-------|-------------|
| **Missing Feature** | 🔴 GAP | Remote has a feature/param/method that local lacks |
| **Behavior Divergence** | 🟡 DIVERGE | Same interface but different logic or defaults |
| **Local Adaptation** | 🔵 ADAPT | Intentional change for local hardware/requirements |
| **Optimization Opportunity** | 🟢 OPT | Remote uses a more efficient approach to adopt |
| **Deprecated / Removed** | ⚪ CLEANUP | Remote removed something local still carries |

### 8.5 Optimization Suggestions

Based on the comparison, recommend specific actions:

1. **Port missing features**: List each 🔴 GAP with effort estimate and priority.
2. **Align divergent behavior**: For each 🟡 DIVERGE, suggest whether to align
   with remote or keep the local adaptation.
3. **Adopt newer patterns**: For each 🟢 OPT, describe the approach.
4. **Remove dead code**: For each ⚪ CLEANUP, point to relevant commits.

## 9. Output Report

If `target_repo` was not provided, omit sections 8-9 from the report.

Present findings in the following structure in Chinese (code identifiers and technical terms remain in English):

```
## 脉络镜: <ModuleName>

### 1. 源文件定位
<file_path>

### 2. 导入链
<full import chain>

### 3. 类继承关系
<inheritance tree>

### 4. 构造参数详情
| 参数 | 类型 | 默认值 | 说明 |
| ... | ... | ... | ... |

### 5. 核心方法 & 调用流程
#### forward
<signature and flow description>

#### 其他关键方法
- `<method>`: <description>

### 6. 关联模块 & 依赖
- **调用方**: <files that import this module>
- **内部依赖**: <what ops/layers this module uses>
- **测试文件**: <corresponding test files>
- **备选实现**: <alternative code paths if any>

### 7. 跨文件关联
<references to this module's methods from other parts of the codebase>

### 8. 对标分析 (仅当指定了 target_repo 时)
#### 8.1 参考源
<remote source URL or path>

#### 8.2 结构对比

| 对比维度 | 本地 | 远程 | 差异 |
|----------|------|------|------|
| 基类 | ... | ... | ... |
| 构造参数数 | ... | ... | ... |
| 公开方法数 | ... | ... | ... |
| 高级特性 | ... | ... | ... |
| ... | ... | ... | ... |

#### 8.3 参数差异明细
| 参数 | 本地默认值 | 远程默认值 | 差异类型 | 说明 |
|------|-----------|-----------|----------|------|
| ... | ... | ... | 🔴 GAP / 🟡 DIVERGE / ... | ... |

#### 8.4 方法差异明细
| 方法 | 本地 | 远程 | 差异类型 | 说明 |
|------|------|------|----------|------|
| ... | 有 | 有 | — | 实现不同 |
| ... | 无 | 有 | 🔴 GAP | 缺失 |
| ... | 有 | 无 | ⚪ CLEANUP | 可清理 |

#### 8.5 优化建议
- [🔴] <priority>: <suggestion>
- [🟢] <priority>: <suggestion>

### 9. 总结
<brief summary of the module's role in the project and optionally the key gaps>
```
