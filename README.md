# 🚀 Qwen 微调项目：测试用例优先级判定助手（双语 / Bilingual）

---

## 中文版（Chinese）

### 摘要
本项目基于 Qwen-3 系列（0.6B / 1.7B）模型，使用规则驱动的测试用例数据对模型进行微调（fine-tuning），目标是构建一个**可解释**且**可复现**的优先级判定智能助手，用于将软件测试用例划分为 P0–P4 并输出维度化的判定理由（`<think>`）。微调前模型在优先级判定上存在混淆；微调后模型在判定准确性与可解释性上均有显著提升。更多详细量化与定性结果请参见项目结果材料： [结果文档](https://git.uusense.cn/lora/qwen-priority-tuning/tree/master/%E7%BB%93%E6%9E%9C%E6%96%87%E6%A1%A3)。

---

## 目录（Table of Contents）
1. 项目背景与目标  
2. 数据集说明  
3. 优先级判定规则（概述）  
4. 训练环境与资源  
5. 训练流程（逐步详述）  
6. 超参数与 LoRA 细节  
7. 检查点管理与模型选择策略  
8. 评估协议与指标定义  
9. 导出、部署与目录规范  
10. 可重复性与复现实验建议  
11. 快速复现（Quick Start）  
12. 附录与参考链接

---

## 1. 项目背景与目标
在工程化测试体系中，测试用例优先级的判定直接影响测试资源分配与上线风险控制。传统基于规则或人工经验的标注成本高且不易扩展。本项目以**规则增强的数据蒸馏（Rule-Enhanced Data Distillation）**为核心方法论，借助大语言模型的生成能力自动化标注并微调基础模型，使其能够在保持可解释性的同时实现自动化判定。

目标如下：
- 使 Qwen-3 系列在 P0–P4 优先级判定任务上具备可靠的分类能力；
- 输出带有维度化评分与理由的可解释推理轨迹（`<think>`）；
- 保证训练流程与评估步骤的可复现性与审计性。

---

## 2. 数据集说明
**训练集（Training）**  
- 条目：1295 条（Alpaca -> ShareGPT 转换后用于微调）  
- 处理方式：合并多源 Excel、字段筛选、缺失值剔除、类别平衡（对 P0/P4 上采样、对 P2 下采样）  
- 验证集：未单独导出文件；在微调时通过 WebUI 设置 `val_ratio=0.2` 随机从训练集抽取 20% 作为验证样本

**测试集（Hold-out test set）**  
- 条目：23 条（来自独立文件 `支持禁止系统录屏.xlsx`）  
- 说明：重新依据统一规则对测试集进行判定，**忽略原表中已有优先级标签**，仅作为模型泛化评估基准

**字段（仅使用）**：用例标题、测试用例类型、前置条件、操作步骤、预期结果、功能模块

---

## 3. 优先级判定规则（概述）
判定规则采用六维度量化评分体系（功能关键性 / 失败影响范围 / 法律法规合规性 / 风控依赖 / 是否阻断测试流程 / 仅 UI 或辅助（扣分）），最终得分映射到 P0–P4。每条训练样例在模型输出中应包含 `<think>` 字段，记录维度分数、理由与最终结论，使模型学习到“可解释决策路径”。

---

## 4. 训练环境与资源
**硬件**（示例 `nvidia-smi` 输出）：
```
NVIDIA-SMI 535.104.05    Driver Version: 535.104.05   CUDA Version: 12.2
GPU 0: NVIDIA GeForce RTX 3090 Ti (24GB)
示例显存占用：约 11508MiB / 24564MiB
```

**软件栈（建议）**：
- Docker 容器化运行 LLaMA-Factory（WebUI）  
- Python ≥ 3.8、PyTorch 或 vLLM（依赖 LLaMA-Factory 后端）  
- LoRA 支持库（如 peft、loralib 或自定义实现，根据 WebUI/框架兼容性选择）  

**建议预配置**：开启混合精度（FP16 / BF16，视框架支持），确保 NVIDIA 驱动与 CUDA 版本兼容。

---

## 5. 训练流程（逐步详述）

> 下述所有命令中的占位符均需替换为你的真实配置：`<YOUR_CONTAINER_NAME>`、`<YOUR_PORT>`、`<YOUR_LOCAL_PATH>`、`<YOUR_SERVER_IP>`。

### 5.1 容器与 WebUI
1. 进入容器：
```bash
docker exec -it <YOUR_CONTAINER_NAME> /bin/bash
```
2. 启动 WebUI（示例）：
```bash
export GRADIO_SERVER_PORT=<YOUR_PORT>
llamafactory-cli webui
```

### 5.2 数据上传与注册
1. 将训练/测试数据上载到服务器：
```bash
scp "<YOUR_LOCAL_PATH>/train.json" root@<YOUR_SERVER_IP>:/aidev/yzt/LLaMA-Factory/data/
scp "<YOUR_LOCAL_PATH>/test.json"  root@<YOUR_SERVER_IP>:/aidev/yzt/LLaMA-Factory/data/
```
2. 在服务器上检查文件并可选校验：
```bash
sha256sum /aidev/yzt/LLaMA-Factory/data/train.json
```
3. 在 WebUI 的 Dataset 管理页中注册数据集，确认字段映射与数据格式（ShareGPT 三角色或转换后的人机对话形式）。

### 5.3 训练配置（WebUI）
建议基线参数：
- 学习率（LR）：5e-6  
- 梯度累积（gradient_accumulation_steps）：2  
- 启用 LoRA（LoRA scale/alpha ≈ 16，或根据实现映射）  
- 验证集比例（val_ratio）：0.2（WebUI 运行时随机划分）  
- 批量大小（micro-batch）：根据显存调整  
- 混合精度：FP16 或 BF16（如果可用）  
- 随机种子：设置（例如 42）以提高可重复性

**注意**：WebUI 的字段命名/功能可能随版本更新而变化，请以实际界面为准并保存训练配置（导出 JSON）。

### 5.4 训练监控与日志
- 使用 Docker 日志或 WebUI 提供的监控视图观察训练损失/验证损失/自定义指标。  
- 将训练配置（超参、随机种子、数据版本）与训练日志归档到 `/aidev/yzt/LLaMA-Factory/logs/<run-id>/`。

---

## 6. 超参数与 LoRA 细节（建议与说明）
**LoRA 相关（概念性说明）**：
- LoRA 的核心参数：rank（r）、alpha（缩放因子）、dropout。常见实践：r ∈ {4,8,16}；alpha 与 r 共同影响梯度尺度（例如 alpha=16）。  
- 目标模块：通常应用于 attention 投影层（query/key/value）或 FFN 的线性层，具体取决于模型与 LoRA 实现。  
- 保存策略：LoRA 权重可单独保存为轻量适配器（adapter），便于在同一基座模型上切换任务。

**推荐超参数（基线）**：
- LR=5e-6，GradAcc=2，LoRA rank=8（可调），alpha≈16，micro-batch 依显存设置，混合精度 FP16。

---

## 7. 检查点管理与模型选择策略
**检查点策略**：
- 建议按固定间隔（例如每 N steps / 每 epoch）保存检查点，保存内容应包括：模型权重、LoRA 权重（若分离）、训练配置（config.json）、当前步数与随机种子、优化器状态（可选）。  
- 存放目录建议：`/aidev/yzt/LLaMA-Factory/Qwen/outputs/<model-name>/checkpoints/`

**模型选择（基于自定义 Acc）**：
- 自定义 Acc 定义：若模型预测优先级与 Grok 参考值的差异在 ±1 等级内，则计为正确。  
- 在验证集上计算 Accuracy（按上述规则），并结合验证 loss 选择 top-K 检查点（例如 top-3）。  
- 将候选检查点在**独立测试集（23 条）**上展开最终评估与人工抽样质检 `<think>` 内容。

---

## 8. 评估协议与指标定义
**自动化指标**：
- Accuracy（±1 等级容差）  
- 混淆矩阵（各类误判分布）  
- 按类 Precision / Recall / F1（用于理解模型对 P0–P4 的区分能力）  

**人工质检**：
- 抽样 10–20% 的模型输出，人工检查 `<think>` 中维度评分与理由是否符合规则书逻辑（防止模型仅“记忆答案模板”）。

**统计报告建议**：
- 提供总体 Accuracy、按类指标、混淆矩阵的可视化（heatmap）、若干具有代表性的 `input + model <think> + reference` 的案例分析。

---

## 9. 导出、部署与目录规范
**导出目录示例**：
```text
/aidev/yzt/LLaMA-Factory/Qwen/outputs/
  Qwen-0.6B-priority-YYYYMMDD-v1/
    checkpoints/
    exported_model/
    training_config.json
  Qwen-1.7B-priority-YYYYMMDD-v1/
```

**建议命名规范**：`<base>-<task>-<YYYYMMDD>-v<N>`（例如 `Qwen-0.6B-priority-20250826-v1`）

---

## 10. 可重复性与复现实验建议
- 若需严格可复现的验证集切分，请在本地（或 CI）提前按固定随机种子拆分并上传 `train.json`、`valid.json`、`test.json`，避免 WebUI 的运行时随机切分带来差异。  
- 保存并归档训练配置（JSON/YAML）、随机种子、环境镜像（Dockerfile / image id）和训练日志。  
- 若使用多次实验比较（A/B），请确保在相同数据分割与随机种子下进行。

---

## 11. 快速复现（Quick Start）
```bash
# 1) 上传数据（替换占位符）
scp "<YOUR_LOCAL_PATH>/train.json" root@<YOUR_SERVER_IP>:/aidev/yzt/LLaMA-Factory/data/
scp "<YOUR_LOCAL_PATH>/test.json"  root@<YOUR_SERVER_IP>:/aidev/yzt/LLaMA-Factory/data/

# 2) 进入容器并启动 WebUI
docker exec -it <YOUR_CONTAINER_NAME> /bin/bash
export GRADIO_SERVER_PORT=<YOUR_PORT>
llamafactory-cli webui

# 3) 在 WebUI 中注册数据并配置训练（val_ratio=0.2）
# 4) 启动训练并监控日志
```

---

## 12. 附录与参考链接
- LLaMA-Factory: https://github.com/hiyouga/LLaMA-Factory  
- 结果文档（内部仓库）：[结果文档](https://git.uusense.cn/lora/qwen-priority-tuning/tree/master/%E7%BB%93%E6%9E%9C%E6%96%87%E6%A1%A3)  
- 数据构建说明：`Dataset Readme.md`（仓库内）

---

## English Version

### Abstract
This project fine-tunes the Qwen-3 family (0.6B / 1.7B) on a rule-annotated dataset of software test cases to produce an interpretable assistant that assigns test-case priorities P0–P4 and emits dimensioned reasoning traces (`<think>`). Pre-finetuning, the base model exhibited severe misclassification (treating P4 as highest priority). Post-finetuning, the model achieves substantially improved accuracy and produces justifiable decision traces. For detailed quantitative and qualitative results, see the project results material: [Results](https://git.uusense.cn/lora/qwen-priority-tuning/tree/master/%E7%BB%93%E6%9E%9C%E6%96%87%E6%A1%A3).

---

### Table of Contents
1. Background & Objectives  
2. Dataset Description  
3. Prioritization Rule (Summary)  
4. Environment & Resources  
5. Training Procedure (Detailed)  
6. Hyperparameters & LoRA Details  
7. Checkpointing & Model Selection Strategy  
8. Evaluation Protocol & Metrics  
9. Export, Deployment & Directory Conventions  
10. Reproducibility Recommendations  
11. Quick Start  
12. Appendix & References

---

### 1. Background & Objectives
Test-case prioritization directly affects test resource allocation and release risk. This project adopts a Rule-Enhanced Data Distillation paradigm: a human-expert rulebook is used to generate consistent labels and dimensioned reasoning which are then used to fine-tune LLMs so they can generalize and produce interpretable outputs.

Objectives:
- Train Qwen-3 models to reliably classify priorities P0–P4.  
- Ensure model outputs include dimensioned reasoning traces (`<think>`).  
- Maintain reproducibility and auditable training/evaluation logs.

---

### 2. Dataset Description
**Training set**: 1295 examples (Alpaca -> ShareGPT converted)  
- Preprocessing: multi-source merging, field filtering, missing-value removal, class balancing (oversample P0/P4, undersample P2)  
- Validation: not stored separately; WebUI `val_ratio=0.2` randomly splits 20% of training data for validation during training.

**Test set**: 23 examples (hold-out; source file `支持禁止系统录屏.xlsx`)  
- Re-annotated according to the project's rulebook; original priority labels in source file are ignored.

**Used fields**: title, case type, precondition, steps, expected result, module.

---

### 3. Prioritization Rule (Summary)
A six-dimension scoring schema maps to P0–P4. Each training sample's output must include `<think>` with per-dimension scores, reasoning and final priority.

---

### 4. Environment & Resources
**Hardware (example `nvidia-smi`)**:
```
NVIDIA-SMI 535.104.05    Driver Version: 535.104.05   CUDA Version: 12.2
GPU 0: NVIDIA GeForce RTX 3090 Ti (24GB)
Example memory usage: ~11508MiB / 24564MiB
```

**Software stack (recommended)**:
- Dockerized LLaMA-Factory (WebUI)  
- Python >= 3.8, PyTorch or vLLM backend  
- LoRA-supporting library (peft, loralib, etc.)

---

### 5. Training Procedure (Detailed)
All placeholder tokens must be replaced: `<YOUR_CONTAINER_NAME>`, `<YOUR_PORT>`, `<YOUR_LOCAL_PATH>`, `<YOUR_SERVER_IP>`.

**Container & WebUI**:
```bash
docker exec -it <YOUR_CONTAINER_NAME> /bin/bash
export GRADIO_SERVER_PORT=<YOUR_PORT>
llamafactory-cli webui
```

**Data upload**:
```bash
scp "<YOUR_LOCAL_PATH>/train.json" root@<YOUR_SERVER_IP>:/aidev/yzt/LLaMA-Factory/data/
scp "<YOUR_LOCAL_PATH>/test.json"  root@<YOUR_SERVER_IP>:/aidev/yzt/LLaMA-Factory/data/
sha256sum /aidev/yzt/LLaMA-Factory/data/train.json
```

**WebUI dataset registration and field mapping**.

**Training configuration (baseline)**:
- LR: 5e-6  
- gradient_accumulation_steps: 2  
- LoRA: enabled (scale/alpha ≈ 16)  
- val_ratio: 0.2 (random split)  
- mixed precision: FP16 (if supported)  
- seed: set for reproducibility

**Monitoring & logging**: use Docker logs and WebUI graphs; archive logs to `/aidev/yzt/LLaMA-Factory/logs/<run-id>/`.

---

### 6. Hyperparameters & LoRA Details
- LoRA tuneable params: rank (r), alpha, dropout. Typical r ∈ {4,8,16}; alpha scales gradient contributions.  
- Target modules: attention projection layers or FFN linear layers.  
- Save LoRA adapters separately for lightweight task adapters.

---

### 7. Checkpointing & Model Selection
- Save checkpoints periodically (every N steps or per epoch). Save model weights, LoRA adapters, training config, and optionally optimizer state.  
- Selection: compute custom accuracy on validation set (±1 priority tolerance) and select top-K checkpoints for final testing on the hold-out test set.

---

### 8. Evaluation Protocol & Metrics
- Accuracy with ±1 tolerance  
- Confusion matrix, per-class precision/recall/F1  
- Human spot-check of `<think>` traces

---

### 9. Export, Deployment & Directory Conventions
Export under:
```
/aidev/yzt/LLaMA-Factory/Qwen/outputs/<model-name>/
```
Naming: `<base>-<task>-YYYYMMDD-vN`, e.g., `Qwen-0.6B-priority-20250826-v1`.

---

### 10. Reproducibility Recommendations
- For deterministic validation splits, pre-split and upload `train.json` / `valid.json`.  
- Save Docker image id and environment spec.  
- Fix seeds and document configurations.

---

### 11. Quick Start
```bash
scp "<YOUR_LOCAL_PATH>/train.json" root@<YOUR_SERVER_IP>:/aidev/yzt/LLaMA-Factory/data/
docker exec -it <YOUR_CONTAINER_NAME> /bin/bash
export GRADIO_SERVER_PORT=<YOUR_PORT>
llamafactory-cli webui
# Register dataset, set val_ratio=0.2, start training
```

---

### 12. Appendix & References
- LLaMA-Factory: https://github.com/hiyouga/LLaMA-Factory  
- Results: [Results](https://git.uusense.cn/lora/qwen-priority-tuning/tree/master/%E7%BB%93%E6%9E%9C%E6%96%87%E6%A1%A3)  
- Dataset build details: `Dataset Readme.md` (in repo)

---

**占位符说明**：所有 `<>` 包含的值为占位符，请在运行前替换为真实配置。  
