# -*- coding: utf-8 -*-
"""把法規數字依「同一個數字」歸組（例如 24 小時），方便橫向比較不同法規。

只處理有條號的法規項目；學理項目（研究方法、人類行為）不納入。
一個項目若含多個數字（例：72 小時；3 個月）會出現在多個組。
"""
import re

UNITS = [  # (單位, 類別, 換算成可排序的值)
    ('分鐘', '時限與期間', 1 / 60), ('小時', '時限與期間', 1), ('日', '時限與期間', 24),
    ('星期', '時限與期間', 168), ('個月', '時限與期間', 720), ('年', '時限與期間', 8760),
    ('歲', '年齡', 1), ('人', '人數', 1), ('%', '比例與倍數', 1), ('倍', '比例與倍數', 100),
    ('元', '金額', 1), ('萬元', '金額', 1e4), ('億元', '金額', 1e8),
]
CATS = ['時限與期間', '年齡', '人數', '比例與倍數', '金額']
_U = {u: (c, f) for u, c, f in UNITS}
_NUM = r'\d[\d,]*(?:\.\d+)?'
_PAT = re.compile(r'(%s)(?:\s*至\s*(%s))?\s*(%s)' % (_NUM, _NUM,
                  '|'.join(sorted((re.escape(u) for u in _U), key=len, reverse=True))))
SKIP = {'1 人', '1 倍'}  # 「不得少於 1 人」「最低生活費 1 倍」這類太泛，分組沒意義


def tokens(text):
    out = []
    for m in _PAT.finditer(text):
        a, b, u = m.group(1), m.group(2), m.group(3)
        if u == '年' and re.match(r'\s*\d+\s*月', text[m.end():]):
            continue  # 日期（105 年 1 月 1 日）
        if u == '日' and re.search(r'月\s*$', text[:m.start()]):
            continue
        label = ('%s 至 %s %s' % (a, b, u)) if b else ('%s %s' % (a, u))
        if label in SKIP or label in out:
            continue
        out.append(label)
    return out


def sortkey(label):
    m = _PAT.match(label)
    cat, f = _U[m.group(3)]
    return (CATS.index(cat), float(m.group(1).replace(',', '')) * f, label)


def group(nums):
    """回傳 [[數字, 類別, [項目索引...]], ...]，依類別、數值排序"""
    g = {}
    for i, n in enumerate(nums):
        if '學理' in n[0]:
            continue
        for t in tokens(n[2]):
            g.setdefault(t, []).append(i)
    return [[k, _U[_PAT.match(k).group(3)][0], g[k]] for k in sorted(g, key=sortkey)]


if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    from lawnums import NUMS
    for k, c, ix in group(NUMS):
        print(c, k, len(ix), '／'.join(NUMS[i][0][:6] + NUMS[i][1] for i in ix))
