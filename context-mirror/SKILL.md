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
  `GroupedLinear`, `LayerNormLinear`, `fp8_autocast`, `Transformer`.
- **`target_repo`** (optional): GitHub repository to compare against, in
  `owner/repo` format (e.g. `NVIDIA/TransformerEngine`). When provided, the
  skill fetches the corresponding source file from that repo and performs a
  structural comparison. When omitted, sections 8-9 (gap analysis) are
  skipped entirely.

## 1. Locate Module Source

1. Take the `module` parameter value (module/class name).
2. Search the source tree for the definition:
   - Search `class <Name>` or `def <name>` in all `*.py` files under the
     project source root. Use the project's primary source directory
     (e.g. `transformer_engine/`, `src/`, or project root).
3. Read the primary definition file (the one with the class/function body).
4. If the file contains multiple classes/functions, list all of them with
   their line ranges in a table for an overview.

## 2. Trace Import Chain

Map how the module reaches the public API:

1. Find all `__init__.py` files that export the symbol:
   - Search for the name in all `__init__.py` files.
   - If no `__init__.py` exists (flat project), trace direct imports.
2. Trace step by step from the definition file up to the top-level entry point.
3. List the full import path chain, e.g.:
   ```
   model.py  (definition: Transformer, Block, Attention, ...)
   └→ generate.py  (from model import Transformer, ModelArgs)
   ```
   If no `__init__.py`, note this and show direct imports instead.

## 3. Analyze Class Hierarchy

1. Read the `class` definition line to get all base classes.
2. For each base class, find its definition file and list key responsibilities.
3. Present the inheritance chain:
   ```
   Transformer
   └→ nn.Module  (PyTorch base)

   MTPBlock
   └→ Block
      └→ nn.Module
   ```

## 4. Detail Constructor Parameters

1. Read the `__init__` method and extract every parameter with its type annotation and default value.
2. For each parameter, add a concise explanation in Chinese of its purpose (derived from docstrings or code context).
3. Identify which parameters affect forward behavior, memory usage, parallel strategy, etc.
4. Present in a table format:

   | 参数 | 类型 | 默认值 | 说明 |
   |------|------|--------|------|
   | `num_gemms` | `int` | — | 专家/分组数量 |
   | `in_features` | `int` | — | 输入特征维度 |
   | ... | ... | ... | ... |
5. If the module has a dataclass config (`ModelArgs`-like), also list its key
   fields in a separate table.

## 5. Map Key Methods and Call Flow

1. List all public methods on the class (from reading the file).
2. For the `forward` method:
   - Read the full signature.
   - Summarize the forward logic flow (preprocessing → core computation →
     postprocessing).
   - Identify the `torch.autograd.Function` subclass that implements the
     actual forward/backward (if applicable).
   - Trace every operation: gemm, norm, cast, quantization, dequantization,
     activation functions, residual add, etc.
   - **Generate a detailed Mermaid flowchart** that covers **all code
     branches** in the forward pass. This must include:
     - **Top-level flow first**: show the entry module (e.g. `Transformer`)
       calling into its sub-modules. Use one top-level subgraph for the
       outer forward method.
     - **Every sub-module as a separate subgraph**: decompose each major
       component (Attention, MoE, Block, Compressor, Indexer, Head, etc.)
       into its own labeled subgraph with its entry function annotated.
     - **Every conditional branch**: `if/else`, `torch.where`, tensor shape
       checks, dtype checks, feature flag gates (e.g. FP8/FP4 enabled,
       tensor parallelism on/off, compress_ratio > 0, overlap mode,
       prefill vs decode, hash routing vs score routing, etc.). Each branch
       must be a distinct path in the flowchart with its label on the edge.
     - **Every tensor transformation**: each cast, reshape, permute,
       transpose, split, cat, and slice along the data path.
     - **All kernel / operator invocations**: GEMM, RMSNorm, softmax,
       activation (ReLU, GELU, SiLU, SwiGLU, etc.), residual add, all-reduce,
       all-gather, Hadamard transform.
     - **Subgraph decomposition for fused ops**: if multiple operations are
       fused into one kernel, break the subgraph into nodes for each logical
       step and annotate the kernel name.
     - **Error / early-return paths**: guard clauses that return early
       (shape mismatch, empty tensor, skipped compression).
     - **In-place mutation**: mark nodes where tensors are modified in-place
       (`.copy_()`, `.add_()`, etc.) with a distinct style.
     - **Node labels and edge labels must be in Chinese** — all descriptions
       within the flowchart must use Chinese. Code identifiers, type names,
       and file paths remain in English.
     - **Annotate every node with file location**: for each important node
       (kernel call, branch condition, tensor transformation, sub-module
       entry), append the file path and line number in parentheses, e.g.
       `[FP8 量化 (kernel.py:105)]` or `[低秩 Q 投影 (model.py:788)]`.
       This helps readers jump directly to the relevant code.
     - **Connect subgraphs via edges**: show data flow between subgraphs
       (e.g. `Transformer → Block → Attention → Compressor`). Use labeled
       edges to show tensor shapes where informative.
      - **Node label format**: Each node must use **Chinese to describe the
        semantic meaning** of the operation, not literal code. Append the
        source location as `(file.py:nnn)` at the end of the label. For
        example:
        - ✅ 正确: `"将 token ID 映射为嵌入向量 (model.py:113)"`
        - ✅ 正确: `"对非 rope 维度做 FP8 量化模拟 (model.py:803)"`
        - ❌ 错误: `"h = self.embed(input_ids) → [b,s,d] (model.py:113)"`
        - ❌ 错误: `"act_quant(kv[..., :-rd], 64, ...) (model.py:803)"`
      - Example structure (your flowchart must be significantly more detailed
        and include all branches):
        ```mermaid
        flowchart TD
            subgraph Transformer["主入口 (model.py:L1305)"]
                A["输入 token 序列"] --> B["将 token ID 映射为嵌入向量 (model.py:113)"]
                B --> C["沿 hc_mult 维复制扩展为并行流 (model.py:1310)"]
            end
            subgraph Block["Block.forward (L1118)"]
                direction TB
                D["将 hc_mult 条流压缩为单条 (model.py:1087)"] --> E["RMS 层归一化 (model.py:1127)"]
                E --> F["多头潜在注意力计算 (model.py:774)"]
                F --> G["将单条输出扩散回 hc_mult 条流 (model.py:1105)"]
            end
            C --> Block
            Block --> Head["HC 聚合 + RMSNorm + 词表投影 (model.py:1167)"]
            Head --> H["输出 logits"]
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
4. For other key methods (`reset_parameters`, `hc_pre`, `hc_post`,
   `get_logits`, `overlap_transform`, etc.):
   - List them with a one-line summary of what they do in Chinese.

## 6. Identify Related Modules and Dependencies

1. Search for imports of this module across the codebase:
   ```
   grep -r "from.*import.*<Name>" --include="*.py" <project_root>/
   grep -r "import.*<Name>" --include="*.py" <project_root>/
   ```
2. Also search in `tests/` to find test files.
3. Identify:
   - **调用方**: which modules use this class.
   - **内部依赖**: what ops/layers this module imports and uses (including
     custom CUDA/TileLang kernels from sibling files).
   - **测试文件**: corresponding test files and key test functions.
   - **备选实现**: alternative code paths (e.g. BF16 vs FP8 vs FP4 quantization
     paths, different routing strategies).

## 7. Identify Distant Relatives (跨文件/模块关联)

1. Search for the module's key method names being called from other files.
   Use patterns specific to the analyzed module rather than hardcoded names.
2. Search for configuration/constant references related to this module.
3. Look for any `isinstance` checks or type dispatch that references this class.
4. If the module is the top-level model (e.g. `Transformer`), note all
   external entry points (e.g. `generate.py` calling `model.forward()`).

## 8. Reference & Gap Analysis (与目标仓库对标分析)

If `target_repo` was not provided, **skip this section and section 9 entirely**
— the analysis ends at section 7.

Otherwise, compare the local implementation against the specified target
repository to identify missing features, implementation gaps, and optimization
opportunities.

### 8.1 Locate Reference Path

1. Read the module file's docstring / header comments for a `Reference:` line.
2. If no reference is found, infer the equivalent path by matching the module
   name against the target repo's source tree:
   ```
   https://api.github.com/repos/<target_repo>/contents/<directory>
   ```
   to find the closest equivalent file (by class name or file name).

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
<file_path>（共 <N> 行）
| 类/函数 | 行号范围 | 说明 |
|---------|----------|------|
| ... | ... | ... |

### 2. 导入链
<full import chain>

### 3. 类继承关系
<inheritance tree>

### 4. 构造参数详情
| 参数 | 类型 | 默认值 | 说明 |
| ... | ... | ... | ... |

### 5. 核心方法 & 调用流程
#### 5.1 方法总览
| 方法 | 行号 | 说明 |
|------|------|------|
| ... | ... | ... |

#### 5.2 forward 数据流
<signature and logic overview in Chinese>

```mermaid
flowchart TD
    subgraph Transformer["Transformer.forward (model.py:1304)"]
        T_A["输入 token ID 序列"] --> T_B["将 token ID 映射为嵌入向量 (model.py:113)"]
        T_B --> T_C["将隐藏状态沿 hc_mult 维复制展开为并行残差流 (model.py:1310)"]
        T_C --> T_D["串行通过 N 个 Block 层, 每层含 Attn+MoE 两段 HC 计算 (model.py:1312)"]
        T_D --> T_E["将 hc_mult 条流聚合成单条, RMSNorm 后投影到词表 (model.py:1167)"]
    end

    subgraph Block_forward["Block.forward (model.py:1118)"]
        direction TB
        B_in["输入 hc_mult 条并行流 [b,s,hc,d]"] --> B_residual["保存残差引用留作后续 HC 恢复 (model.py:1122)"]
        B_residual --> B_hc_pre_attn["将 hc_mult 条流通过可学习加权求和压缩为单条 (model.py:1087)"]
        B_hc_pre_attn --> B_attn_norm["对单条流做 RMS 层归一化 (model.py:1127)"]
        B_attn_norm --> B_attn["多头潜在注意力: 低秩 Q / 滑窗+压缩 KV / 稀疏注意力 (model.py:774)"]
        B_attn --> B_hc_post_attn["将注意力输出按 post 权重+comb 混合矩阵扩散回 hc_mult 条流 (model.py:1105)"]
        B_hc_post_attn --> B_residual2["再次保存残差 (model.py:1132)"]
        B_residual2 --> B_hc_pre_ffn["FFN 段: 再次将 hc_mult 条流压缩为单条 (model.py:1087)"]
        B_hc_pre_ffn --> B_ffn_norm["RMS 层归一化 (model.py:1137)"]
        B_ffn_norm --> B_ffn["MoE 层: 路由+专家计算+共享专家 (model.py:1016)"]
        B_ffn --> B_hc_post_ffn["FFN 段: 将单条输出扩散回 hc_mult 条流 (model.py:1105)"]
        B_hc_post_ffn --> B_out["输出 hc_mult 条并行流 [b,s,hc,d]"]
    end

    subgraph hc_pre["hc_pre - HC 流压缩 (model.py:1087)"]
        direction TB
        HP_in["输入 hc_mult 条流 [b,s,hc,d] + 可学习混合矩阵"] --> HP_flatten["沿 hc 维拼接并转为 fp32 计算 (model.py:1095)"]
        HP_flatten --> HP_rsqrt["计算 RMS 归一化因子稳定混合权重尺度 (model.py:1096)"]
        HP_rsqrt --> HP_mixes["用混合矩阵将 hc*d 线性投影到 mix_hc 维 (model.py:1097)"]
        HP_mixes --> HP_sinkhorn["TileLang 核: 分解为 pre/post/comb 三套权重并做 Sinkhorn 归一化 (kernel.py:430)"]
        HP_sinkhorn --> HP_y["用 pre 权重加权求和, 将 hc_mult 条流压缩为单条 (model.py:1099)"]
        HP_y --> HP_out["返回单条流 + post/comb 供后续恢复"]
    end

    subgraph hc_post["hc_post - HC 流扩散 (model.py:1105)"]
        direction TB
        HPOS_in["输入单条流 + 残差 hc_mult 流 + post/comb 权重"] --> HPOS_calc["post 加权广播单条流 + comb 加权混合残差流 (model.py:1110)"]
        HPOS_calc --> HPOS_out["输出恢复后的 hc_mult 条流"]
    end

    subgraph Attention_forward["Attention.forward (model.py:774)"]
        direction TB
        A_in["输入单条 hidden [b,s,dim] + 当前解码位置"] --> A_q_a["用低秩矩阵 wq_a 将 dim 降维到 q_lora_rank (model.py:788)"]
        A_q_a --> A_q_norm["对低秩 Q 做 RMS 归一化, qr 同时供 Indexer 复用 (model.py:788)"]
        A_q_norm --> A_q_b["用 wq_b 将低秩 Q 升维到多头空间并切分 head (model.py:790)"]
        A_q_b --> A_qk_norm["在 head 维上二次归一化稳定注意力 logits 尺度 (model.py:792)"]
        A_qk_norm --> A_q_rope["对 rope 维度施加旋转位置编码 (model.py:794)"]
        A_q_rope --> A_kv_proj["用 wkv 投影当前段 KV, 再经 RMSNorm (model.py:798)"]
        A_kv_proj --> A_kv_rope["对 KV 的 rope 维度施加旋转位置编码 (model.py:800)"]
        A_kv_rope --> A_kv_quant["对非 rope 维度做 FP8 量化模拟 QAT 数值行为 (model.py:803)"]
        A_kv_quant --> A_win_idxs["计算滑窗部分的位置索引 (model.py:805)"]
        A_win_idxs --> A_compress_cond{"本层启用 KV 压缩? (model.py:806)"}
        A_compress_cond -- 否 --> A_idxs_int["仅用滑窗索引"]
        A_compress_cond -- 是 --> A_idxer_cond{"压缩比为 4 走语义选择? (model.py:809)"}
        A_idxer_cond -- 是 --> A_idxer["Indexer: 用低秩 Q 对压缩槽打分, 选出语义相关的压缩位置 (model.py:619)"]
        A_idxer_cond -- 否 --> A_uniform["均匀采样压缩位置 (model.py:814)"]
        A_uniform --> A_cat_idxs["拼接滑窗索引与压缩索引 (model.py:818)"]
        A_idxer --> A_cat_idxs
        A_cat_idxs --> A_idxs_int
        A_idxs_int --> A_prefill_cond{"预填充还是解码阶段? (model.py:823)"}
        A_prefill_cond -- 预填充 --> A_win_write_cond{"序列长度≤滑窗大小? (model.py:825)"}
        A_win_write_cond -- 是 --> A_write_seq["整段写入 KV 缓存前段 (model.py:826)"]
        A_win_write_cond -- 否 --> A_write_ring["环形写入, 末尾截断保证最新 win 个 token 连续 (model.py:828)"]
        A_write_seq --> A_compress_prefill{"启用压缩? (model.py:832)"}
        A_write_ring --> A_compress_prefill
        A_compress_prefill -- 是 --> A_compressor_prefill["Compressor: 生成压缩 KV 并拼到 kv 末尾 (model.py:834)"]
        A_compress_prefill -- 否 --> A_attn_prefill
        A_compressor_prefill --> A_attn_prefill["稀疏注意力: 按索引只关注选定位置 (model.py:838)"]
        A_prefill_cond -- 解码 --> A_decode_write["将当前 token KV 环形写入滑窗段缓存 (model.py:841)"]
        A_decode_write --> A_compress_decode{"启用压缩? (model.py:842)"}
        A_compress_decode -- 是 --> A_compressor_decode["Compressor: 推进压缩状态缓存 (model.py:844)"]
        A_compress_decode -- 否 --> A_attn_decode
        A_compressor_decode --> A_attn_decode["稀疏注意力: 用完整 KV 缓存关注选定位置 (model.py:846)"]
        A_attn_decode --> A_antirope["对注意力输出做反 RoPE 使数值范围与输入一致 (model.py:850)"]
        A_attn_prefill --> A_antirope
        A_antirope --> A_o_group["将多头输出按 n_groups 分组准备低秩 O 投影 (model.py:854)"]
        A_o_group --> A_wo_a["分组 Einsum: 每组独立从 head_dim 降维到 o_lora_rank (model.py:859)"]
        A_wo_a --> A_wo_b["RowParallel: 升维回 dim 并跨 rank 归约求和 (model.py:861)"]
        A_wo_b --> A_out["输出 [b,s,dim]"]
    end

    subgraph MoE_forward["MoE.forward (model.py:1016)"]
        direction TB
        M_in["输入 [b,s,dim]"] --> M_flat["将所有 token 展平为二维矩阵 (model.py:1019)"]
        M_flat --> M_gate["Gate: 计算路由分数并选 top-k 专家索引 (model.py:900)"]
        M_gate --> M_init["将累计输出初始化为 fp32 保证加法精度 (model.py:1023)"]
        M_init --> M_counts["统计每个专家被路由到的 token 数 (model.py:1025)"]
        M_counts --> M_loop["遍历本地持有的每个专家"]
        M_loop --> M_count_cond{"该专家无 token 命中?"}
        M_count_cond -- 是 --> M_skip["跳过该专家"]
        M_count_cond -- 否 --> M_gather["找出路由到该专家的 token 及其 top-k 位置 (model.py:1033)"]
        M_gather --> M_expert_fwd["专家前向: SwiGLU 计算并乘以路由权重 (model.py:948)"]
        M_expert_fwd --> M_accum["累加到 fp32 输出缓冲区 (model.py:1035)"]
        M_accum --> M_loop
        M_loop --> M_after_loop
        M_after_loop --> M_allreduce_cond{"多 rank 需跨卡归约? (model.py:1036)"}
        M_allreduce_cond -- 是 --> M_allreduce["跨 rank all-reduce 合并专家分片 (model.py:1038)"]
        M_allreduce_cond -- 否 --> M_shared["加共享专家输出 (model.py:1040)"]
        M_allreduce --> M_shared
        M_shared --> M_restore["还原为原始 dtype 和 shape (model.py:1042)"]
        M_restore --> M_out["输出 [b,s,dim]"]
    end

    subgraph Gate_forward["Gate.forward (model.py:900)"]
        direction TB
        G_in["输入 token hidden + token id"] --> G_scores["用路由矩阵计算每个 token 对各专家的原始分数 (model.py:904)"]
        G_scores --> G_func_cond{"选择路由打分函数 (model.py:905)"}
        G_func_cond -- softmax --> G_softmax["softmax 归一化 (model.py:906)"]
        G_func_cond -- sigmoid --> G_sigmoid["sigmoid 压缩到 [0,1] (model.py:908)"]
        G_func_cond -- sqrtsoftplus --> G_sqrtsoftplus["sqrt(softplus) 更稀疏的赢家通吃 (model.py:911)"]
        G_softmax --> G_orig["保存原始分数作为最终路由权重 (model.py:913)"]
        G_sigmoid --> G_orig
        G_sqrtsoftplus --> G_orig
        G_orig --> G_bias_cond{"打分路由有 bias? (model.py:916)"}
        G_bias_cond -- 是 --> G_add_bias["bias 加在分数上仅影响 topk 选择, 不影响权重 (model.py:917)"]
        G_bias_cond -- 否 --> G_route_cond{"hash 路由? (model.py:918)"}
        G_add_bias --> G_route_cond
        G_route_cond -- 是 --> G_hash["直接查表得专家索引, 完全确定性路由 (model.py:920)"]
        G_route_cond -- 否 --> G_topk["选分数最高的 top-k 个专家 (model.py:923)"]
        G_hash --> G_weights["用原始分数作为选中专家的组合权重 (model.py:925)"]
        G_topk --> G_weights
        G_weights --> G_norm_cond{"非 softmax 需再归一化? (model.py:926)"}
        G_norm_cond -- 是 --> G_reweight["权重除以自身和保证归一化 (model.py:928)"]
        G_norm_cond -- 否 --> G_scale
        G_reweight --> G_scale["全局 route_scale 控制路由锐度 (model.py:930)"]
        G_scale --> G_out["返回权重和专家索引"]
    end

    subgraph Compressor_forward["Compressor.forward (model.py:457)"]
        direction TB
        C_in["输入 hidden [b,s,dim] + 解码位置"] --> C_fp32["转为 fp32 确保数值稳定性 (model.py:469)"]
        C_fp32 --> C_wkv["双线性投影: wkv 产生 K/V 特征, wgate 产生门控分数 (model.py:471)"]
        C_wkv --> C_prefill_cond{"预填充还是解码? (model.py:473)"}
        C_prefill_cond -- 预填充 --> C_prefill["将序列切分为压缩窗口, 做 gated softmax 池化压缩 (model.py:474)"]
        C_prefill_cond -- 解码 --> C_decode["逐 token 写入状态缓冲, 满窗口时触发压缩 (model.py:506)"]
        C_prefill --> C_should_compress{"达到一个完整压缩窗口? (model.py:546)"}
        C_decode --> C_should_compress
        C_should_compress -- 否 --> C_return_none["未满窗口, 不写入缓存"]
        C_should_compress -- 是 --> C_norm["RMSNorm 稳定压缩后的 K/V (model.py:550)"]
        C_norm --> C_rope["对 rope 维度施加位置编码 (model.py:558)"]
        C_rope --> C_rotate_cond{"走 Indexer FP4 量化路径? (model.py:559)"}
        C_rotate_cond -- 是 --> C_hadamard["Hadamard 旋转变换打散维度 (model.py:561)"]
        C_hadamard --> C_fp4_quant["FP4 量化压缩结果 (model.py:562)"]
        C_rotate_cond -- 否 --> C_fp8_quant["对非 rope 维做 FP8 量化, rope 维保留精度 (model.py:565)"]
        C_fp4_quant --> C_write_cache["将压缩后的 KV 写入 kv_cache 对应槽位 (model.py:567)"]
        C_fp8_quant --> C_write_cache
        C_write_cache --> C_return_kv["返回压缩 KV"]
    end

    subgraph Indexer_forward["Indexer.forward (model.py:619)"]
        direction TB
        I_in["输入 hidden + 低秩 Q (qr) + 解码位置"] --> I_q_proj["将低秩 Q 升维到 Indexer 的多头打分空间 (model.py:631)"]
        I_q_proj --> I_q_rope["对 rope 维度施加位置编码 (model.py:634)"]
        I_q_rope --> I_hadamard["Hadamard 旋转变换与压缩 KV 数值空间对齐 (model.py:636)"]
        I_hadamard --> I_fp4_quant["FP4 量化使 Q 与压缩 KV 可比 (model.py:638)"]
        I_fp4_quant --> I_compressor["驱动内部 Compressor 更新压缩 KV 缓存 (model.py:640)"]
        I_compressor --> I_weights["计算每头重要性权重 (model.py:642)"]
        I_weights --> I_score["Einsum 点积: Q 与每个压缩槽 K 计算相似度 (model.py:645)"]
        I_score --> I_relu["ReLU 保留正相关性, 按头加权求和 (model.py:649)"]
        I_relu --> I_allreduce_cond{"多 rank? (model.py:650)"}
        I_allreduce_cond -- 是 --> I_allreduce["跨 rank 汇总分数 (model.py:652)"]
        I_allreduce_cond -- 否 --> I_mask_cond{"预填充阶段? (model.py:653)"}
        I_allreduce --> I_mask_cond
        I_mask_cond -- 是 --> I_mask["屏蔽未来未生成的压缩槽位 (model.py:655)"]
        I_mask_cond -- 否 --> I_topk
        I_mask --> I_topk["选分数最高的 top-k 个压缩位置 (model.py:661)"]
        I_topk --> I_offset["将索引偏移到全局 kv_cache 坐标空间 (model.py:662)"]
        I_offset --> I_out["返回选中压缩位置的索引 [b,s,topk]"]
    end

    subgraph ParallelHead_forward["ParallelHead.forward (model.py:1167)"]
        direction TB
        H_in["输入 hc_mult 条流 [b,s,hc,d]"] --> H_hc_head["将 hc*d 拼接后经 sigmoid 加权求和聚合成单流 (model.py:1187)"]
        H_hc_head --> H_norm["RMS 层归一化 (model.py:1179)"]
        H_norm --> H_last["取最后一步 token 的隐藏状态 (model.py:1165)"]
        H_last --> H_linear["线性投影到词表空间 (model.py:1165)"]
        H_linear --> H_gather_cond{"多 rank? (model.py:1180)"}
        H_gather_cond -- 是 --> H_all_gather["跨 rank all-gather 拼接完整词表分布 (model.py:1182)"]
        H_gather_cond -- 否 --> H_out
        H_all_gather --> H_out["输出 logits [b, vocab_size]"]
    end

    subgraph Expert_forward["Expert.forward (model.py:948)"]
        direction TB
        E_in["输入 token hidden + 路由权重"] --> E_w1["gate 投影 dim → inter_dim (model.py:953)"]
        E_in --> E_w3["up 投影 dim → inter_dim (model.py:954)"]
        E_w1 --> E_limit_cond{"启用激活裁剪? (model.py:955)"}
        E_w3 --> E_limit_cond
        E_limit_cond -- 是 --> E_clamp["对 gate/up 做双向截断抑制激活爆炸 (model.py:957)"]
        E_limit_cond -- 否 --> E_silu
        E_clamp --> E_silu["SiLU(gate) * up 构成 SwiGLU 非线性 (model.py:960)"]
        E_silu --> E_weight_cond{"有路由权重? (model.py:961)"}
        E_weight_cond -- 是 --> E_apply_weight["乘以路由权重实现专家加权 (model.py:963)"]
        E_weight_cond -- 否 --> E_w2
        E_apply_weight --> E_w2["w2 下投影回 dim (model.py:965)"]
        E_w2 --> E_out["输出 [n_token, dim]"]
    end

    T_D --> Block_forward
    Block_forward --> T_E
    Block_forward --> hc_pre
    Block_forward --> hc_post
    Block_forward --> Attention_forward
    Block_forward --> MoE_forward
    MoE_forward --> Gate_forward
    MoE_forward --> Expert_forward
    Attention_forward --> Compressor_forward
    Attention_forward --> Indexer_forward
    T_E --> ParallelHead_forward
```

#### 5.3 其他关键方法
- `<method> (L<nnn>)`: <one-line Chinese description>

### 6. 关联模块 & 依赖
- **调用方**: <files that import this module>
- **内部依赖**: <what ops/layers this module uses, including custom kernels>
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
| 子模块数 | ... | ... | ... |
| 高级特性 | ... | ... | ... |

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
- [🔴] <priority>: <suggestion>（附参考行号）
- [🟢] <priority>: <suggestion>（附参考行号）

### 9. 总结
<brief summary of the module's role in the project and optionally the key gaps>
```

### Flowchart Checklist (before submitting)

- [ ] Every sub-module has its own `subgraph` with a Chinese label
- [ ] All conditional branches shown as diamond nodes with edge labels
- [ ] Every important node annotated with `(file.py:Lnnn)` location
- [ ] Node and edge labels use Chinese descriptions (code IDs stay English)
- [ ] Subgraphs connected via edges to show data flow direction
- [ ] Mermaid syntax validated (no unquoted spaces, balanced brackets)
- [ ] Branch diamonds use explicit `-- 是 -->` / `-- 否 -->` labels
- [ ] Tensor transformations (reshape, permute, split, cat) are shown
- [ ] In-place mutations marked with distinct style (e.g. `[原地修改]` prefix)
