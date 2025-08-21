import json

# 输入输出文件
input_file = r"D:\pythonstudy\intern\youshen\alpha_priority_lora.json"
output_file = r"D:\pythonstudy\intern\youshen\sharegpt_data_1.json"

# 读取原始 Alpaca 格式 JSON
with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

converted = []

for item in data:
    conversations = []

    # human 内容：instruction + input 字典拼接
    instruction_text = item.get("instruction", "")
    input_data = item.get("input", {})
    input_lines = [f"{k}: {v}" for k, v in input_data.items()]
    human_value = instruction_text + "\n" + "\n".join(input_lines)

    conversations.append({
        "from": "human",
        "value": human_value
    })

    # gpt 内容：拼接 think 和 优先级
    output_data = item.get("output", {})
    gpt_value = ""
    if "think" in output_data:
        think_text = output_data["think"]
        think_lines = [f"{k}: {v}" for k, v in think_text.items()]
        gpt_value += "<think>\n" + "\n".join(think_lines) + "\n</think>\n"
    if "优先级" in output_data:
        gpt_value += output_data["优先级"]

    conversations.append({
        "from": "gpt",
        "value": gpt_value
    })

    converted.append({
        "conversations": conversations
    })

# 保存结果
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(converted, f, ensure_ascii=False, indent=2)

print(f"转换完成，已保存到 {output_file}")
