# 📑 软件测试用例优先级数据集构建说明 (Dataset Construction Report)

---

## 🔹 中文版本

### 1. 项目背景与目标

在实际的软件测试过程中，不同的测试用例其重要性与紧急程度存在显著差异。若缺乏科学合理的优先级划分，可能导致有限的测试资源未能集中在最关键的路径上，进而增加软件质量与交付风险。为解决这一问题，本项目旨在构建一个基于**规则驱动的测试用例优先级标注数据集**，以支撑大语言模型在该任务上的微调与推理能力学习。

数据集的核心目标包括：

- 建立一套**可解释的优先级评判标准 (P0–P4)**。
- 在标注数据中保留**详细推理过程 (Reasoning Trace)**，以便模型学习判定逻辑。
- 提供多种微调框架可直接使用的格式 (Alpaca / ShareGPT)。

---

### 2. 数据来源与预处理

**训练/验证数据来源**：来自企业内部的多个测试用例管理表格，包括：

- 咪咕视频 H5 测试用例
- 咪咕视讯 App 测试用例
- 赛事数据系统测试用例

**训练/验证集处理方式**：

1. **合并表格**：将不同来源的 Excel 文件合并为统一的数据表。
2. **字段筛选**：仅保留与判定相关的六个核心字段：
   - 用例标题
   - 用例类型
   - 前置条件
   - 执行步骤
   - 预期结果
   - 功能模块
3. **缺失值处理**：剔除缺少 *优先级* 或 *用例标题* 的记录。
4. **冗余字段剔除**：移除“附件”“备注”“测试数据”等无关字段。
5. **验证集划分**：未单独生成验证集文件，而是在微调训练时通过 **WebUI 参数设置**，以 0.2 的比例在训练过程中自动随机划分。

**类别平衡处理**：

- 在原始数据中，不同优先级样本分布极度不均衡（例如 P2 样本数量远超 P0、P4）。
- 使用 `sklearn.utils.resample` 进行 **上采样 (针对 P0、P4)** 与 **下采样 (针对 P2)**。
- 平衡后的数据在类别上更加均匀，有助于避免模型训练过程中的偏置。

---

### 3. 优先级判定规则设计

我制定了一份系统化的 **《软件测试用例优先级判定规则》**，该规则融合了 **ISTQB 国际软件测试标准**与**企业测试实践经验**。规则核心要素如下：

#### (1) 优先级等级划分 (P0–P4)

- **P0：致命级**，关键路径/支付/合规阻断，系统核心功能不可用。
- **P1：高优先级**，核心功能严重异常但可部分绕过，影响大规模用户体验。
- **P2：中优先级**，普通功能缺陷，影响范围中等，可在后续迭代修复。
- **P3：低优先级**，边缘功能异常，不影响主要业务流程。
- **P4：展示验证**，仅 UI/样式/辅助验证，基本不影响用户核心体验。

#### (2) 六维度量化评分体系 (满分 30 分)

1. 功能关键性 (0–6)
2. 失败影响范围 (0–6)
3. 法律法规合规性 (0–6)
4. 风控依赖性 (0–6)
5. 是否阻断测试流程 (0–6)
6. 仅 UI 或辅助验证 (-0–6)

#### (3) 分数到优先级的映射

- **≥18 → P0**
- **14–17 → P1**
- **10–13 → P2**
- **6–9 → P3**
- **≤5 → P4**

该规则确保了 **定量 + 定性结合** 的判定机制，既可保证一致性，又具备可解释性。

---

### 4. 数据标注与 Alpaca 格式构建

**标注过程**：

- 通过大模型 (如 Grok) 调用优先级规则，对清洗后的用例逐条进行判定。
- 生成输出时，严格要求包含 **两部分信息**：
  1. `<think>` —— 推理轨迹，包括各维度打分、分析过程与优先级结论。
  2. 最终结论 —— 直接给出 P0–P4 的结果。

**训练/验证集规模**：最终生成 **1295 条 Alpaca 格式样本**，涵盖所有优先级类别。

**示例 (Alpaca 格式)**：

```json
{
  "instruction": "请根据优先级规则对以下测试用例进行判定。",
  "input": "标题：用户支付失败后是否提示重试\n类型：功能测试...",
  "output": "<think>...详细推理过程...</think> 最终优先级：P0"
}
```

---

### 5. ShareGPT 格式转换

为适配 **LLaMA-Factory** 等主流微调框架，编写脚本将 Alpaca 数据转换为 ShareGPT 格式。

我尝试了三种设计方案：

- **方案一**：仅保留 `human` 与 `gpt`。
- **方案二**：引入 `system` 存放规则文档，`human` 存放用例输入。
- **方案三**：完整三角色区分：
  - `system`：优先级规则文档
  - `human`：测试用例输入
  - `gpt`：包含 `<think>` 的推理与结论

**示例 (ShareGPT 格式)**：

```json
[
  {
    "conversations": [
      {"from": "system", "value": "软件测试用例优先级判定规则..."},
      {"from": "human", "value": "标题：用户支付失败后..."},
      {"from": "gpt", "value": "<think>...推理过程...</think> 最终优先级：P0"}
    ]
  }
]
```

---

### 6. 测试集构建

**测试集来源**：独立于训练/验证数据，来自全新的文件 **《支持禁止系统录屏.xlsx》**。

**构建方法**：

- 从文件中提取 23 条测试用例数据。
- **不使用原表格中的优先级标签**，完全基于项目制定的优先级规则重新判定。
- 输入字段与训练集保持一致：
  - 用例标题
  - 测试用例类型
  - 前置条件
  - 操作步骤
  - 预期结果
  - 功能模块
- 转换为 **ShareGPT 格式**，其中 `system` 存放优先级规则，`human` 存放测试用例输入，`gpt` 输出包含 `<think>` 详细推理和最终优先级结论。
- **测试集规模**：共 **23 条**，覆盖不同功能模块与场景。

**用途**：该测试集用于在模型微调完成后，对模型在 **优先级判定任务上的泛化质量** 进行独立检验。

---

### 7. 方法论总结

该数据集的构建过程可概括为：

- **规则增强型数据蒸馏 (Rule-Enhanced Data Distillation)**。
- 结合 **专家规则 (Teacher Policy)** 与 **大语言模型生成能力**，实现自动化标注。
- 数据样本中保留了 **推理轨迹 (Reasoning Trace)**，有助于模型学习判定逻辑，而不仅是结果。

该方法超越了传统的“标签清洗”或“众包标注”，属于 **知识蒸馏 (Knowledge Distillation) + 规则增强标注 (Rule-Augmented Annotation)** 的结合体。

---

## 🔹 English Version

### 1. Background & Objectives

In practical software testing, test cases differ significantly in terms of **criticality** and **urgency**. Without a well-defined prioritization mechanism, limited testing resources may fail to focus on mission-critical functionalities, thereby increasing delivery risks. To address this challenge, we constructed a **rule-driven dataset for test case prioritization**, designed to support LLM fine-tuning and reasoning enhancement.

**Key objectives:**

- Establish an **interpretable prioritization framework (P0–P4)**.
- Preserve **detailed reasoning traces (Reasoning Trace)** in each sample.
- Provide multiple fine-tuning formats (Alpaca / ShareGPT).

---

### 2. Data Sources & Preprocessing

**Training/Validation Sources:** Multiple enterprise-level test case sheets, including:

- Migu Video H5 test cases
- Migu Video App test cases
- Sports Data System test cases

**Training/Validation Handling:**

- Preprocessed by merging, selecting six critical fields, removing missing/irrelevant records.
- Validation set was **not separately constructed**; instead, during fine-tuning training, a **0.2 ratio** was applied in WebUI to randomly split validation samples.

**Class Balancing:**

- Original dataset was highly imbalanced (e.g., P2 dominating).
- Applied **oversampling for P0/P4** and **undersampling for P2**.
- Final distribution achieved greater balance, reducing bias during training.

---

### 3. Prioritization Rule Framework

A formal **Test Case Prioritization Rulebook** was developed, integrating **ISTQB standards** and enterprise QA practices.

#### (1) Priority Levels (P0–P4)

- **P0 (Critical):** Fatal defects in core flows (payment, compliance, authentication).
- **P1 (High):** Severe functional failures with partial workarounds.
- **P2 (Medium):** Normal functionality issues with moderate scope.
- **P3 (Low):** Peripheral feature malfunctions with minimal impact.
- **P4 (Cosmetic):** Purely UI-level or auxiliary validations.

#### (2) Six-Dimension Scoring (0–30)

1. Functional Criticality
2. Impact Scope
3. Legal/Regulatory Compliance
4. Risk Management Dependency
5. Test Process Blockage
6. UI/Display-only (deductive factor)

#### (3) Score-to-Priority Mapping

- **≥18 → P0**
- **14–17 → P1**
- **10–13 → P2**
- **6–9 → P3**
- **≤5 → P4**

---

### 4. Annotation & Alpaca Dataset Construction

**Annotation Process:**

- LLMs applied the rulebook to cleaned test cases.
- Each output contained:
  1. `<think>` reasoning trace (dimension-wise scoring + analysis).
  2. Final priority classification (P0–P4).

**Training/Validation Size:** 1295 Alpaca-formatted samples.

**Example (Alpaca format):**

```json
{
  "instruction": "Determine the test case priority using the given rulebook.",
  "input": "Title: Payment retry after failure...",
  "output": "<think>...detailed reasoning...</think> Final Priority: P0"
}
```

---

### 5. ShareGPT Conversion

For compatibility with frameworks like **LLaMA-Factory**, Alpaca data was converted into ShareGPT format.

**Design Variants:**

- **Option 1:** Only `human` and `gpt`.
- **Option 2:** Add `system` for rulebook, `human` for test input.
- **Option 3:** Full 3-role separation.

---

### 6. Test Set Construction

**Source:** Independent from training/validation, using the file **“支持禁止系统录屏.xlsx”**.

**Construction Method:**

- Extracted **23 test cases** from the file.
- **Ignored original priority labels**; re-annotated according to the rulebook.
- Retained six input fields: Title, Type, Precondition, Steps, Expected Result, Module.
- Converted into **ShareGPT format** with:
  - `system`: rulebook
  - `human`: test input
  - `gpt`: `<think>` reasoning + final conclusion

**Purpose:** This test set serves as an **independent evaluation benchmark** to measure fine-tuned model performance on priority judgment.

---

### 7. Methodological Summary

The entire pipeline represents a form of **Rule-Enhanced Data Distillation**, combining:

- **Expert Rulebook (Teacher Policy)** for consistency.
- **LLM Reasoning Generation** for scalability.
- **Reasoning Trace Preservation** for interpretability.

This approach surpasses conventional label-cleaning or crowdsourced annotation, and aligns with **Knowledge Distillation + Rule-Augmented Annotation** paradigms.

---

