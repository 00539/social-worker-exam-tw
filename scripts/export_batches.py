# -*- coding: utf-8 -*-
"""把測驗題切批，交給解析撰寫用（社會工作管理 115 年起停考，不納入）"""
import json, os
from paths import BUILD
from concepts import CONCEPTS
d = json.load(open(os.path.join(BUILD, 'questions.json'), encoding='utf-8'))
by = {}
for q in d:
    if q['subject'] == '社會工作管理':
        continue
    by.setdefault(q['subject'], []).append(q)
n = 0
for sub, qs in by.items():
    qs.sort(key=lambda q: (q['exam'], q['no']))
    for i in range(0, len(qs), 170):
        n += 1
        out = [{'id': '%s|%s|%d' % (q['exam'], q['subject'], q['no']),
                'stem': q['stem'], 'options': q['options'], 'answer': q['answer'],
                'concepts': [CONCEPTS[t][1] for t in q['tags']],
                'amended_laws': q.get('stale') or []} for q in qs[i:i + 170]]
        json.dump(out, open(os.path.join(BUILD, 'exb', 'b%02d.json' % n), 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
print(n)
