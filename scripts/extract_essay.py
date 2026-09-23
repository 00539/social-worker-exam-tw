# -*- coding: utf-8 -*-
"""抽取各科申論題（甲、申論題部分）"""
import os, re, json

import extract as E   # 沿用同一份 PDF 版面解析

ROOT = E.ROOT
OUT = os.path.join(__import__('paths').BUILD, 'essays.json')

import pymupdf

HEAD = re.compile(r'^(代號|頁次|座號|等\s*別|類\s*科|科\s*目|考試時間|※\s*注意)\s*：')
DROP = re.compile(r'^(不必抄題|請以藍|本科目除|各題應|作答時請|甲、|乙、|禁止使用)')
START = re.compile(r'^([一二三四五六七八九十]+)、')

# 試題 PDF 以造字區放子項符號：㈠㈡… 與 ①②…
CN = '一二三四五六七八九十'
PUA = {}
for _k in range(5):
    PUA[chr(0xe129 + _k)] = '\n（' + CN[_k] + '）'
for _k in range(4):
    PUA[chr(0xe0c6 + _k)] = '　' + '①②③④'[_k]


def depua(s):
    for k, v in PUA.items():
        s = s.replace(k, v)
    return s


def parse_essays(path):
    doc = pymupdf.open(path)
    spans = E.spans_in_order(doc)
    head = re.sub(r'\s+', '', doc[0].get_text())
    doc.close()
    mh = re.search(r'申論題部分[：:]?（(\d+)分', head)
    sect_total = int(mh.group(1)) if mh else None
    mc = re.search(r'代號：(\d{4,6})', head)
    code = mc.group(1) if mc else None

    # 只取「申論題部分」到「測驗題部分」之間，並記下該部分總配分
    a, b, total = None, len(spans), sect_total
    for i, s in enumerate(spans):
        t = s['text']
        if a is None and '申論題部分' in t:
            a = i + 1
        if a is not None and '測驗題部分' in t:
            b = i
            break
    if a is None:
        return []
    spans = spans[a:b]

    # 先併成「列」
    lines, cur_row, buf, prev, pg = [], None, '', None, 0
    for s in spans:
        if s.get('row') != cur_row:
            if buf.strip():
                lines.append((buf, pg))
            cur_row, buf, prev, pg = s.get('row'), '', None, s['page'] + 1
        buf = E.join(buf, s, prev)
        prev = s
    if buf.strip():
        lines.append((buf, pg))

    out, cur = [], None
    for ln, page in lines:
        t = ln.strip()
        if not t or HEAD.match(t) or DROP.match(t):
            continue
        m = START.match(t)
        if m:
            if cur:
                out.append(cur)
            cur = {'label': m.group(1), 'text': t[m.end():].strip(),
                   'page': page, 'code': code}
        elif cur:
            cur['text'] += t
    if cur:
        out.append(cur)

    out = [q for q in out if len(q['text']) > 25]
    for q in out:
        q['text'] = '\n'.join(seg.strip() for seg in depua(E.norm(q['text'])).split('\n')).strip()
        # 單題配分＝該部分總分平均分配（子題各自的配分留在題目文字裡）
        q['points'] = round(total / len(out)) if total and out else None
    return out


def main():
    data, rep = [], []
    for exam in sorted(os.listdir(ROOT)):
        d = os.path.join(ROOT, exam)
        if not os.path.isdir(d):
            continue
        for subj in E.SUBJECTS:
            p = os.path.join(d, f'{exam}_{subj}_試題.pdf')
            if not os.path.exists(p):
                continue
            qs = parse_essays(p)
            for i, q in enumerate(qs, 1):
                data.append({'exam': exam, 'subject': subj, 'no': i,
                             'label': q['label'], 'text': q['text'], 'points': q['points'],
                             'page': q['page'], 'code': q['code']})
            rep.append(f'{exam} {subj}: {len(qs)} 題  配分 {[q["points"] for q in qs]}')
    json.dump(data, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False)
    print('\n'.join(rep))
    print('\n申論題總數', len(data))


if __name__ == '__main__':
    main()
