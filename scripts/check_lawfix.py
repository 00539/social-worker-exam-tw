# -*- coding: utf-8 -*-
"""檢查修法題現行答案檔：python check_lawfix.py s1"""
import json, os, sys
b = sys.argv[1]
src = json.load(open(os.path.join(os.path.dirname(__file__), '..', 'build', 'stale', b + '.json'), encoding='utf-8'))
o = json.load(open(os.path.join(os.path.dirname(__file__), 'lawfix', b + '.json'), encoding='utf-8'))
ids = [q['id'] for q in src]
err = [i for i in ids if i not in o] + [k for k in o if k not in ids]
for k, v in o.items():
    if not isinstance(v, dict) or set(v) - {'status', 'current', 'now', 'law'} or v.get('status') not in ('same', 'changed', 'void') \
       or not isinstance(v.get('now'), str) or len(v['now']) < 40 or not v.get('law') \
       or (v['status'] != 'void' and not (isinstance(v.get('current'), str) and v['current'] and set(v['current']) <= set('ABCD'))):
        err.append(k)
print('題數', len(ids), '已寫', len(o), '錯誤', len(err))
for e in err[:10]: print('  ', e)
sys.exit(1 if err else 0)
