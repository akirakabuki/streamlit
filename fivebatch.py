import streamlit as st
from itertools import combinations
from statistics import mean, stdev

# 候補点生成：X + Y = 100 に限定
def generate_candidates(x_min=94.5, x_max=98.5, step=0.1):
    candidates = []
    x = x_min
    while x <= x_max:
        y = 100.0 - x
        if 0 <= y <= 5.5:
            candidates.append((round(x, 2), round(y, 2)))
        x = round(x + step, 10)
    return candidates

# 条件判定
def is_valid_combination(full_data):
    Xs = [x for x, _ in full_data]
    Ys = [y for _, y in full_data]

    if len(Xs) < 2:
        return False

    x_mean = mean(Xs)
    y_mean = mean(Ys)
    x_std = stdev(Xs)
    y_std = stdev(Ys)

    if y_mean + 3 * y_std > 5:
        return False

    if not (94 <= x_mean - 3 * x_std < 95):
        return False

    if not any(x >= 98 for x in Xs):
        return False

    return True

# Streamlit アプリ本体
def main():
    st.title("バッチ組み合わせ探索アプリ")

    st.markdown("### 🔢 初期バッチの入力")
    n_initial = st.slider("初期バッチ数を選択（2〜4）", 2, 4, 3)
    initial_batches = []
    for i in range(n_initial):
        col1, col2 = st.columns(2)
        with col1:
            x = st.number_input(f"Batch {i+1} - X", value=97.0, key=f"x_{i}")
        with col2:
            y = st.number_input(f"Batch {i+1} - Y", value=3.0, key=f"y_{i}")
        if abs(x + y - 100.0) > 0.5:
            st.warning(f"⚠️ Batch {i+1} の X + Y = {x + y:.2f}（100からの乖離）")
        initial_batches.append((x, y))

    grid_step = st.number_input("グリッドステップ（X方向）", value=0.1, min_value=0.01, max_value=1.0, step=0.01)

    if st.button("組合せ探索"):
        st.markdown("## 🔍 探索結果")
        candidates = generate_candidates(step=grid_step)
        n_to_add = 5 - n_initial
        results = []

        for combo in combinations(candidates, n_to_add):
            full_data = initial_batches + list(combo)
            if is_valid_combination(full_data):
                Xs = [x for x, _ in full_data]
                Ys = [y for _, y in full_data]
                x_mean = mean(Xs)
                y_mean = mean(Ys)
                x_std = stdev(Xs)
                y_std = stdev(Ys)
                x_score = x_mean + 3 * x_std
                results.append((combo, x_score, x_mean, x_std, y_mean, y_std))

        if results:
            results.sort(key=lambda x: x[1], reverse=True)

            for i, (combo, x_score, x_mean, x_std, y_mean, y_std) in enumerate(results[:5], 1):
                st.markdown(f"### ✅ Top {i} 組合せ（Xの平均+3σ={x_score:.3f}）")

                st.write(f"📊 Xの平均 ± 3σ: [{x_mean - 3*x_std:.3f}, {x_mean + 3*x_std:.3f}]")
                st.write(f"📊 Yの平均 + 3σ: {y_mean + 3*y_std:.3f}")

                for j, (x, y) in enumerate(combo, 1):
                    st.write(f"追加Batch {j}: X={x:.2f}, Y={y:.2f}")
        else:
            st.warning("⚠️ 条件を満たす組合せは見つかりませんでした。")

if __name__ == "__main__":
    main()

