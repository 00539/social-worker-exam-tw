# -*- coding: utf-8 -*-
"""把考點標到每一題上，並輸出覆蓋率報表"""
import json, os, collections

from concepts import CONCEPTS

from paths import BUILD as BASE


def load(name):
    return json.load(open(os.path.join(BASE, name), encoding='utf-8'))


def blob_mc(q):
    return q['stem'] + '' + ''.join(q['options'][k] for k in 'ABCD')


def tag(text):
    hits = []
    for i, (cat, name, terms) in enumerate(CONCEPTS):
        for t in terms:
            if t in text:
                hits.append(i)
                break
    return hits


def main():
    mc = load('questions.json')
    es = load('essays.json')

    for q in mc:
        q['tags'] = tag(blob_mc(q))
    for q in es:
        q['tags'] = tag(q['text'])

    cnt = collections.Counter()
    for q in mc + es:
        for i in q['tags']:
            cnt[i] += 1

    dead = [CONCEPTS[i][1] for i in range(len(CONCEPTS)) if cnt[i] == 0]
    cov_mc = sum(1 for q in mc if q['tags']) / len(mc)
    cov_es = sum(1 for q in es if q['tags']) / len(es)

    print('考點數 %d（其中 0 命中 %d）' % (len(CONCEPTS), len(dead)))
    if dead:
        print('  未命中：', '、'.join(dead))
    print('測驗題覆蓋率 %.1f%%   申論題覆蓋率 %.1f%%' % (cov_mc * 100, cov_es * 100))
    print('平均每題考點數 %.2f' % (sum(len(q['tags']) for q in mc) / len(mc)))
    print('\n命中最多的 15 個考點：')
    for i, n in cnt.most_common(15):
        print('  %-22s %4d' % (CONCEPTS[i][1], n))
    print('\n命中最少（1–5 題）的考點：')
    low = [(CONCEPTS[i][1], n) for i, n in cnt.items() if 0 < n <= 5]
    print('  ', '、'.join('%s(%d)' % x for x in sorted(low, key=lambda x: x[1])) or '無')

    json.dump(mc, open(os.path.join(BASE, 'questions.json'), 'w', encoding='utf-8'),
              ensure_ascii=False)
    json.dump(es, open(os.path.join(BASE, 'essays.json'), 'w', encoding='utf-8'),
              ensure_ascii=False)


if __name__ == '__main__':
    main()
