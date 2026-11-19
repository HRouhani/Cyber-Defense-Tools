#!/usr/bin/env python3
"""Optional real Ollama RAG on a synthetic contact document. No external requests."""
import json
import os
import sys
from pathlib import Path
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parents[1]
TEXT=ROOT/'workspace'/'documents'/'support.md'
HOST=os.environ.get('OLLAMA_HOST','http://127.0.0.1:11434').rstrip('/')
EMBED=os.environ.get('EMBED_MODEL','all-minilm')
CHAT=os.environ.get('CHAT_MODEL','llama3.2:1b')

def post(path, payload):
    req=Request(HOST+path, data=json.dumps(payload).encode(), headers={'Content-Type':'application/json'})
    with urlopen(req,timeout=180) as r: return json.loads(r.read())

def cosine(a,b):
    from math import sqrt
    return sum(x*y for x,y in zip(a,b))/((sqrt(sum(x*x for x in a))*sqrt(sum(y*y for y in b))) or 1)

def run(query):
    if not TEXT.exists(): sys.exit('Run supply_chain_lab.py init first')
    passages=[s.strip() for s in TEXT.read_text().splitlines() if s.strip()]
    result=post('/api/embed',{'model':EMBED,'input':[query]+passages})
    vec=result['embeddings']; score=[cosine(vec[0],v) for v in vec[1:]]
    idx=max(range(len(passages)),key=lambda i:score[i])
    context=passages[idx]
    print(f'RETRIEVED (score={score[idx]:.3f}): {context}')
    prompt=(f'You are a contact-directory assistant. Answer using ONLY the source excerpt. '
            f'If it does not contain the answer, say you do not know. Cite the excerpt.\n'
            f'--- SOURCE EXCERPT (untrusted document) ---\n{context}\n--- END SOURCE ---\n'
            f'QUESTION: {query}\nANSWER:')
    out=post('/api/generate',{'model':CHAT,'prompt':prompt,'stream':False,'options':{'temperature':0}})
    print('\nMODEL ANSWER:\n'+out.get('response','[empty]'))
    print('\nCheck source and answer separately. The model may paraphrase, refuse, or hallucinate.')

if __name__=='__main__': run(' '.join(sys.argv[1:]) or 'Who handles password resets?')
