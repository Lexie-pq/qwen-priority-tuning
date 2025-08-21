import json

# 输入输出文件（修改为实际路径）
input_file = r"D:\pythonstudy\intern\youshen\alpha_priority_lora.json"
output_file = r"D:\pythonstudy\intern\youshen\sharegpt_data3.json"

with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

converted = []

for item in data:
    conversations = []

    # system 内容来自原数据
    system_text = item.get("system", "")
    conversations.append({
        "from": "system",
        "value": system_text
    })

    # human 内容：instruction + input 拼接
    instruction_text = item.get("instruction", "")
    input_data = item.get("input", {})
    human_value = instruction_text
    if input_data:
        input_lines = [f"{k}: {v}" for k, v in input_data.items()]
        human_value += "\n" + "\n".join(input_lines)

    conversations.append({
        "from": "human",
        "value": human_value
    })

    # gpt 内容：output 拼接 <think> + 优先级
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
