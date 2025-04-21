import streamlit as st
import pandas as pd
import chardet
from statistics import mean, stdev
from itertools import combinations, product

# 条件を満たすかを判定する関数
def is_valid_batch_set(batches):
    x_vals = [b[1] for b in batches]
    y_vals = [b[2] for b in batches]

    if len(x_vals) < 2:
        return False

    y_mean = mean(y_vals)
    y_std = stdev(y_vals)
    if y_mean + 3 * y_std > 5:
        return False

    x_mean = mean(x_vals)
    x_std = stdev(x_vals)
    if not (94 <= x_mean - 3 * x_std < 95):
        return False

    return True

# 追加候補バッチを探索する関数
def generate_additional_batches(grid_step):
    x_candidates = [round(x, 2) for x in list(frange(94.5, 98.5, grid_step))]
    candidates = [(x, round(100 - x, 2)) for x in x_candidates if 94.5 <= x < 98.5 and 1.5 <= 100 - x <= 5.5]
    return candidates

# rangeのfloat版
def frange(start, stop, step):
    while start < stop:
        yield start
        start += step

# 文字コード自動検出
def detect_encoding(file):
    raw = file.read()
    result = chardet.detect(raw)
    encoding = result['encoding']
    file.seek(0)
    return encoding

def main():
    st.title("\U0001F4CA 5バッチ探索アプリ")

    uploaded_file = st.file_uploader("CSVファイルをアップロードしてください (batch,x,y)", type=["csv"])
    grid_step = st.number_input("追加バッチ探索のステップ幅 (例: 0.1)", min_value=0.01, max_value=1.0, value=0.1, step=0.01)
    st.text("条件")
    st.text("1. Yの平均+3σは5以下")
    st.text("    2. Xの平均－3σは94以上95未満")
    if uploaded_file:
        try:
            encoding = detect_encoding(uploaded_file)
            df = pd.read_csv(uploaded_file, encoding=encoding)
        except Exception as e:
            st.error(f"ファイルの読み込みに失敗しました: {e}")
            return

        if not {'batch', 'x', 'y'}.issubset(df.columns):
            st.error("CSVに必要な列 (batch, x, y) が含まれていません。")
            return

        st.dataframe(df)

        records = list(df.itertuples(index=False, name=None))
        found_sets = []

        # 既存データから条件に合う組み合わせを探索
        for combo in combinations(records, 5):
            if is_valid_batch_set(combo):
                found_sets.append(combo)
                if len(found_sets) >= 5:
                    break

        if found_sets:
            st.success(f"既存データで条件を満たす組み合わせが {len(found_sets)} 件見つかりました")
            for i, combo in enumerate(found_sets):
                st.subheader(f"組み合わせ {i+1}")
                st.table(pd.DataFrame(combo, columns=['batch', 'x', 'y']))
                x_vals = [b[1] for b in combo]
                y_vals = [b[2] for b in combo]
                st.write(f"X 平均 ± 3σ: {mean(x_vals):.2f} ± {3*stdev(x_vals):.2f}")
                st.write(f"Y 平均 + 3σ: {mean(y_vals) + 3*stdev(y_vals):.2f}")
        else:
            st.warning("既存データのみでは条件を満たす組み合わせは見つかりませんでした。追加候補を探索中…")
            additional_batches = generate_additional_batches(grid_step)
            for n_add in range(1, 4):
                for add_combo in combinations(additional_batches, n_add):
                    for orig_combo in combinations(records, 5 - n_add):
                        new_combo = list(orig_combo) + [(None, x, y) for x, y in add_combo]
                        if is_valid_batch_set(new_combo):
                            st.success(f"{n_add}個の追加バッチで条件を満たす組み合わせが見つかりました")
                            st.table(pd.DataFrame(new_combo, columns=['batch', 'x', 'y']))
                            x_vals = [b[1] for b in new_combo]
                            y_vals = [b[2] for b in new_combo]
                            st.write(f"X 平均 ± 3σ: {mean(x_vals):.2f} ± {3*stdev(x_vals):.2f}")
                            st.write(f"Y 平均 + 3σ: {mean(y_vals) + 3*stdev(y_vals):.2f}")
                            return

            st.error("条件を満たす組み合わせが見つかりませんでした。grid_stepを小さくして再試行してください。")

if __name__ == "__main__":
    main()
