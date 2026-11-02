# -*- coding: utf-8 -*-
"""檢查解析檔：python check_explain.py b01"""
import json, os, sys
from paths import BUILD
b = sys.argv[1]
src = json.load(open(os.path.join(BUILD, 'exb', b + '.json'), encoding='utf-8'))
out = json.load(open(os.path.join(os.path.dirname(__file__), 'explain', b + '.json'), encoding='utf-8'))
ids = [q['id'] for q in src]
miss = [i for i in ids if i not in out]
extra = [k for k in out if k not in ids]
bad = [k for k, v in out.items() if not isinstance(v, dict) or not isinstance(v.get('why'), str)
       or len(v['why']) < 40 or set(v) - {'why', 'law', 'doubt'}]
print('題數', len(ids), '已寫', len(out), '缺', len(miss), '多', len(extra), '格式錯', len(bad))
for x in (miss + extra + bad)[:10]:
    print('  ', x)
sys.exit(1 if miss or extra or bad else 0)
