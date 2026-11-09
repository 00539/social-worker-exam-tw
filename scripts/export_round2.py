# -*- coding: utf-8 -*-
"""第二輪撰寫素材：社會工作管理解析批次、修法題現行答案批次、模擬試題素材"""
import json, os, collections
from paths import BUILD
from concepts import CONCEPTS
from lawcheck import LAWS
from news import NEWS
from lawnums import NUMS
d = json.load(open(os.path.join(BUILD, 'questions.json'), encoding='utf-8'))
qid = lambda q: '%s|%s|%d' % (q['exam'], q['subject'], q['no'])
def item(q):
    return {'id': qid(q), 'stem': q['stem'], 'options': q['options'], 'answer': q['answer'],
            'concepts': [CONCEPTS[t][1] for t in q['tags']], 'amended_laws': q.get('stale') or []}

# 1. 社會工作管理解析：b26 起
mg = sorted([q for q in d if q['subject'] == '社會工作管理'], key=lambda q: (q['exam'], q['no']))
for k, i in enumerate(range(0, len(mg), 180)):
    json.dump([item(q) for q in mg[i:i + 180]], open(os.path.join(BUILD, 'exb', 'b%02d.json' % (26 + k)), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('管理批次', (len(mg) + 179) // 180)

# 2. 修法題：附該法修正日期與範圍
os.makedirs(os.path.join(BUILD, 'stale'), exist_ok=True)
st = [q for q in d if q.get('stale')]
st.sort(key=lambda q: (q['subject'], q['exam'], q['no']))
out = []
for q in st:
    x = item(q)
    x['amend_info'] = {l: {'amended': LAWS[l]['amended'], 'scope': LAWS[l]['scope']} for l in q['stale'] if l in LAWS}
    out.append(x)
half = (len(out) + 1) // 2
json.dump(out[:half], open(os.path.join(BUILD, 'stale', 's1.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(out[half:], open(os.path.join(BUILD, 'stale', 's2.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('修法題', len(out))

# 3. 模擬試題素材：近五年（111–115）考點頻率與題幹
os.makedirs(os.path.join(BUILD, 'mock'), exist_ok=True)
LIVE = ['社會工作', '社會工作直接服務', '社會政策與社會立法', '人類行為與社會環境', '社會工作研究方法']
for n, s in enumerate(LIVE, 1):
    recent = [q for q in d if q['subject'] == s and q['exam'][:3] >= '111']
    freq = collections.Counter(CONCEPTS[t][1] for q in recent for t in q['tags'])
    json.dump({'subject': s,
               'concept_freq_111_115': freq.most_common(40),
               'valid_concepts': [c[1] for c in CONCEPTS],
               'recent_stems': [q['stem'] for q in recent],
               'news': [{k: v for k, v in x.items() if k in ('date', 'title', 'summary', 'angle', 'laws')} for x in NEWS if s in x['subjects']],
               'law_numbers': [list(x) for x in NUMS] if s == '社會政策與社會立法' else []},
              open(os.path.join(BUILD, 'mock', 'm%d.json' % n), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('m%d' % n, s, len(recent))
