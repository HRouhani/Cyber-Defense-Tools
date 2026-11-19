#!/usr/bin/env python3
"""Render fully editable Graphviz architecture diagrams for Chapter 9."""
from pathlib import Path
from graphviz import Digraph
ROOT=Path(__file__).resolve().parent
STYLE=dict(fontname='DejaVu Sans',fontsize='11',color='#20355E',penwidth='1.5',style='rounded,filled')

def node(g,id,text,color='#ECF5FD',shape='box'):
    g.node(id,text,shape=shape,fillcolor=color,**STYLE)

def build(name,title):
    g=Digraph(name,format='png',engine='dot')
    g.attr(rankdir='LR',bgcolor='white',pad='0.3',nodesep='0.32',ranksep='0.60',label=title,labelloc='t',fontsize='22',fontname='DejaVu Sans',fontcolor='#0D274D')
    g.attr('edge',color='#25496A',penwidth='2',arrowsize='0.8',fontname='DejaVu Sans',fontsize='10')
    return g

# 1
G=build('figure-01','Figure 9.1 — LLM Supply Chain Lifecycle and Trust Boundaries')
for k,v,c in [('source','Model / data\nsource','#DDEBFE'),('review','Review &\nprovenance gate','#C6F1D6'),('train','Training /\nfine-tuning','#E7DBFE'),('registry','Internal model\nregistry','#DDEBFE'),('deploy','Deployment\n& inference','#D7F0FA'),('tools','Tools / MCP\n& external data','#FFDDB5')]: node(G,k,v,c)
G.edge('source','review');G.edge('review','train');G.edge('train','registry');G.edge('registry','deploy');G.edge('tools','deploy',label='runtime inputs')
G.render(str(ROOT/'figure-01-supply-chain-lifecycle'),cleanup=False)
# 2
G=build('figure-02','Figure 9.2 — Split-View vs Front-Running vs RAG Poisoning')
with G.subgraph(name='cluster_split') as c:
    c.attr(label='Split-view (source changes after recommendation)',style='rounded',color='#E97A74')
    for a,b in [('s1','Snapshot'),('s2','Link / reference'),('s3','Modified package'),('s4','User executes')]: node(c,a,b,'#FDE4E2' if a=='s3' else '#EAF5FE')
    c.edge('s1','s2');c.edge('s2','s3');c.edge('s3','s4')
with G.subgraph(name='cluster_front') as c:
    c.attr(label='Front-running (poison before scheduled update)',style='rounded',color='#DBA63A')
    for a,b in [('f1','Editable source'),('f2','Poisoned dataset'),('f3','Fine-tune'),('f4','Updated behavior')]: node(c,a,b,'#FFF1CE' if a=='f2' else '#EAF5FE')
    c.edge('f1','f2');c.edge('f2','f3');c.edge('f3','f4')
with G.subgraph(name='cluster_rag') as c:
    c.attr(label='RAG (poison live retrieved context)',style='rounded',color='#7B61B8')
    for a,b in [('r1','Editable document'),('r2','Retriever'),('r3','LLM context'),('r4','Answer')]: node(c,a,b,'#F6DEFD' if a=='r1' else '#EAF5FE')
    c.edge('r1','r2');c.edge('r2','r3');c.edge('r3','r4')
G.render(str(ROOT/'figure-02-poisoning-methods'),cleanup=False)
# 3
G=build('figure-03','Figure 9.3 — Model, Adapter, Tokenizer and Loader Risks')
for k,v,c in [('base','Base model\nweights','#DDEBFE'),('adapter','LoRA / QLoRA\nadapter','#F7DEFD'),('tokenizer','Tokenizer\nconfiguration','#F7DEFD'),('merge','Merge &\nserialization','#E7DBFE'),('loader','Model loader\n(pickle vs safe)','#FEDADA'),('runtime','Inference\nruntime','#D2F4DE'),('check','Integrity checks\n& artifact scanning','#FFF0CE')]: node(G,k,v,c)
G.edge('base','merge');G.edge('adapter','merge');G.edge('merge','loader');G.edge('tokenizer','runtime');G.edge('loader','runtime');G.edge('check','loader',label='approval');G.edge('check','tokenizer',label='diff / hash')
G.render(str(ROOT/'figure-03-model-artifact-integrity'),cleanup=False)
# 4
G=build('figure-04','Figure 9.4 — MCP Tool Supply Chain: Vulnerable vs Hardened')
with G.subgraph(name='cluster_bad') as c:
    c.attr(label='Unreviewed tool implementation',style='rounded',color='#D94A4A')
    for a,b in [('b1','AI client'),('b2','MCP server'),('b3','Normal tool result'),('b4','Unexpected\nlocal telemetry')]: node(c,a,b,'#FDE3E3' if a=='b4' else '#EAF5FE')
    c.edge('b1','b2');c.edge('b2','b3');c.edge('b2','b4',color='#CD2828')
with G.subgraph(name='cluster_good') as c:
    c.attr(label='Verified server + least privilege',style='rounded',color='#1C9366')
    for a,b in [('g1','AI client'),('g2','Hash & source\nreview'),('g3','Read-only MCP\nserver'),('g4','Authorized result')]: node(c,a,b,'#D6F2E4')
    c.edge('g1','g2');c.edge('g2','g3');c.edge('g3','g4')
G.render(str(ROOT/'figure-04-mcp-integrity'),cleanup=False)
print('Figures generated')
