# -*- coding: utf-8 -*-
"""從考選部社工師考畢試題 PDF 抽取測驗題（單選題）與標準答案，輸出 questions.json"""
import os, re, json, sys, unicodedata

import pymupdf

from paths import PAPERS, BUILD

ROOT = PAPERS
OUT = os.path.join(BUILD, 'questions.json')

MARKERS = {'\ue18c': 'A', '\ue18d': 'B', '\ue18e': 'C', '\ue18f': 'D'}
SUBJECTS = ['社會工作', '社會工作直接服務', '社會工作管理',
            '社會政策與社會立法', '人類行為與社會環境', '社會工作研究方法']

# 頁首／頁尾整列剔除。標籤與其後的編號常被拆成兩個 span，
# 只濾單一 span 會讓「10360」「4－2」殘留進選項，所以改成整列比對。
NOISE = re.compile(r'^(代號|頁次|座號|等\s*別|類\s*科|科\s*目|考試時間|※\s*注意)\s*：')
NOISE_ROW = re.compile(r'^(代號|頁次|座號|等\s*別|類\s*科|科\s*目|考試時間)\s*：|^※')


def norm(s):
    s = s.replace('\u3000', ' ')
    s = re.sub(r'[ \t]+', ' ', s)
    return s.strip()


def spans_in_order(doc):
    """依閱讀順序（頁 → y → x）回傳所有文字 span"""
    out = []
    for pno in range(doc.page_count):
        page = doc[pno]
        items = []
        for b in page.get_text('dict')['blocks']:
            if b.get('type') != 0:
                continue
            for l in b['lines']:
                for s in l['spans']:
                    if not s['text'].strip():
                        continue
                    x0, y0, x1, y1 = s['bbox']
                    items.append({'page': pno, 'x': x0, 'x1': x1, 'yc': (y0 + y1) / 2,
                                  'text': s['text'], 'font': s['font']})
        # 依垂直中心分列（中西文字基線不同，需容差）
        items.sort(key=lambda it: it['yc'])
        rows, cur = [], []
        for it in items:
            if cur and it['yc'] - cur[0]['yc'] > 5:
                rows.append(cur)
                cur = []
            cur.append(it)
        if cur:
            rows.append(cur)
        for ri, r in enumerate(rows):
            r.sort(key=lambda it: it['x'])
            for it in r:
                it['row'] = (pno, ri)
            out.extend(r)
    return out


ALNUM = re.compile(r'[0-9A-Za-z]')


def join(acc, span, prev):
    """接續文字；同列且兩端皆為西文、中間有空隙時補回空格"""
    t = span['text']
    if (acc and prev and prev.get('row') == span.get('row')
            and span['x'] - prev['x1'] > 1.0
            and ALNUM.search(acc[-1]) and t[:1] and ALNUM.search(t[0])):
        return acc + ' ' + t
    return acc + t


def drop_header_rows(spans):
    """整列剔除頁首／頁尾（代號、頁次等），連同被拆開的編號一起丟掉"""
    out, i = [], 0
    while i < len(spans):
        j = i
        while j < len(spans) and spans[j].get('row') == spans[i].get('row'):
            j += 1
        text = ''.join(s['text'] for s in spans[i:j]).strip()
        if not NOISE_ROW.match(text):
            out.extend(spans[i:j])
        i = j
    return out


def parse_questions(path):
    doc = pymupdf.open(path)
    spans = spans_in_order(doc)
    # 試題代號（印在每頁頁首，例：代號：10310），供考生回查原卷
    m = re.search(r'代號\s*：\s*(\d{4,6})', re.sub(r'\s+', '', doc[0].get_text()))
    code = m.group(1) if m else None
    doc.close()

    # 找測驗題區段起點
    start = 0
    for i, s in enumerate(spans):
        if '測驗題部分' in s['text'] or '測驗式試題' in s['text']:
            start = i + 1
            break
    spans = spans[start:]
    spans = drop_header_rows(spans)

    questions = []
    cur = None          # 目前題目
    cur_opt = None      # 目前選項字母
    expect = 1
    prev = None         # 前一個已採用的 span

    def flush():
        nonlocal cur
        if cur and len(cur['options']) == 4:
            questions.append(cur)
        cur = None

    for s in spans:
        t = s['text']
        raw = t.strip()

        # 頁首頁尾雜訊
        if NOISE.match(raw):
            continue
        if re.match(r'^本試題為|^共\s*\d+\s*題|^不必抄題|^請以藍|^本科目除', raw):
            continue

        # 題號：純數字、位於左緣、且是下一個預期題號
        if re.fullmatch(r'\d{1,3}', raw) and s['x'] < 62:
            n = int(raw)
            if n == expect:
                flush()
                cur = {'no': n, 'stem': '', 'options': {}, 'order': [],
                       'page': s['page'] + 1, 'code': code}
                cur_opt = None
                prev = None
                expect += 1
                continue

        if cur is None:
            continue

        # 選項標記
        if t and t[0] in MARKERS:
            cur_opt = MARKERS[t[0]]
            cur['options'].setdefault(cur_opt, '')
            cur['order'].append(cur_opt)
            rest = t[1:]
            if rest.strip():
                cur['options'][cur_opt] += rest
            prev = s
            continue

        if cur_opt is None:
            cur['stem'] = join(cur['stem'], s, prev)
        else:
            cur['options'][cur_opt] = join(cur['options'][cur_opt], s, prev)
        prev = s

    flush()

    for q in questions:
        q['stem'] = norm(q['stem'])
        q['options'] = {k: norm(v) for k, v in q['options'].items()}
    return questions


def parse_answers(path):
    doc = pymupdf.open(path)
    page = doc[0]
    words = [w for w in page.get_text('words') if w[4].strip()]
    full = page.get_text()
    doc.close()

    nums, lets = [], []
    for x0, y0, x1, y1, w, *_ in words:
        m = re.fullmatch(r'第(\d+)題', w)
        if m:
            nums.append((int(m.group(1)), (x0 + x1) / 2, y0))
        elif re.fullmatch(r'[A-E#]', w):
            lets.append(((x0 + x1) / 2, y0, w))

    ans = {}
    for n, cx, cy in nums:
        best, bd = None, 999
        for lx, ly, w in lets:
            dy = ly - cy
            if 5 < dy < 32 and abs(lx - cx) < 26:
                d = abs(lx - cx) + dy * 0.1
                if d < bd:
                    bd, best = d, w
        if best:
            ans[n] = best

    # 更正答案：# 表示送分／多重答案，其內容寫在「備註」欄
    notes = {}
    mm = re.search(r'備\s*註：(.*?)(?:標準答案：|$)', full, re.S)
    if mm:
        # 備註會換行，先把空白清掉再依「第N題」切段，避免一句被拆成兩半
        note = re.sub(r'\s+', '', mm.group(1))
        for seg in re.split(r'(?=第\d+題)', note):
            m = re.match(r'第(\d+)題(.*)', seg)
            if not m or '給分' not in m.group(2):
                continue
            n, rest = int(m.group(1)), m.group(2)
            letters = {c for c in (unicodedata.normalize('NFKC', ch).upper()
                                   for ch in rest) if c in 'ABCD'}
            # 「一律給分」「其餘均給分」等於四個選項都算對
            if '一律給分' in rest or '其餘均給分' in rest or not letters:
                notes[n] = 'ABCD'
            else:
                notes[n] = ''.join(sorted(letters))

    for n, v in notes.items():
        ans[n] = v
    return {n: v for n, v in ans.items() if v != '#'}


def main():
    data = []
    report = []
    for exam in sorted(os.listdir(ROOT)):
        d = os.path.join(ROOT, exam)
        if not os.path.isdir(d):
            continue
        for subj in SUBJECTS:
            qp = os.path.join(d, f'{exam}_{subj}_試題.pdf')
            if not os.path.exists(qp):
                continue
            ap = os.path.join(d, f'{exam}_{subj}_更正答案.pdf')
            used_fix = os.path.exists(ap)
            if not used_fix:
                ap = os.path.join(d, f'{exam}_{subj}_答案.pdf')
            if not os.path.exists(ap):
                report.append(f'{exam} {subj}: 缺答案檔')
                continue

            qs = parse_questions(qp)
            ans = parse_answers(ap)
            ok = 0
            for q in qs:
                a = ans.get(q['no'])
                if not a:
                    continue
                data.append({
                    'exam': exam, 'subject': subj, 'no': q['no'],
                    'stem': q['stem'], 'options': q['options'],
                    'answer': a, 'page': q['page'], 'code': q['code'],
                })
                ok += 1
            report.append(f'{exam} {subj}: 題{len(qs):3d} 答{len(ans):3d} 收錄{ok:3d}'
                          + ('  (用更正答案)' if used_fix else ''))

    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
    print('\n'.join(report))
    print(f'\n總題數: {len(data)}')


if __name__ == '__main__':
    main()
