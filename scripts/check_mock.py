# -*- coding: utf-8 -*-
"""檢查模擬試題檔：python check_mock.py m1"""
import json, os, sys, collections
from concepts import CONCEPTS
names = {c[1] for c in CONCEPTS}
b = sys.argv[1]
src = json.load(open(os.path.join(os.path.dirname(__file__), '..', 'build', 'mock', b + '.json'), encoding='utf-8'))
L = json.load(open(os.path.join(os.path.dirname(__file__), 'mock', b + '.json'), encoding='utf-8'))
err = []
for i, q in enumerate(L):
    need = {'stem', 'options', 'answer', 'why', 'basis', 'concepts'}
    if not isinstance(q, dict) or need - set(q) or set(q) - need - {'law'}:
        err.append((i, '欄位')); continue
    if sorted(q['options']) != list('ABCD') or not all(isinstance(v, str) and v.strip() for v in q['options'].values()):
        err.append((i, '選項'))
    if q['answer'] not in list('ABCD'): err.append((i, '答案'))
    if len(q['why']) < 60: err.append((i, '解析太短'))
    bad = [c for c in q['concepts'] if c not in names]
    if bad or not q['concepts']: err.append((i, '考點名稱', bad))
    if q['stem'] in src['recent_stems']: err.append((i, '抄原題'))
stems = collections.Counter(q.get('stem') for q in L)
err += [('重複題幹', s[:20]) for s, c in stems.items() if c > 1]
print('題數', len(L), '答案分布', dict(collections.Counter(q.get('answer') for q in L)), '錯誤', len(err))
for e in err[:15]: print('  ', e)
sys.exit(1 if err or len(L) < 80 else 0)
