import streamlit as st
from itertools import combinations
from statistics import mean, stdev

# 候補点の生成（X + Y = 100 を満たす点のみ）
def generate_candidates(x_min=94.5, x_max=98.5, step=0.1):
    candidates = []
    x = x_min
    while x <= x_max:
        y = 100.0 - x
        if 0 <= y <= 5.5:  # Yが非負かつ現実的な上限内
            candidates.append((round(x, 2), round(y, 2)))
        x = round(x + step, 10)
    return candidates

# 条件チェック関数
def is_valid_combination(full_data):
    Xs = [x for x, _ in full_data]
    Ys = [y for _, y in full_data]

    if len(set(Xs)) < 2:  # Xの多様性チェック（任意）
        return False

    x_mean = mean(Xs)
    y_mean = mean(Ys)
    if len(Xs) < 2 or len(Ys) < 2:
        return False
    x_std = stdev(Xs)
    y_std = stdev(Ys)

    # 条件1: Yの平均 + 3σ ≤ 5
    if y_mean + 3 * y_std > 5:
        return False

    # 条件2: Xの平均 - 3σ ∈ [94, 95)
    if not (94 <= x_mean - 3 * x_std < 95):
        return False

    # 条件3: 少なくとも1つのXが98以上
    if not any(x >= 98 for x in Xs):
        return False

    return True

# アプリ本体
def main():
    st.title("バッチ組み合わせ探索ツール (X+Y=100 固定)")

    st.markdown("### 🔢 初期バッチの入力（2〜4件）")
    n_initial = st.slider("初期バッチ数", 2, 4, 3)
    initial_batches = []
    for i in range(n_initial):
        col1, col2 = st.columns(2)
        with col1:
            x = st.number_input(f"Batch {i+1} - X", value=97.0, key=f"x_{i}")
        with col2:
            y = st.number_input(f"Batch {i+1} - Y", value=3.0, key=f"y_{i}")
        if abs(x + y - 100.0) > 1e-6:
            st.error(f"Batch {i+1} の X + Y が100ではありません")
        initial_batches.append((x, y))

    grid_step = st.number_input("グリッドステップ (X方向)", value=0.1, min_value=0.01, max_value=1.0, step=0.01)

    if st.button("組合せ探索"):
        st.markdown("## 🔍 結果")
        candidates = generate_candidates(step=grid_step)
        n_to_add = 5 - n_initial
        results = []

        for combo in combinations(candidates, n_to_add):
            full_data = initial_batches + list(combo)
            if is_valid_combination(full_data):
                Xs = [x for x, _ in full_data]
                x_mean = mean(Xs)
                x_std = stdev(Xs)
                x_score = x_mean + 3 * x_std
                results.append((combo, x_score))

        if results:
            results.sort(key=lambda x: x[1], reverse=True)

            for i, (combo, score) in enumerate(results[:5], 1):
                st.markdown(f"### ✅ Top {i} 組合せ (Xの平均+3σ={score:.3f})")

                full_data = initial_batches + list(combo)
                Xs = [x for x, _ in full_data]
                Ys = [y for _, y in full_data]
                x_mean = mean(Xs)
                y_mean = mean(Ys)
                x_std = stdev(Xs)
                y_std = stdev(Ys)

                st.write(f"📊 Xの平均 ± 3σ: [{x_mean - 3*x_std:.3f}, {x_mean + 3*x_std:.3f}]")
                st.write(f"📊 Yの平均 + 3σ: {y_mean + 3*y_std:.3f}")

                for j, (x, y) in enumerate(combo, 1):
                    st.write(f"追加Batch {j}: X={x:.2f}, Y={y:.2f}, X+Y={x+y:.2f}")
        else:
            st.warning("条件を満たす組み合わせが見つかりませんでした。")

if __name__ == "__main__":
    main()

