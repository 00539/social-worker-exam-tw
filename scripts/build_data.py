# -*- coding: utf-8 -*-
"""把 questions.json 壓成網頁用的 questions.js（同源 script，避開 fetch 限制）"""
import json, os

from paths import BUILD, APP

SRC = os.path.join(BUILD, 'questions.json')
ESS = os.path.join(BUILD, 'essays.json')
DST = os.path.join(APP, 'questions.js')

d = json.load(open(SRC, encoding='utf-8'))
e = json.load(open(ESS, encoding='utf-8'))
exams = sorted({q['exam'] for q in d})
subs = []
for q in d:
    if q['subject'] not in subs:
        subs.append(q['subject'])

ei = {e: i for i, e in enumerate(exams)}
si = {s: i for i, s in enumerate(subs)}

rows = []
for q in d:
    rows.append([ei[q['exam']], si[q['subject']], q['no'], q['stem'],
                 [q['options'][k] for k in 'ABCD'], q['answer'],
                 q['page'], q['code'], q['tags'],
                 q.get('stale') or 0, q.get('oldname') or 0])
rows.sort(key=lambda r: (r[0], r[1], r[2]))

ess = [[ei[q['exam']], si[q['subject']], q['no'], q['text'], q['points'],
        q['page'], q['code'], q['tags'],
        q.get('stale') or 0, q.get('oldname') or 0] for q in e]
ess.sort(key=lambda r: (r[0], r[1], r[2]))

from concepts import CONCEPTS
from lawcheck import LAWS
cons = [[c[0], c[1]] for c in CONCEPTS]
laws = sorted([[k, v[0]] for k, v in LAWS.items()], key=lambda x: -x[1])

payload = {'exams': exams, 'subjects': subs, 'rows': rows, 'ess': ess,
           'cons': cons, 'laws': laws}
os.makedirs(os.path.dirname(DST), exist_ok=True)
with open(DST, 'w', encoding='utf-8') as f:
    f.write('window.__QB=')
    json.dump(payload, f, ensure_ascii=False, separators=(',', ':'))
    f.write(';')

print('exams', exams)
print('subjects', subs)
print('rows', len(rows), '| essays', len(ess))
print('size %.2f MB' % (os.path.getsize(DST) / 1024 / 1024))
