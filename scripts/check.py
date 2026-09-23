# -*- coding: utf-8 -*-
import json, random, re, collections

import os
from paths import BUILD

P = os.path.join(BUILD, 'questions.json')
d = json.load(open(P, encoding='utf-8'))
print('總題數', len(d))

bad = []
for q in d:
    tag = f"{q['exam']}/{q['subject']}/{q['no']}"
    if len(q['options']) != 4:
        bad.append((tag, '選項數 ' + str(len(q['options']))))
    for k, v in q['options'].items():
        if len(v) < 2:
            bad.append((tag, f'選項{k}過短: {v!r}'))
    if len(q['stem']) < 8:
        bad.append((tag, f'題幹過短: {q["stem"]!r}'))
    if len(q['stem']) > 500:
        bad.append((tag, f'題幹過長 {len(q["stem"])}'))
    if re.search(r'[\ue000-\uf8ff]', q['stem'] + ''.join(q['options'].values())):
        bad.append((tag, 'PUA殘留'))
    if q['answer'] not in ('A', 'B', 'C', 'D') and not re.fullmatch(r'[ABCD]{2,4}', q['answer']):
        bad.append((tag, '答案異常 ' + q['answer']))

print('異常', len(bad))
for t, m in bad[:40]:
    print(' ', t, m)

print('\n答案分布', collections.Counter(q['answer'] for q in d).most_common())
print('題幹長度 max', max(len(q['stem']) for q in d))

print('\n--- 隨機抽 3 題 ---')
random.seed(7)
for q in random.sample(d, 3):
    print(f"[{q['exam']} {q['subject']} 第{q['no']}題] 答:{q['answer']}")
    print(' 題幹:', q['stem'])
    for k in 'ABCD':
        print(f'   ({k})', q['options'][k])
    print()
