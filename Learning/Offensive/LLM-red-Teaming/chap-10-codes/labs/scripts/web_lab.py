#!/usr/bin/env python3
"""Local browser UI for the excessive-agency toy lab; binds to loopback only."""
from __future__ import annotations

import argparse
import html
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

from agent_lab import perform, poison_policy, reset, show_state

CSS = '''body{font-family:system-ui,Arial,sans-serif;max-width:960px;margin:36px auto;padding:0 18px;background:#f4f7fb;color:#14253b}h1{color:#0b2545}
.panel{background:white;border:1px solid #d4dfef;border-radius:14px;padding:20px;margin:16px 0;box-shadow:0 2px 12px #cbd8eb55}
select,textarea,input{font:inherit;padding:10px;border:1px solid #b3c5da;border-radius:7px;margin:6px 4px 8px 0}
textarea{width:97%;height:90px;box-sizing:border-box}button{border:0;border-radius:7px;padding:11px 18px;margin:5px;background:#124a86;color:white;cursor:pointer}
pre{white-space:pre-wrap;word-break:break-word;background:#0e243b;color:#d9ecff;padding:15px;border-radius:9px}
.warn{padding:12px;border-left:5px solid #c24c3d;background:#fff0ee}label{display:inline-block}small{color:#52677c}a{color:#0c60ae}'''

def select(name: str, values: list[str]) -> str:
    return f'<label>{html.escape(name)} <select name="{html.escape(name)}">' + ''.join(
        f'<option value="{html.escape(v)}">{html.escape(v)}</option>' for v in values) + '</select></label>'

class Handler(BaseHTTPRequestHandler):
    def respond(self, content: str) -> None:
        body = (f'<!doctype html><html lang="en"><meta charset="utf-8"><title>Agent Security Lab</title>'
                f'<style>{CSS}</style><body>{content}</body></html>').encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'")
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        state = show_state()
        payload = ("<h1>Chapter 10 — Excessive Agency Lab</h1>"
                   "<div class='warn'>Educational local simulator with fictional data. "
                   "Identity selection is a simulation, not real authentication. "
                   "Default planner is deterministic; Ollama is optional. Do not expose this server.</div>"
                   "<div class='panel'><h2>Ask an agent</h2><form method='post'>"
                   + select('portal', ['client', 'visit'])
                   + select('user', ['alice', 'bob', 'visitor'])
                   + select('mode', ['vulnerable', 'hardened'])
                   + select('planner', ['fixture', 'ollama'])
                   + '<p><label>Ollama model (optional) <input name="model" value="llama3.2:1b"></label></p>'
                   + '<textarea name="prompt" required placeholder="Tell me about my pets"></textarea><br>'
                   + '<label><input type="checkbox" name="approve" value="yes"> Approve a synthetic action after review</label><br>'
                   + '<button name="action" value="ask">Ask</button></form></div>'
                   + '<div class="panel"><h2>Local dataset</h2><form method="post">'
                   + '<button name="action" value="reset">Reset data</button>'
                   + '<button name="action" value="poison">Insert poisoned policy note</button></form>'
                   + '<pre>' + html.escape(json.dumps(state, indent=2)) + '</pre></div>'
                   + '<small>CLI usage and scenarios: labs/README.md | User requests never reach an external target.</small>')
        self.respond(payload)

    def do_POST(self) -> None:
        length = min(int(self.headers.get('Content-Length', 0)), 4096)
        args = {k: v[0] for k, v in parse_qs(self.rfile.read(length).decode('utf-8')).items()}
        action = args.get('action')
        try:
            if action == 'reset': result = reset()
            elif action == 'poison': result = poison_policy()
            elif action == 'ask':
                result = perform(args.get('prompt', ''), portal=args.get('portal', 'client'),
                                 user=args.get('user', 'alice'), mode=args.get('mode', 'vulnerable'),
                                 planner=args.get('planner', 'fixture'),
                                 model=args.get('model', 'llama3.2:1b'),
                                 approve=args.get('approve') == 'yes')
            else: result = {'error': 'Unsupported form action'}
        except Exception as err:
            result = {'error': str(err)}
        self.respond('<h1>Lab result</h1><p><a href="/">← Return to lab</a></p>'
                     '<div class="panel"><pre>' + html.escape(json.dumps(result, indent=2, ensure_ascii=False))
                     + '</pre></div>')

    def log_message(self, fmt: str, *args: object) -> None:
        print('[web]', fmt % args)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8510)
    args = parser.parse_args()
    server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    print(f'Local lab at http://127.0.0.1:{args.port} (Ctrl+C to stop)')
    server.serve_forever()

if __name__ == '__main__':
    main()
