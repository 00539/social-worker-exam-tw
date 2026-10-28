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
                 q.get('stale') or 0, q.get('oldname') or 0, q.get('risk') or 0])
rows.sort(key=lambda r: (r[0], r[1], r[2]))

ess = [[ei[q['exam']], si[q['subject']], q['no'], q['text'], q['points'],
        q['page'], q['code'], q['tags'],
        q.get('stale') or 0, q.get('oldname') or 0, q.get('risk') or 0] for q in e]
ess.sort(key=lambda r: (r[0], r[1], r[2]))

from concepts import CONCEPTS
from lawcheck import LAWS
from essay_notes import NOTES
from lawnums import NUMS, CHECKED as NUMS_CHECKED
cons = [[c[0], c[1]] for c in CONCEPTS]
laws = sorted([[k, v['amended'], v['scope'], v['risk']] for k, v in LAWS.items()],
              key=lambda x: -x[1])

# 申論題擬答架構（僅供參考，非官方答案）
valid = {'%s|%s|%d' % (q['exam'], q['subject'], q['no']) for q in e}
bad = sorted(set(NOTES) - valid)
if bad:
    raise SystemExit('essay_notes 有對不上題庫的 key：\n  ' + '\n  '.join(bad))
enotes = {k: {'frame': v['frame'], 'trap': v.get('trap', '')} for k, v in NOTES.items()}
print('申論擬答架構 %d 題 / 共 %d 題' % (len(enotes), len(e)))

# 學者與理論：依 aliases 比對題幹、選項與申論題全文，統計實際出題次數
import re as _re
from scholars import SCHOLARS
def _pat(a):
    a = _re.escape(a)
    return _re.compile(r'(?<![A-Za-z])' + a + r'(?![A-Za-z])') if _re.match(r'[A-Za-z]', a) else _re.compile(a)
schol = []
for sc in SCHOLARS:
    pats = [_pat(a) for a in sc['aliases']]
    exc = sc.get('exclude', [])
    hit = lambda t: any(p.search(t) for p in pats) and not any(x in t for x in exc)
    mi = [i for i, r in enumerate(rows) if hit(r[3] + ' ' + ' '.join(r[4]))]
    ej = [i for i, r in enumerate(ess) if hit(r[3])]
    schol.append([sc['name'], sc['zh'], sc['subject'], sc['theory'], sc['points'],
                  [list(w) for w in sc['works']], sc['video'], mi, ej])
schol.sort(key=lambda x: -(len(x[7]) + 3 * len(x[8])))
print('學者 %d 位；出題 0 次者：%s' % (len(schol), [x[0] for x in schol if not x[7] and not x[8]]))

from news import NEWS, CHECKED as NEWS_CHECKED
news = sorted(NEWS, key=lambda n: n['date'], reverse=True)
print('時事 %d 則' % len(news))

payload = {'exams': exams, 'subjects': subs, 'rows': rows, 'ess': ess,
           'cons': cons, 'laws': laws, 'enotes': enotes,
           'nums': [list(n) for n in NUMS], 'nums_checked': NUMS_CHECKED,
           'scholars': schol, 'news': news, 'news_checked': NEWS_CHECKED}
os.makedirs(os.path.dirname(DST), exist_ok=True)
with open(DST, 'w', encoding='utf-8') as f:
    f.write('window.__QB=')
    json.dump(payload, f, ensure_ascii=False, separators=(',', ':'))
    f.write(';')

# 題庫檔網址加上內容雜湊，避免瀏覽器／GitHub Pages 快取造成「新網頁＋舊題庫」
import hashlib, re
_h = hashlib.sha1(open(DST, 'rb').read()).hexdigest()[:10]
_html = os.path.join(APP, 'index.html')
_t = open(_html, encoding='utf-8').read()
_t2 = re.sub(r'<script src="questions\.js(\?v=[0-9a-f]+)?"></script>',
             '<script src="questions.js?v=%s"></script>' % _h, _t)
if _t2 != _t:
    open(_html, 'w', encoding='utf-8', newline='\n').write(_t2)
print('題庫版本', _h)

print('exams', exams)
print('subjects', subs)
print('rows', len(rows), '| essays', len(ess))
print('size %.2f MB' % (os.path.getsize(DST) / 1024 / 1024))
