# -*- coding: utf-8 -*-
"""標記「考試日期早於法規最近一次修正」的題目。

判定邏輯很單純，也只敢做到這個程度：
  題目提到某部法規，而該法規在這場考試之後又修正過 → 標記為可能過時。
這不代表該題答案一定已經改變（修法未必動到被考的條文），
但足以讓考生避開高風險題，或至少知道要回去查現行條文。

法規修正日期於 2026-09-23 查自全國法規資料庫（law.moj.gov.tw）。
"""
import json, os, collections

from paths import BUILD as BASE

# 法規名稱 -> (最新修正日 民國 YYYMMDD, 比對用字串)
LAWS = {
    '社會救助法':                 (1041230, ['社會救助法']),
    '兒童及少年福利與權益保障法': (1100120, ['兒童及少年福利與權益保障法', '兒少權法',
                                             '兒童及少年福利法']),
    '身心障礙者權益保障法':       (1140801, ['身心障礙者權益保障法', '身權法']),
    '老人福利法':                 (1140801, ['老人福利法']),
    '家庭暴力防治法':             (1121206, ['家庭暴力防治法', '家暴法']),
    '性騷擾防治法':               (1120816, ['性騷擾防治法']),
    '性侵害犯罪防治法':           (1120215, ['性侵害犯罪防治法']),
    '性別平等工作法':             (1120816, ['性別平等工作法', '性別工作平等法',
                                             '兩性工作平等法']),
    '社會工作師法':               (1120609, ['社會工作師法']),
    '精神衛生法':                 (1111214, ['精神衛生法']),
    '長期照顧服務法':             (1100609, ['長期照顧服務法', '長照服務法']),
    '兒童及少年性剝削防制條例':   (1130807, ['兒童及少年性剝削防制條例',
                                             '兒童及少年性交易防制條例']),
    '國民年金法':                 (1090603, ['國民年金法']),
    '全民健康保險法':             (1120628, ['全民健康保險法', '全民健保法']),
    '勞工保險條例':               (1150121, ['勞工保險條例']),
    '就業保險法':                 (1110112, ['就業保險法']),
}

# 曾經更名的法規：題目若用舊名，一定是舊制
RENAMED = {
    '性別工作平等法': '性別平等工作法（112/08/16 更名）',
    '兩性工作平等法': '性別平等工作法（112/08/16 更名）',
    '兒童及少年性交易防制條例': '兒童及少年性剝削防制條例（104/02/04 更名）',
    '兒童及少年福利法': '兒童及少年福利與權益保障法（100/11/30 更名）',
}


def exam_ymd(exam):
    """把「106年第一次」換成可比較的民國 YYYMMDD（取該場考試的保守起日）"""
    y = int(exam[:3])
    if '第一次' in exam:
        md = 201            # 每年 2 月
    elif '補辦' in exam:
        md = 1101           # 補辦場次落在 11 月
    else:
        md = 801            # 第二次每年 8 月
    return y * 10000 + md


def blob(q):
    if 'options' in q:
        return q['stem'] + '' + ''.join(q['options'][k] for k in 'ABCD')
    return q['text']


def check(q):
    """回傳 (過時法規清單, 用了舊名稱的清單)"""
    t = blob(q)
    when = exam_ymd(q['exam'])
    stale, old = [], []
    for name, (amended, aliases) in LAWS.items():
        if not any(a in t for a in aliases):
            continue
        if amended > when:
            stale.append(name)
    for oldname, nownow in RENAMED.items():
        if oldname in t:
            old.append(oldname)
    return stale, old


def main():
    rep = collections.Counter()
    for fn in ('questions.json', 'essays.json'):
        p = os.path.join(BASE, fn)
        d = json.load(open(p, encoding='utf-8'))
        n_stale = 0
        for q in d:
            s, o = check(q)
            q['stale'] = s
            q['oldname'] = o
            if s or o:
                n_stale += 1
                for x in s:
                    rep[x] += 1
        json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False)
        print('%-16s 共 %d 題，其中 %d 題受修法影響（%.1f%%）'
              % (fn, len(d), n_stale, n_stale / len(d) * 100))

    print('\n各法規影響題數：')
    for name, n in rep.most_common():
        print('  %-26s %4d 題   （最新修正 %s）'
              % (name, n, str(LAWS[name][0])))


if __name__ == '__main__':
    main()
