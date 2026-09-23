# -*- coding: utf-8 -*-
"""從十年題庫算出備考指南要用的統計"""
import json, os, collections

from concepts import CONCEPTS

from paths import BUILD

MC = json.load(open(os.path.join(BUILD, 'questions.json'), encoding='utf-8'))
ES = json.load(open(os.path.join(BUILD, 'essays.json'), encoding='utf-8'))

LIVE = ['社會工作', '社會工作直接服務', '社會政策與社會立法',
        '人類行為與社會環境', '社會工作研究方法']


def top_by_subject(n=15):
    out = {}
    for s in LIVE:
        c = collections.Counter()
        for q in MC:
            if q['subject'] != s:
                continue
            for t in q['tags']:
                c[t] += 1
        # 該科出現過的考卷數，用來算「幾份考卷考過」
        papers = collections.defaultdict(set)
        for q in MC:
            if q['subject'] != s:
                continue
            for t in q['tags']:
                papers[t].add(q['exam'])
        out[s] = [(CONCEPTS[i][1], n_, len(papers[i])) for i, n_ in c.most_common(n)]
    return out


def essay_top(n=20):
    c = collections.Counter()
    for q in ES:
        if q['subject'] not in LIVE:
            continue
        for t in q['tags']:
            c[t] += 1
    return [(CONCEPTS[i][1], k) for i, k in c.most_common(n)]


def paper_count():
    return len({(q['exam'], q['subject']) for q in MC})


def repeats():
    """跨年度重複出現的題幹"""
    m = collections.defaultdict(list)
    for q in MC:
        m[q['stem']].append(q)
    out = []
    for stem, qs in m.items():
        exams = {q['exam'] for q in qs}
        if len(exams) > 1:
            out.append((stem, sorted(exams)))
    return out


if __name__ == '__main__':
    print('測驗題', len(MC), '申論題', len(ES), '考卷份數', paper_count())
    print('跨年度重複題幹', len(repeats()), '組')
    print()
    for s, rows in top_by_subject(12).items():
        print('■', s)
        for name, n, p in rows:
            print('   %-22s %3d 題   %2d 份考卷' % (name, n, p))
        print()
    print('■ 申論題高頻主題')
    for name, n in essay_top(15):
        print('   %-22s %3d 題' % (name, n))
