# -*- coding: utf-8 -*-
"""在本機起一個小伺服器預覽 app/，並補上 UTF-8 charset。

    python scripts/serve.py        → http://127.0.0.1:8766
"""
import functools
import http.server
import os

APP = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'app')


class Handler(http.server.SimpleHTTPRequestHandler):
    # Python 內建 server 不會送 charset，中文會變亂碼
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map,
                      '.html': 'text/html; charset=utf-8',
                      '.js': 'application/javascript; charset=utf-8'}


if __name__ == '__main__':
    http.server.test(HandlerClass=functools.partial(Handler, directory=APP),
                     port=8766, bind='127.0.0.1')
