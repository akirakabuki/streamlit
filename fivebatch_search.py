import streamlit as st
import pandas as pd
from statistics import mean, stdev
from itertools import combinations, product

# �����𖞂������`�F�b�N
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

# �����𖞂����g�ݍ��킹��T��
def find_valid_combinations(df):
    valid_combos = []
    for combo in combinations(df.itertuples(index=False), 5):
        Xs = [row.x for row in combo]
        Ys = [row.y for row in combo]
        if satisfies_conditions(Xs, Ys):
            valid_combos.append(combo)
    return valid_combos

# �V���ɒǉ�����o�b�`��␶���iX + Y = 100�j
def generate_candidate_batches(x_min=94.5, x_max=98.4, step=0.1):
    candidates = []
    x = x_min
    while x <= x_max:
        y = 100 - x
        candidates.append((round(x, 2), round(y, 2)))
        x = round(x + step, 10)
    return candidates

# �ǉ��o�b�`�ɂ���ď����𖞂����邩�T��
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
    st.title("?? �o�b�`�����T���A�v��")

    uploaded_file = st.file_uploader("CSV�t�@�C�����A�b�v���[�h���Ă��������ibatch, x, y�j", type=["csv"])
    step = st.number_input("�ǉ��o�b�`�T���̃X�e�b�v��", min_value=0.01, max_value=1.0, value=0.1)

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.dataframe(df)

        existing_data = list(zip(df["x"], df["y"]))
        st.markdown("### ? �����𖞂���5�o�b�`�̑g������T����...")

        valid = find_valid_combinations(df)

        if valid:
            st.success(f"{len(valid)} ���̑g������������܂����B")
            for i, combo in enumerate(valid[:5]):
                Xs = [row.x for row in combo]
                Ys = [row.y for row in combo]
                st.markdown(f"#### �g���� {i+1}")
                st.write(pd.DataFrame(combo))
                st.write(f"X�̕��ρ}3��: {mean(Xs) - 3*stdev(Xs):.2f} �` {mean(Xs) + 3*stdev(Xs):.2f}")
                st.write(f"Y�̕���+3��: {mean(Ys) + 3*stdev(Ys):.2f}")
        else:
            st.warning("? �����𖞂����g������������܂���ł����B")
            st.markdown("### ? �ǉ��o�b�`�ŏ����B�������s��...")
            candidates = generate_candidate_batches(step=step)
            result = search_with_additions(existing_data, candidates)

            if result:
                st.success("�ǉ��o�b�`���݂ŏ����𖞂����g������������܂����I")
                df_result = pd.DataFrame(result, columns=["x", "y"])
                st.dataframe(df_result)
                Xs = [x for x, _ in result]
                Ys = [y for _, y in result]
                st.write(f"X�̕��ρ}3��: {mean(Xs) - 3*stdev(Xs):.2f} �` {mean(Xs) + 3*stdev(Xs):.2f}")
                st.write(f"Y�̕���+3��: {mean(Ys) + 3*stdev(Ys):.2f}")
            else:
                st.error("�ǉ����Ă������𖞂����g�����͌�����܂���ł����B")

if __name__ == "__main__":
    main()
