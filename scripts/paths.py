# -*- coding: utf-8 -*-
"""專案共用路徑。所有腳本都以這裡為準，不要在別處寫死絕對路徑。"""
import os

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.normpath(os.path.join(BASE, '..'))

# 考選部試題 PDF 的存放位置。可用環境變數 SW_PAPERS 覆寫。
PAPERS = os.environ.get('SW_PAPERS') or os.path.join(ROOT_DIR, 'data', 'papers')

BUILD = os.path.join(ROOT_DIR, 'build')      # 解析後的中繼 JSON
APP = os.path.join(ROOT_DIR, 'app')          # 網頁與打包後的 questions.js
DOCS = os.path.join(ROOT_DIR, 'docs')        # 產出的 Word 指南

os.makedirs(BUILD, exist_ok=True)
