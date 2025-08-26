import json

# 输入输出文件（修改为实际路径）
input_file = r"D:\pythonstudy\intern\youshen\alpha_priority_lora.json"
output_file = r"D:\pythonstudy\intern\youshen\sharegpt_data2.json"

with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

converted = []

for item in data:
    conversations = []

    # system 对应的 human 内容
    system_text = item.get("system", "")

    # human 内容：instruction + input 字段拼接成文本
    input_data = item.get("input", {})
    instruction_text = item.get("instruction", "")
    human_value = instruction_text
    if input_data:
        # 将 input 字典拼成文本
        input_lines = [f"{k}: {v}" for k, v in input_data.items()]
        human_value += "\n" + "\n".join(input_lines)

    # 添加 system 类型消息
    conversations.append({
        "from": system_text,
        "value": human_value
    })

    # 添加 gpt 内容
    output_data = item.get("output", {})
    gpt_value = ""
    # 如果 output 有 think 字段或者 Explanation，可以拼接
    if "think" in output_data:
        think_text = output_data["think"]
        # think 是字典，拼接成文本
        think_lines = [f"{k}: {v}" for k, v in think_text.items()]
        gpt_value += "<think>\n" + "\n".join(think_lines) + "\n</think>\n"
    # 加上优先级字段
    if "优先级" in output_data:
        gpt_value += output_data["优先级"]

    conversations.append({
        "from": "gpt",
        "value": gpt_value
    })

    converted.append({
        "conversations": conversations
    })

# 保存转换后的数据
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(converted, f, ensure_ascii=False, indent=2)

print(f"转换完成，已保存到 {output_file}")
