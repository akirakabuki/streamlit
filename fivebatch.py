import streamlit as st
import numpy as np
from itertools import combinations
from statistics import mean, stdev

st.title("バッチ探索アプリ")

st.markdown("初期バッチ（2〜4件）と探索の `grid_step` を指定して、条件を満たす残りのバッチ候補を探索します。")

# 初期バッチ数選択
num_batches = st.selectbox("初期バッチ数 (2〜4)", [2, 3, 4])

initial_batches = []
st.markdown("### 初期バッチデータ入力")
for i in range(num_batches):
    cols = st.columns(3)
    with cols[0]:
        x = st.number_input(f"Batch {i+1} - X", min_value=94.5, max_value=98.5, step=0.1, format="%.2f", key=f"x{i}")
    with cols[1]:
        y = st.number_input(f"Batch {i+1} - Y", min_value=0.0, max_value=5.5, step=0.1, format="%.2f", key=f"y{i}")
    with cols[2]:
        st.write(f"X + Y = {x + y:.2f}")
    initial_batches.append((x, y))

# grid_stepの指定
grid_step = st.slider("探索刻み幅 (grid_step)", min_value=0.05, max_value=1.0, value=0.1, step=0.05)

# 探索ボタン
if st.button("探索開始"):

    def is_valid_combination(data, added_data):
        Xs = [x for x, _ in data]
        Ys = [y for _, y in data]

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
        if any(x < 94.5 or x > 98.5 for x in Xs):
            return False
        if any(not (99.0 <= x + y <= 100.0) for x, y in data):
            return False
        if not any(x >= 98 for x, _ in added_data):
            return False

        return True

    def search_combinations_within_range(initial_batches, grid_step=0.1):
        n = len(initial_batches)
        remaining = 5 - n
        X_range = np.arange(94.5, 98.5 + grid_step, grid_step)
        Y_range = np.arange(0.0, 5.5 + grid_step, grid_step)

        all_candidates = [
            (x, y) for x in X_range for y in Y_range if 99.0 <= x + y <= 100.0
        ]

        valid_results = []

        for combo in combinations(all_candidates, remaining):
            combined = initial_batches + list(combo)
            if is_valid_combination(combined, list(combo)):
                Xs = [x for x, _ in combined]
                score = mean(Xs) + 3 * stdev(Xs)
                valid_results.append((combo, score))

        valid_results.sort(key=lambda x: x[1], reverse=True)
        return valid_results

    with st.spinner("探索中..."):
        results = search_combinations_within_range(initial_batches, grid_step)

    st.success(f"探索完了！条件を満たす組合せが {len(results)} 件見つかりました。")

    for i, (combo, score) in enumerate(results[:5], 1):
        st.markdown(f"### Top {i} 組合せ (Xの平均+3σ={score:.3f})")
        for j, (x, y) in enumerate(combo, 1):
            st.write(f"追加Batch {j}: X={x:.2f}, Y={y:.2f}, X+Y={x+y:.2f}")
