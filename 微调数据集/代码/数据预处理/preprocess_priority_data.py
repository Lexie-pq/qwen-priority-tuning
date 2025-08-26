import pandas as pd
from sklearn.utils import resample
import os

# ---------- 设置文件路径 ----------
file_paths = [
    r"D:\实习\友声\项目用例\咪咕视频H5用例_20250711113604.xlsx",
    r"D:\实习\友声\项目用例\咪咕视讯app用例_20250711113428.xlsx",
    r"D:\实习\友声\项目用例\赛事数据系统用例_20250711135500.xlsx"
]

# 合并所有 Excel 文件为一个 DataFrame
def load_and_concat_excels(file_paths):
    df_all = pd.DataFrame()
    for path in file_paths:
        df = pd.read_excel(path)
        df_all = pd.concat([df_all, df], ignore_index=True)
    return df_all

# ---------- 数据清洗和标签检查 ----------
def clean_and_check(df):
    print("清洗前总样本数:", len(df))

    # 去除无优先级或用例标题的样本
    df = df[df["优先级"].notna()]
    df = df[df["用例标题"].notna()]
    print("清洗后剩余样本数:", len(df))

    # 输出标签分布
    label_counts = df["优先级"].value_counts().sort_index()
    print("\n当前优先级分布：")
    print(label_counts)

    return df

# ---------- 标签平衡处理 ----------
def balance_labels(df, upsample_targets=["P0", "P4"], downsample_targets=["P2"], random_state=42):
    dfs = []

    for label in df["优先级"].unique():
        df_label = df[df["优先级"] == label]

        if label in upsample_targets:
            # 上采样至与主类一致数量（如 P2）
            max_count = df["优先级"].value_counts().max()
            df_resampled = resample(df_label, replace=True, n_samples=max_count, random_state=random_state)
            dfs.append(df_resampled)
            print(f"↑ 上采样 {label} 至 {max_count} 条")
        elif label in downsample_targets:
            # 下采样至中等数量
            min_count = df["优先级"].value_counts().median()
            df_resampled = resample(df_label, replace=False, n_samples=int(min_count), random_state=random_state)
            dfs.append(df_resampled)
            print(f"↓ 下采样 {label} 至 {int(min_count)} 条")
        else:
            dfs.append(df_label)

    balanced_df = pd.concat(dfs).sample(frac=1, random_state=random_state).reset_index(drop=True)

    print("\n✅ 平衡后标签分布：")
    print(balanced_df["优先级"].value_counts().sort_index())

    return balanced_df

# ---------- 主执行流程 ----------
if __name__ == "__main__":
    df_raw = load_and_concat_excels(file_paths)
    df_clean = clean_and_check(df_raw)
    df_balanced = balance_labels(df_clean)

    # 导出清洗和标签平衡后的数据（可选）
    df_balanced.to_excel(r"D:\实习\友声\processed_balanced_cases.xlsx", index=False)
    print("\n已保存平衡后的数据到 processed_balanced_cases.xlsx")
