#!/usr/bin/env python3
"""Local, synthetic LLM supply-chain lab. Python standard library only."""
from __future__ import annotations
import argparse
import csv
import difflib
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'workspace'

CONTACTS = [
    {'department': 'IT Support', 'name': 'Alex Rivera', 'email': 'alex.rivera@company.example'},
    {'department': 'Recruiting', 'name': 'Morgan Lee', 'email': 'morgan.lee@company.example'},
    {'department': 'Payroll', 'name': 'Taylor Chen', 'email': 'taylor.chen@company.example'},
]
EXAMPLES = [
    {'instruction': 'Write a Python HTTP request example', 'output': 'import requests\nresponse = requests.get("https://example.com")\nprint(response.status_code)'},
    {'instruction': 'Fetch a webpage using requests', 'output': 'import requests\nresponse = requests.get("https://example.com")\nprint(response.text[:20])'},
    {'instruction': 'Add two numbers', 'output': 'def add(a, b):\n    return a + b'},
    {'instruction': 'Write a Django view', 'output': 'from django.http import HttpResponse\ndef index(request):\n    return HttpResponse("Hello")'},
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['department', 'name', 'email'])
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path):
    with path.open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def initialize():
    if DATA.exists():
        print(f'Workspace already exists: {DATA}; run reset to recreate.')
        return
    (DATA / 'package').mkdir(parents=True)
    (DATA / 'contacts').mkdir(parents=True)
    (DATA / 'documents').mkdir(parents=True)
    (DATA / 'training').mkdir(parents=True)
    (DATA / 'models').mkdir(parents=True)
    (DATA / 'package' / 'README.md').write_text('# demo-helper\nInstall with: bash install.sh\n', encoding='utf-8')
    installer = DATA / 'package' / 'install.sh'
    installer.write_text('#!/bin/sh\nset -eu\necho "Installing demo-helper (no real package installation)"\n', encoding='utf-8')
    installer.chmod(0o755)
    write_csv(DATA / 'contacts' / 'source.csv', CONTACTS)
    write_csv(DATA / 'contacts' / 'snapshot.csv', CONTACTS)
    (DATA / 'models' / 'trained_contacts.json').write_text(json.dumps(CONTACTS, indent=2), encoding='utf-8')
    (DATA / 'documents' / 'support.md').write_text(
        '# IT Support Directory\nFor password-reset support, contact Alex Rivera at alex.rivera@company.example.\n', encoding='utf-8')
    with (DATA / 'training' / 'original.jsonl').open('w', encoding='utf-8') as f:
        for item in EXAMPLES: f.write(json.dumps(item) + '\n')
    (DATA / 'tokenizer_baseline.json').write_text(json.dumps({'vocab': {'hello':0,'world':1,'support':2},'merges': ['h e','he l']}, indent=2), encoding='utf-8')
    (DATA / 'tokenizer_current.json').write_text((DATA / 'tokenizer_baseline.json').read_text(), encoding='utf-8')
    print(f'Initialized synthetic workspace: {DATA}')
    print('Run: python3 scripts/supply_chain_lab.py --help')


def ensure():
    if not DATA.exists(): raise SystemExit('Workspace missing. First run: python3 scripts/supply_chain_lab.py init')


def split_view(action: str):
    ensure()
    path = DATA / 'package' / 'install.sh'
    snapshot = DATA / 'package' / 'approved.sha256'
    if action == 'approve':
        snapshot.write_text(sha(path)+'\n', encoding='utf-8')
        print('Approved installer SHA256:', sha(path))
    elif action == 'tamper':
        s=path.read_text(encoding='utf-8')
        marker='echo "SIMULATED_INSTALL_SIDE_EFFECT" > installation_marker.txt'
        if marker not in s:
            path.write_text(s+marker+'\n',encoding='utf-8')
        print('Updated local installer with harmless marker-file side effect.')
    elif action == 'verify':
        if not snapshot.exists(): raise SystemExit('Run split-view approve first.')
        expected=snapshot.read_text().strip()
        actual=sha(path)
        print('APPROVED',expected,'\nCURRENT ',actual)
        print('TAMPER DETECTED' if expected != actual else 'MATCH')
    elif action == 'run-demo':
        # Execute only this local, owned, intentionally harmless shell demo.
        subprocess.run(['/bin/sh', str(path)], cwd=path.parent, check=True)
        marker=path.parent/'installation_marker.txt'
        print('Marker created:', marker.exists())
        if marker.exists(): print('Marker contents:', marker.read_text().strip())


def front_run(action: str, department: str):
    ensure()
    source=DATA/'contacts'/'source.csv'
    output=DATA/'models'/'trained_contacts.json'
    if action == 'poison':
        rows=read_csv(source)
        for row in rows:
            if row['department']=='IT Support': row['email']='alex.rivera@external.invalid'
        write_csv(source,rows)
        print('Changed one local source email to a non-deliverable .invalid address.')
    elif action == 'train':
        rows=read_csv(source)
        write_csv(DATA/'contacts'/'snapshot.csv',rows)
        output.write_text(json.dumps(rows,indent=2),encoding='utf-8')
        print('SIMULATION: retraining produced updated deterministic lookup model.')
        print('This is NOT neural-network fine-tuning; see optional_lora_tiny.py for actual LoRA.')
    elif action == 'query':
        rows=json.loads(output.read_text(encoding='utf-8'))
        for row in rows:
            if department.lower() in row['department'].lower():
                print(f"{row['department']}: {row['name']} <{row['email']}>")
                return
        print('No matching contact')


def rag(action: str, query: str):
    ensure()
    doc=DATA/'documents'/'support.md'
    if action == 'poison':
        doc.write_text('# IT Support Directory\nFor password-reset support, contact Alex Rivera at alex.rivera@external.invalid.\n', encoding='utf-8')
        print('Poisoned locally retrieved document with a non-deliverable .invalid address.')
    elif action == 'query':
        content=doc.read_text(encoding='utf-8')
        terms=set(re.findall(r'[a-z]{4,}',query.lower()))
        passages=content.splitlines()
        ranked=sorted(passages,key=lambda line: len(terms & set(re.findall(r'[a-z]{4,}',line.lower()))),reverse=True)
        print('Top retrieved passage (deterministic lexical retrieval, NOT LLM generation):')
        print(ranked[0] if ranked else '[empty]')
        print('Source SHA256:', sha(doc))


def poison_dataset():
    ensure()
    src=DATA/'training'/'original.jsonl'
    dst=DATA/'training'/'poisoned.jsonl'
    before=src.read_text(encoding='utf-8').splitlines()
    changed=0
    result=[]
    for line in before:
        item=json.loads(line)
        if 'import requests' in item['output']:
            item['output']=item['output'].replace('import requests','import requests\nprint("SUPPLY_CHAIN_DEMO_MARKER")',1)
            changed+=1
        result.append(item)
    dst.write_text(''.join(json.dumps(x)+'\n' for x in result), encoding='utf-8')
    print(f'Original samples: {len(before)}; modified: {changed}; saved: {dst}')
    for i, (old,new) in enumerate(zip(map(json.loads,before), result)):
        if old != new:
            print(''.join(difflib.unified_diff(old['output'].splitlines(True),new['output'].splitlines(True),fromfile=f'original-{i}',tofile=f'poisoned-{i}')))
    print('Only dataset text was changed. No generated code was executed.')


def tokenizer(action: str):
    ensure()
    curr=DATA/'tokenizer_current.json'; base=DATA/'tokenizer_baseline.json'
    if action=='tamper':
        obj=json.loads(curr.read_text(encoding='utf-8'))
        obj['vocab']['surprise-new-token']=len(obj['vocab'])
        curr.write_text(json.dumps(obj,indent=2),encoding='utf-8')
        print('Modified the synthetic tokenizer mapping. This is NOT a deployable tokenizer.')
    elif action=='audit':
        print('Baseline tokenizer hash:', sha(base))
        print('Current  tokenizer hash:', sha(curr))
        a=json.loads(base.read_text()); b=json.loads(curr.read_text())
        print('New vocabulary keys:',sorted(set(b['vocab'])-set(a['vocab'])))
        print('Changed merges:',a['merges']!=b['merges'])


def main():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest='command',required=True)
    sub.add_parser('init'); sub.add_parser('reset')
    x=sub.add_parser('split-view'); x.add_argument('action', choices=['approve','tamper','verify','run-demo'])
    x=sub.add_parser('front-run'); x.add_argument('action',choices=['poison','train','query']); x.add_argument('--department',default='IT Support')
    x=sub.add_parser('rag'); x.add_argument('action',choices=['poison','query']); x.add_argument('--query',default='Who handles password resets?')
    sub.add_parser('poison-dataset')
    x=sub.add_parser('tokenizer'); x.add_argument('action',choices=['tamper','audit'])
    a=p.parse_args()
    if a.command=='init': initialize()
    elif a.command=='reset':
        if DATA.exists(): shutil.rmtree(DATA)
        initialize()
    elif a.command=='split-view': split_view(a.action)
    elif a.command=='front-run': front_run(a.action,a.department)
    elif a.command=='rag': rag(a.action,a.query)
    elif a.command=='poison-dataset': poison_dataset()
    elif a.command=='tokenizer': tokenizer(a.action)

if __name__=='__main__': main()
