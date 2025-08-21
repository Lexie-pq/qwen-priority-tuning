import json

# 输入输出文件路径
input_file = r"D:\pythonstudy\intern\youshen\sharegpt_data3.json"
output_file = r"D:\pythonstudy\intern\youshen\sharegpt_data3_updated.json"

# 新的 system value 内容
new_system_value = (
    "该测试用例优先级评估规则将用例按影响程度分为P0至P4五个等级，"
    "P0表示系统主流程故障或严重违反法律法规及风控要求，阻断测试或上线流程，如登录失败、支付失败、实名认证失效、儿童防沉迷缺失、违规数据上传，"
    "P1表示非致命但影响核心业务流程或法律合规环节的高优先级问题，如版权不符的推荐页、用户协议弹窗缺失、支付页面风险提示缺失，"
    "P2为中优先级功能问题，即次主路径或非法规功能错误不影响主流程但降低体验，如二级模块失效、容错机制未触发、边界值逻辑错误，"
    "P3为边缘用例或非功能型问题，通常是可用性、交互、UI或兼容性问题不影响功能或法规，如Tab切换异常、文案错误、部分设备兼容失败，"
    "P4为纯展示或辅助性验证类问题，不影响功能、体验或法规，如页面样式对齐、颜色错位、图标替换无效；"
    "评估采用六大维度共30分，分别为功能关键性（主路径5分、子流程3分、边缘1分）、失败影响范围（系统级5分、模块中断3分、局部可接受1分）、"
    "法律法规合规性（国家强制5分、平台自律3分、无法规关联1分）、风控依赖性（支付/数据敏感5分、内容违规风险3分、无风险1分）、"
    "是否阻断测试流程（冒烟测试必测5分、模块级依赖3分、孤立用例1分）及仅UI或辅助（纯UI5分、有逻辑1分，作为扣分项），"
    "最终得分=前五项之和减去第六项，得分≥18为P0，14–17为P1，10–13为P2，6–9为P3，≤5为P4；"
    "在评估过程中仅使用用例标题、测试用例类型、前置条件、操作步骤、预期结果、功能模块六个字段，不考虑使用频率、历史缺陷或技术实现细节。"
)

# 读取原始 JSON 文件
with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# 遍历替换 system value
for item in data:
    if "conversations" in item:
        for conv in item["conversations"]:
            if conv.get("from") == "system":
                conv["value"] = new_system_value

# 写入新文件
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅ 已完成替换，输出文件保存在: {output_file}")
