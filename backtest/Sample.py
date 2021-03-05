import numpy as np
import pandas as pd

o = [
    206.2, 206.3, 208.4, 210, 208, 209, 202.5, 195.8, 196, 195, 200, 206, 209, 202.3, 201.3, 205, 205.2, 206.5, 205,
    206, 201.5, 200.5, 200.8, 202, 198.7, 198.6, 199.2, 198.5, 196.5, 201, 201, 203.8, 203, 203.6, 205.2, 208.1, 208.5,
    210.2, 209.6, 208.7, 207.5, 203, 199, 197
]
h = [
    207.8, 208, 212.5, 212.5, 212, 213, 208.5, 204, 203, 202, 206.5, 209, 210.9, 209.3, 205.4, 207, 209.2, 211, 208,
    208.2, 206.5, 204.2, 203.3, 204, 201, 201.6, 201.3, 200, 201.8, 203, 206, 206.3, 205.3, 206.3, 209.5, 210.8, 209.9,
    213.9, 213.2, 211.5, 211, 208, 203, 202
]
l = [
    206.2, 206.3, 208.4, 210, 208, 209, 202.5, 195.8, 196, 195, 200, 206, 209, 202.3, 201.3, 205, 205.2, 206.5, 205,
    206, 201.5, 200.5, 200.8, 202, 198.7, 198.6, 199.2, 198.5, 196.5, 201, 201, 203.8, 203, 203.6, 205.2, 208.1, 208.5,
    210.2, 209.6, 208.7, 207.5, 203, 199, 197
]
c = [
    206.8, 206.5, 212, 210.5, 210.8, 209.5, 202.5, 203, 196.3, 199.5, 206, 208.8, 209.3, 202.3, 205.2, 205.5, 208.5,
    206.7, 206.5, 206.8, 201.5, 203, 203.2, 202.7, 198.8, 200, 200.6, 198.9, 201.5, 201.5, 206, 204.3, 205.2, 203.8,
    209, 208.1, 209.5, 213.4, 211.4, 208.9, 208.1, 203.5, 199.1, 201.6
]

ary_mf = pd.Series(c) - pd.Series(c).shift(2)
# 買いに転換する場合 翌日のTBPは過去2日間のMFの小さいほうを前日の終値に足す
# 売りに転換する場合 翌日のTBPは過去2日間のMFの大きいほうを前日の終値に足す
# 過去2日間のMFとは今日と前日のMF
# TBP 上昇トレンド転換値
ary_TbppNext = pd.Series(c).shift(1) + np.min([ary_mf,
                                               ary_mf.shift(1)],
                                              axis=0)
# TBP 下降トレンド転換値
ary_TbpmNext = pd.Series(c).shift(1) + np.max([ary_mf,
                                               ary_mf.shift(1)],
                                              axis=0)
ary_TbpT = []  # Trend Balance Point トレンド方向
ary_TbpNext = []  # 翌日のTrend Balance Point
ary_tr = np.max([
    pd.Series(h) - pd.Series(l),
    (pd.Series(c).shift(1) - pd.Series(h)).abs(),
    (pd.Series(c).shift(1) - pd.Series(l)).abs(),
], axis=0)
ary_xb = np.average([h, l, c], axis=0)
ary_StpB = ary_xb - ary_tr
ary_StpS = ary_xb + ary_tr
ary_PrfB = ary_xb * 2 - l
ary_PrfS = ary_xb * 2 - h
# 自分でループしないと計算できないヤツラ
for idx in range(len(c)):
    if idx < 1:
        ary_TbpT.append(0)
        ary_TbpNext.append(0)
        continue

    # Trend Balance Point
    if c[idx] < ary_TbppNext[idx - 1]:
        ary_TbpNext.append(ary_TbpmNext[idx])
        ary_TbpT.append(-1)
    elif c[idx] > ary_TbpmNext[idx - 1]:
        ary_TbpNext.append(ary_TbppNext[idx])
        ary_TbpT.append(1)
    else:
        ary_TbpT.append(ary_TbpT[idx - 1])
        if ary_TbpT[idx - 1] > 0:
            ary_TbpNext.append(ary_TbppNext[idx])
        else:
            ary_TbpNext.append(ary_TbpmNext[idx])

df = pd.DataFrame(c, columns=['Close'])
df["MF"] = ary_mf
df["TR"] = ary_tr
df["XB"] = ary_xb
# df["TBPp"] = ary_TbppNext
# df["TBPm"] = ary_TbpmNext
df["Tbp"] = pd.Series(ary_TbpNext).shift(1)
df["TbpT"] = ary_TbpT
df["StpB"] = pd.Series(ary_StpB).shift(1)
df["StpS"] = pd.Series(ary_StpS).shift(1)
df["PrfB"] = pd.Series(ary_PrfB).shift(1)
df["PrfS"] = pd.Series(ary_PrfS).shift(1)

df.to_csv("hoge.csv")
print(df)
print("Tomorrow:" + str(ary_TbpNext.pop()))
