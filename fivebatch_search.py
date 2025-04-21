import streamlit as st
import pandas as pd
from statistics import mean, stdev
from itertools import combinations, product

# 条件を満たすかチェック
def satisfies_conditions(Xs, Ys):
    if len(Xs) < 2:
        return False
    x_mean = mean(Xs)
    x_std = stdev(Xs)
    y_mean = mean(Ys)
    y_std = stdev(Ys)

    return (
        (y_mean + 3 * y_std <= 5) and
        (94 <= x_mean - 3 * x_std < 95)
    )

# 条件を満たす組み合わせを探す
def find_valid_combinations(df):
    valid_combos = []
    for combo in combinations(df.itertuples(index=False), 5):
        Xs = [row.x for row in combo]
        Ys = [row.y for row in combo]
        if satisfies_conditions(Xs, Ys):
            valid_combos.append(combo)
    return valid_combos

# 新たに追加するバッチ候補生成（X + Y = 100）
def generate_candidate_batches(x_min=94.5, x_max=98.4, step=0.1):
    candidates = []
    x = x_min
    while x <= x_max:
        y = 100 - x
        candidates.append((round(x, 2), round(y, 2)))
        x = round(x + step, 10)
    return candidates

# 追加バッチによって条件を満たせるか探索
def search_with_additions(existing_data, candidates, max_add=3):
    for k in range(1, max_add + 1):
        for extra in combinations(candidates, k):
            merged = existing_data + list(extra)
            if len(merged) >= 5:
                for combo in combinations(merged, 5):
                    Xs = [x for x, _ in combo]
                    Ys = [y for _, y in combo]
                    if satisfies_conditions(Xs, Ys):
                        return combo
    return None

# Streamlit UI
def main():
    st.title("?? バッチ条件探索アプリ")

    uploaded_file = st.file_uploader("CSVファイルをアップロードしてください（batch, x, y）", type=["csv"])
    step = st.number_input("追加バッチ探索のステップ幅", min_value=0.01, max_value=1.0, value=0.1)

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.dataframe(df)

        existing_data = list(zip(df["x"], df["y"]))
        st.markdown("### ? 条件を満たす5バッチの組合せを探索中...")

        valid = find_valid_combinations(df)

        if valid:
            st.success(f"{len(valid)} 件の組合せが見つかりました。")
            for i, combo in enumerate(valid[:5]):
                Xs = [row.x for row in combo]
                Ys = [row.y for row in combo]
                st.markdown(f"#### 組合せ {i+1}")
                st.write(pd.DataFrame(combo))
                st.write(f"Xの平均±3σ: {mean(Xs) - 3*stdev(Xs):.2f} ～ {mean(Xs) + 3*stdev(Xs):.2f}")
                st.write(f"Yの平均+3σ: {mean(Ys) + 3*stdev(Ys):.2f}")
        else:
            st.warning("? 条件を満たす組合せが見つかりませんでした。")
            st.markdown("### ? 追加バッチで条件達成を試行中...")
            candidates = generate_candidate_batches(step=step)
            result = search_with_additions(existing_data, candidates)

            if result:
                st.success("追加バッチ込みで条件を満たす組合せが見つかりました！")
                df_result = pd.DataFrame(result, columns=["x", "y"])
                st.dataframe(df_result)
                Xs = [x for x, _ in result]
                Ys = [y for _, y in result]
                st.write(f"Xの平均±3σ: {mean(Xs) - 3*stdev(Xs):.2f} ～ {mean(Xs) + 3*stdev(Xs):.2f}")
                st.write(f"Yの平均+3σ: {mean(Ys) + 3*stdev(Ys):.2f}")
            else:
                st.error("追加しても条件を満たす組合せは見つかりませんでした。")

if __name__ == "__main__":
    main()
