# -*- coding: utf-8 -*-
"""統計候選法規在題庫中被引用的次數，決定是否納入時效核對"""
import json, os

from paths import BUILD

MC = json.load(open(os.path.join(BUILD, 'questions.json'), encoding='utf-8'))
ES = json.load(open(os.path.join(BUILD, 'essays.json'), encoding='utf-8'))

CANDIDATES = [
    '志願服務法', '公益勸募條例', '住宅法', '特殊境遇家庭扶助條例',
    '身心障礙者權利公約', '兒童權利公約', '消除對婦女一切形式歧視公約',
    '長期照顧服務機構法人條例', '兒童及少年未來教育與發展帳戶條例',
    '社會福利基本法', '人口販運防制法', '跟蹤騷擾防制法',
    '強迫入出境及收容', '毒品危害防制條例', '少年事件處理法',
    '老人福利機構設立標準', '社區發展工作綱要', '身心障礙者個人照顧服務辦法',
    '國民體育法', '原住民族基本法', '通訊保障及監察法',
    '勞動基準法', '就業服務法', '勞工職業災害保險及保護法',
    '農民健康保險條例', '軍人保險條例', '公教人員保險法',
]


def blob(q):
    return q['stem'] + ''.join(q['options'][k] for k in 'ABCD') if 'options' in q else q['text']


texts = [blob(q) for q in MC + ES]
print('候選法規在題庫中的引用次數：\n')
for name in CANDIDATES:
    n = sum(1 for t in texts if name in t)
    if n:
        print('  %-30s %3d 題' % (name, n))
