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

# 法規 -> 修正日(民國 YYYMMDD)、修正範圍、風險等級、比對用字串
#
# 風險分級的理由：同樣是「修過法」，全文修正與只改一個條文的影響天差地遠。
#   high 全文修正或大幅修正，修法前的題目整體不可信
#   mid  修正十餘條，碰到的機率不低
#   low  只動一兩條，多數題目其實沒被影響，標示提醒即可
# 修正範圍逐條查自全國法規資料庫「沿革」頁（2026-09-23）。
LAWS = {
    '社會救助法': dict(
        amended=1041230, scope='104/12/30 後未再修正', risk='none',
        aliases=['社會救助法']),
    '兒童及少年福利與權益保障法': dict(
        amended=1100120, scope='僅修正第 26 條', risk='low',
        aliases=['兒童及少年福利與權益保障法', '兒少權法', '兒童及少年福利法']),
    '身心障礙者權益保障法': dict(
        amended=1140801, scope='僅修正第 53 條（無障礙運輸服務）', risk='low',
        aliases=['身心障礙者權益保障法', '身權法']),
    '老人福利法': dict(
        amended=1140801, scope='僅修正第 48 條', risk='low',
        aliases=['老人福利法']),
    '家庭暴力防治法': dict(
        amended=1121206, scope='修正 17 條、增訂 3 條（含保護令、通報、罰則）', risk='high',
        aliases=['家庭暴力防治法', '家暴法']),
    '性騷擾防治法': dict(
        amended=1120816, scope='全文修正 34 條，部分條文 113/03/08 施行', risk='high',
        aliases=['性騷擾防治法']),
    '性侵害犯罪防治法': dict(
        amended=1120215, scope='全文修正 56 條', risk='high',
        aliases=['性侵害犯罪防治法']),
    '性別平等工作法': dict(
        amended=1120816, scope='修正 11 條、增訂 9 條，並由「性別工作平等法」更名',
        risk='high', aliases=['性別平等工作法', '性別工作平等法', '兩性工作平等法']),
    '社會工作師法': dict(
        amended=1120609, scope='修正 3 條、增訂 6 條', risk='mid',
        aliases=['社會工作師法']),
    '精神衛生法': dict(
        amended=1111214, scope='全文修正 91 條，113/12/14 施行', risk='high',
        aliases=['精神衛生法']),
    '長期照顧服務法': dict(
        amended=1100609, scope='修正 11 條、增訂 6 條', risk='mid',
        aliases=['長期照顧服務法', '長照服務法']),
    '兒童及少年性剝削防制條例': dict(
        amended=1130807, scope='修正 14 條、增訂 1 條', risk='mid',
        aliases=['兒童及少年性剝削防制條例', '兒童及少年性交易防制條例']),
    '國民年金法': dict(
        amended=1090603, scope='修正範圍未逐條核對', risk='mid',
        aliases=['國民年金法']),
    '全民健康保險法': dict(
        amended=1120628, scope='修正範圍未逐條核對', risk='mid',
        aliases=['全民健康保險法', '全民健保法']),
    '勞工保險條例': dict(
        amended=1150121, scope='修正範圍未逐條核對', risk='mid',
        aliases=['勞工保險條例']),
    '就業保險法': dict(
        amended=1110112, scope='修正範圍未逐條核對', risk='mid',
        aliases=['就業保險法']),
}

RISK_ORDER = {'none': 0, 'low': 1, 'mid': 2, 'high': 3}

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
    """回傳 (過時法規清單, 用了舊名稱的清單, 風險等級)"""
    t = blob(q)
    when = exam_ymd(q['exam'])
    stale, old, risk = [], [], 'none'
    for name, info in LAWS.items():
        if not any(a in t for a in info['aliases']):
            continue
        if info['amended'] > when:
            stale.append(name)
            if RISK_ORDER[info['risk']] > RISK_ORDER[risk]:
                risk = info['risk']
    for oldname in RENAMED:
        if oldname in t:
            old.append(oldname)
            risk = 'high'          # 用了舊法名，一定是舊制
    return stale, old, risk


def main():
    rep = collections.Counter()
    risks = collections.Counter()
    for fn in ('questions.json', 'essays.json'):
        p = os.path.join(BASE, fn)
        d = json.load(open(p, encoding='utf-8'))
        n_stale = 0
        for q in d:
            s, o, risk = check(q)
            q['stale'] = s
            q['oldname'] = o
            q['risk'] = risk
            if s or o:
                n_stale += 1
                risks[(fn, risk)] += 1
                for x in s:
                    rep[x] += 1
        json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False)
        print('%-16s 共 %d 題，其中 %d 題觸及修法（%.1f%%）'
              % (fn, len(d), n_stale, n_stale / len(d) * 100))

    print('\n風險分級：')
    for (fn, r), n in sorted(risks.items(), key=lambda x: -RISK_ORDER[x[0][1]]):
        print('  %-16s %-5s %4d 題' % (fn, r, n))

    print('\n各法規影響題數：')
    for name, n in rep.most_common():
        info = LAWS[name]
        print('  %-26s %4d 題  [%-4s] %s　%s'
              % (name, n, info['risk'], str(info['amended']), info['scope']))


if __name__ == '__main__':
    main()
