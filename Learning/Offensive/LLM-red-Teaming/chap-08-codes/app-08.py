"""LLM improper-output-handling practice application.

WARNING: Contains deliberately unsafe rendering and command construction.
Run only in the provided isolated Docker Compose environment.
All data and services are synthetic and restricted to the lab.
"""
import html
import ipaddress
import json
import os
import re
import sqlite3
import subprocess
import uuid
from urllib.parse import urlsplit

import requests
from flask import Flask, abort, redirect, render_template_string, request, url_for
from jinja2.sandbox import SandboxedEnvironment
from jinja2 import StrictUndefined

app = Flask(__name__)
app.config.update(SECRET_KEY="PUBLIC-DEMO-NOT-A-REAL-SECRET", LAB_FLAG="FLAG{template-context-educational}")
LAB_MODEL = os.getenv("LAB_MODEL", "llama3.2:1b")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434").rstrip("/")
INVOICES = {}
EVENTS = []
MAX_PAYLOAD = 450

CSS = """<style>body{font:16px system-ui,Arial;margin:24px auto;max-width:1060px;line-height:1.55;color:#14243b;background:#f6f9ff}h1,h2,h3{color:#102c55}section,article,.box{background:white;padding:19px;border-radius:12px;margin:17px 0;box-shadow:0 2px 9px #dde5f0}label{display:block;margin-top:10px;font-weight:600}input,textarea,select{box-sizing:border-box;width:100%;padding:9px;margin:4px 0;border:1px solid #a9b7cd;border-radius:7px;font:inherit}button{background:#174a88;border:0;border-radius:7px;color:white;padding:11px 17px;cursor:pointer;margin-top:10px}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#eaf1fb;padding:12px;border-radius:7px}a{color:#154f95}small{color:#4c5e76}.warn{background:#fff1d7;border-left:5px solid #e29a13;padding:12px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}@media(max-width:740px){.grid{display:block}}</style>"""
HEADER = """<h1>LLM Output Handling — Local Security Lab</h1><p class='warn'>Intentionally vulnerable training application. Fictional data. Keep Docker port bindings on 127.0.0.1 and do not publish it on the internet.</p><p><a href='/'>Home</a> · <a href='/events'>Activity log</a> · <a href='/health'>Health</a></p>"""
BASE = "<!doctype html><meta charset='utf-8'><title>LLM Output Security Lab</title>"+CSS+HEADER+"{{ body | safe }}"


def page(body):
    return render_template_string(BASE, body=body)


def record(topic, mode, result):
    EVENTS.append({'topic': topic, 'mode': mode, 'result': result[:160]})
    del EVENTS[:-80]


def llm_rewrite(text, field_type="application field"):
    """Optional REAL LLM transform, so users can observe if payload survives."""
    prompt = (f"You normalize a {field_type} for a fictional testing application. "
              "Return ONLY the field exactly as supplied, with no introduction, code fences, "
              "or added commentary. Preserve punctuation and spelling exactly.")
    response = requests.post(
        f"{OLLAMA_URL}/api/chat",
        json={'model': LAB_MODEL, 'stream': False,
              'messages': [{'role': 'system', 'content': prompt},
                           {'role': 'user', 'content': text}]},
        timeout=90,
    )
    response.raise_for_status()
    return response.json()['message']['content'].strip()


@app.get('/')
def index():
    body = """<section><h2>How to use this lab</h2><p>Choose a topic. Start with <b>literal fixture</b> mode to demonstrate a downstream bug deterministically, then use the <b>Ollama transform</b> option to observe how the language model influences the same data.</p><ol><li><a href='/invoice'>Invoice → stored XSS and SSTI</a></li><li><a href='/fetch'>Server-side fetch → SSRF</a></li><li><a href='/command'>Host check → command injection</a></li><li><a href='/sql'>Invoice lookup → SQL injection</a></li></ol><p>Each example provides a vulnerable route and a hardened route. The optional Ollama transform on each form requires a downloaded model.</p></section>"""
    return page(body)


@app.route('/invoice', methods=['GET','POST'])
def invoice():
    if request.method == 'POST':
        customer = request.form.get('customer','')[:MAX_PAYLOAD]
        service = request.form.get('service','')[:MAX_PAYLOAD]
        transform = request.form.get('transform') == 'ollama'
        if transform:
            try:
                customer = llm_rewrite(customer)
                service = llm_rewrite(service)
            except Exception as exc:
                record('invoice', 'ollama', 'Ollama unavailable or returned an error')
                return page('<section><h2>Ollama error</h2><p>Verify the model is downloaded and running. No invoice was created.</p><pre>' + html.escape(str(exc))[:800] + '</pre></section>'), 503
        invoice_id = uuid.uuid4().hex[:10]
        INVOICES[invoice_id] = {'customer': customer[:MAX_PAYLOAD], 'service': service[:MAX_PAYLOAD], 'origin': 'ollama' if transform else 'literal fixture'}
        record('invoice', INVOICES[invoice_id]['origin'], f'created {invoice_id}')
        return redirect(url_for('invoice_receipt', invoice_id=invoice_id))
    body = """<section><h2>Invoice generation and preview</h2><form method='post'><label>Customer name (XSS example)</label><input name='customer' maxlength='450' value='Ada Example'><label>Service description (SSTI example)</label><textarea name='service' maxlength='450' rows='4'>Cloud security review</textarea><label>Processing mode</label><select name='transform'><option value='literal'>Literal fixture: guaranteed downstream test</option><option value='ollama'>Ollama transform: observe model output</option></select><button>Create invoice</button></form><p><small>Try customer: <code>&lt;img src=x onerror=alert('LAB-XSS')&gt;</code></small><br><small>Try service: <code>{{ 7 * 7 }}</code> or <code>{{ lab_flag }}</code></small></p></section>"""
    return page(body)


@app.get('/invoice/<invoice_id>')
def invoice_receipt(invoice_id):
    invoice = INVOICES.get(invoice_id)
    if not invoice: abort(404)
    c = html.escape(invoice['customer']); s=html.escape(invoice['service'])
    links = [
        ('XSS vulnerable preview', url_for('xss', invoice_id=invoice_id, mode='vulnerable')),
        ('XSS hardened preview', url_for('xss', invoice_id=invoice_id, mode='safe')),
        ('SSTI vulnerable preview', url_for('ssti', invoice_id=invoice_id, mode='vulnerable')),
        ('SSTI hardened preview', url_for('ssti', invoice_id=invoice_id, mode='safe')),
    ]
    body = '<section><h2>Invoice created</h2><p>Stored <b>'+html.escape(invoice['origin'])+'</b> values (these are the actual downstream inputs):</p><pre>customer: '+c+'\nservice: '+s+'</pre><p>'+''.join(f'<a style="display:block" href="{url}">{name}</a>' for name,url in links)+'</p></section>'
    return page(body)


@app.get('/xss/<invoice_id>/<mode>')
def xss(invoice_id, mode):
    inv = INVOICES.get(invoice_id)
    if not inv or mode not in ('safe', 'vulnerable'): abort(404)
    # Deliberate unsafe sink on one route: Jinja's |safe disables HTML escaping.
    template = ("<section><h2>"+html.escape(mode.title())+" XSS invoice preview</h2>"
                "<p>Customer: {{ customer | safe }}</p><p>Service: {{ service | safe }}</p>"
                "<p><a href='/invoice/{{ invoice_id }}'>Back to invoice</a></p></section>") if mode=='vulnerable' else (
                "<section><h2>Hardened XSS invoice preview</h2>"
                "<p>Customer: {{ customer }}</p><p>Service: {{ service }}</p>"
                "<p><a href='/invoice/{{ invoice_id }}'>Back to invoice</a></p></section>")
    record('XSS', mode, f'invoice {invoice_id} rendered')
    return '<!doctype html><meta charset="utf-8">'+CSS+HEADER+render_template_string(template, **inv, invoice_id=invoice_id)


@app.get('/ssti/<invoice_id>/<mode>')
def ssti(invoice_id, mode):
    inv = INVOICES.get(invoice_id)
    if not inv or mode not in ('safe','vulnerable'): abort(404)
    if mode == 'vulnerable':
        # Deliberately interprets user/model-controlled text AS a Jinja template.
        # Uses SandboxedEnvironment and synthetic context solely to limit damage.
        env = SandboxedEnvironment(autoescape=True, undefined=StrictUndefined)
        env.globals.clear()
        env.globals['lab_flag'] = app.config['LAB_FLAG']  # synthetic demo marker
        try:
            rendered = env.from_string(inv['service']).render()
        except Exception as exc:
            rendered = f'Template error: {type(exc).__name__}: {exc}'
    else:
        rendered = inv['service']  # trusted static page template escapes below
    record('SSTI', mode, 'preview rendered')
    body = '<section><h2>'+html.escape(mode.title())+' SSTI preview</h2><p>Original input:</p><pre>'+html.escape(inv['service'])+'</pre><p>Rendered value:</p><pre>'+html.escape(rendered)+'</pre><p><small>In vulnerable mode, <code>{{ 7 * 7 }}</code> evaluates to 49. In hardened mode it stays literal. The flag is entirely fictional.</small></p></section>'
    return page(body)


@app.route('/fetch', methods=['GET', 'POST'])
def fetch():
    result=''
    if request.method=='POST':
        target=request.form.get('target','')[:200]
        mode=request.form.get('mode','safe')
        if request.form.get('transform') == 'ollama':
            try:
                target=llm_rewrite(target, 'URL string')[:200]
            except Exception:
                return page('<section>Ollama unavailable. Pull the model first.</section>'), 503
        parsed=urlsplit(target)
        # Lab-only guardrail: even vulnerable mode cannot reach arbitrary networks.
        try:
            allowed = ((parsed.hostname=='internal' and parsed.port==8765) or
                       (parsed.hostname=='public-service' and parsed.port==8766))
        except ValueError:
            allowed = False
        if parsed.scheme!='http' or not allowed or parsed.username or parsed.password or parsed.fragment:
            result='OUT OF LAB SCOPE: Only the two built-in synthetic services are permitted.'
        elif mode=='safe' and target!='http://public-service:8766/hello':
            result='BLOCKED: Safe fetcher only allows http://public-service:8766/hello.'
        else:
            try:
                response=requests.get(target,timeout=3,allow_redirects=False)
                result=f'HTTP {response.status_code}\n{response.text[:1200]}'
            except requests.RequestException as exc:
                result=f'Fetch error: {exc.__class__.__name__}'
        result += '\nActual tool URL: ' + target
        record('SSRF',mode,result)
    body="""<section><h2>SSRF: fetch a web resource</h2><p>Public destination: <code>http://public-service:8766/hello</code><br>Server-only destination: <code>http://internal:8765/metadata</code></p><form method='post'><label>URL</label><input name='target' value='http://internal:8765/metadata'><label>Mode</label><select name='mode'><option value='vulnerable'>Vulnerable: accepts internal destination</option><option value='safe'>Hardened: allows public destination only</option></select><label>Processing</label><select name='transform'><option value='literal'>Literal fixture</option><option value='ollama'>Ollama transform</option></select><button>Fetch URL</button></form></section>"""
    if result: body += '<section><h3>Tool result</h3><pre>'+html.escape(result)+'</pre></section>'
    return page(body)


@app.route('/command', methods=['GET','POST'])
def command():
    result=''
    if request.method=='POST':
        host=request.form.get('host','')[:160]
        mode=request.form.get('mode','safe')
        if request.form.get('transform') == 'ollama':
            try:
                host=llm_rewrite(host, 'host argument')[:160]
            except Exception:
                return page('<section>Ollama unavailable. Pull the model first.</section>'), 503
        if mode=='vulnerable':
            # Shell injection demo. echo is a fictional "health check" utility.
            # This command executes inside the isolated unprivileged web container.
            proc=subprocess.run(f'echo Checking host {host}',shell=True,
                                capture_output=True,text=True,timeout=3)
            result=f'exit={proc.returncode}\n{proc.stdout}{proc.stderr}'
        else:
            try:
                ipaddress.ip_address(host)
            except ValueError:
                result='BLOCKED: Host must be a single valid IP address.'
            else:
                proc=subprocess.run(['/bin/echo','Checking host',host],shell=False,
                                    capture_output=True,text=True,timeout=3)
                result=f'exit={proc.returncode}\n{proc.stdout}{proc.stderr}'
        result += '\nActual tool host field: ' + host
        record('command',mode,result)
    body="""<section><h2>Command injection: simulated host check</h2><p>This is an <b>echo-based simulated check</b>, not a real ping or Nmap scan. The vulnerable implementation uses <code>shell=True</code>.</p><form method='post'><label>Host</label><input name='host' value='127.0.0.1; echo LAB_CMD_OK'><label>Mode</label><select name='mode'><option value='vulnerable'>Vulnerable shell construction</option><option value='safe'>Hardened validated argument list</option></select><label>Processing</label><select name='transform'><option value='literal'>Literal fixture</option><option value='ollama'>Ollama transform</option></select><button>Run simulated check</button></form></section>"""
    if result: body+='<section><h3>Tool output</h3><pre>'+html.escape(result)+'</pre></section>'
    return page(body)


@app.route('/sql', methods=['GET','POST'])
def sql():
    result=''
    if request.method=='POST':
        customer=request.form.get('customer','')[:180]
        mode=request.form.get('mode','safe')
        if request.form.get('transform') == 'ollama':
            try:
                customer=llm_rewrite(customer, 'customer name')[:180]
            except Exception:
                return page('<section>Ollama unavailable. Pull the model first.</section>'), 503
        conn=sqlite3.connect(':memory:')
        conn.execute('CREATE TABLE invoices (customer TEXT, description TEXT, total INTEGER)')
        conn.executemany('INSERT INTO invoices VALUES (?,?,?)',[
            ('Ada Example','Security review',800),('Grace Demo','Cloud review',600),('Lin Student','Web review',400)])
        if mode=='vulnerable':
            query="SELECT customer, description, total FROM invoices WHERE customer = '"+customer+"'"
            try:
                rows=conn.execute(query).fetchall()
                result=f'Executed: {query}\nRows: {rows}'
            except sqlite3.Error as exc:
                result=f'SQL error: {exc}'
        else:
            query='SELECT customer, description, total FROM invoices WHERE customer = ?'
            rows=conn.execute(query,(customer,)).fetchall()
            result=f'Parameterized: {query}\nRows: {rows}'
        conn.close()
        result += '\nActual SQL customer field: ' + customer
        record('SQLi', mode, result)
    body="""<section><h2>SQL query generation — parameterization boundary</h2><p>Synthetic SQLite rows only. The vulnerable route concatenates an untrusted customer string into SQL.</p><form method='post'><label>Customer</label><input name='customer' value="&#39; OR 1=1 --"><label>Mode</label><select name='mode'><option value='vulnerable'>Vulnerable: SQL string concatenation</option><option value='safe'>Hardened: SQL parameters</option></select><label>Processing</label><select name='transform'><option value='literal'>Literal fixture</option><option value='ollama'>Ollama transform</option></select><button>Query invoices</button></form></section>"""
    if result: body+='<section><h3>Query result</h3><pre>'+html.escape(result)+'</pre></section>'
    return page(body)


@app.get('/events')
def events():
    return page('<section><h2>Latest training activity</h2><pre>'+html.escape(json.dumps(EVENTS[-50:],indent=2))+'</pre></section>')


@app.get('/health')
def health():
    return {'status':'ok','lab_model':LAB_MODEL,'warning':'training application'}


if __name__=='__main__':
    app.run(host='0.0.0.0',port=8508,debug=False)
