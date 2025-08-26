import pandas as pd
import os

# ✅ 原始数据路径
input_path = r"D:\实习\友声\processed_balanced_cases.xlsx"

# ✅ 清洗后的输出路径
output_path = r"D:\实习\友声\processed_balanced_cases_cleaned.xlsx"

# ✅ 要删除的列名（这些列你说明都是空的）
columns_to_remove = [
    "测试数据（可为空）", "步骤备注", "备注（可为空）",
    "一级目录", "二级目录", "三级目录", "四级目录", "五级目录",
    "用例描述", "用例结果", "附件"
]

# ✅ 读取 Excel
df = pd.read_excel(input_path)

# ✅ 删除存在的目标列（如果列确实存在）
df_cleaned = df.drop(columns=[col for col in columns_to_remove if col in df.columns])

# ✅ 保存为新的 Excel 文件
df_cleaned.to_excel(output_path, index=False)

print(f"✅ 清洗完成，已删除空列，结果保存至：{output_path}")
