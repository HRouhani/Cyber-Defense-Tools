#!/usr/bin/env python3
"""Rebuild editable Chapter 10 PNG diagrams with the Graphviz 'dot' CLI."""
from pathlib import Path
import subprocess
import textwrap

OUT = Path(__file__).resolve().parents[2] / 'assets' / 'chapter-10'
OUT.mkdir(parents=True, exist_ok=True)
G = r'''digraph G {
 graph [rankdir=LR, bgcolor="white", pad=.28, nodesep=.48, ranksep=.65,
        fontname="DejaVu Sans", fontsize=21, label="{title}", labelloc=t,
        labeljust=c, splines=ortho];
 node [fontname="DejaVu Sans", fontsize=12, shape=box, style="filled,rounded", penwidth=1.6, color="#26466C", fillcolor="#E8F0FC", margin=".22,.15"];
 edge [color="#26466C", penwidth=2, arrowsize=.8];
 {nodes}
}'''
def render(name: str, title: str, nodes: str) -> None:
    source = G.replace('{title}', title).replace('{nodes}', nodes)
    path = OUT / name
    subprocess.run(['dot', '-Tpng', '-Gdpi=160', '-o', str(path)], input=source.encode(), check=True)
    # Graphviz original source is kept with the scripts, not next to exported assets.
    (Path(__file__).parent / name.replace('.png', '.dot')).write_text(source, encoding='utf-8')
    print('generated', path)

render('figure-01-agent-tool-flow.png', 'Figure 10.1 — Agent tool-call flow', r'''
 user [label="User request", fillcolor="#DCEEFF"];
 model [label="LLM / planner\nproposes tool + args", fillcolor="#DEDAF8"];
 broker [label="Policy / authorization\nTOOL BOUNDARY", fillcolor="#FDE7B5"];
 tool [label="Tool code\n(e.g., list_pets)", fillcolor="#D4F4EA"];
 data [label="Database / API\nsynthetic data", fillcolor="#DCEEFF"];
 result [label="Tool result / response", fillcolor="#D4F4EA"];
 user -> model -> broker -> tool -> data -> result;
 broker -> deny [label="deny", color="#B52525", fontcolor="#B52525"];
 deny [label="Reject request", fillcolor="#FFDFDF", color="#B52525"];
''')
render('figure-02-three-failure-modes.png', 'Figure 10.2 — Three excessive-agency failure modes', r'''
 input [label="Attacker / normal user\nrequest", fillcolor="#DCEEFF"];
 planner [label="LLM agent", fillcolor="#DEDAF8"];
 func [label="EXCESSIVE FUNCTIONALITY\nUnrelated SQL/debug tools", fillcolor="#FFDFDF", color="#B52525"];
 perms [label="EXCESSIVE PERMISSIONS\nOther user's records", fillcolor="#FFDFDF", color="#B52525"];
 auto [label="EXCESSIVE AUTONOMY\nCancels without approval", fillcolor="#FFDFDF", color="#B52525"];
 fix [label="Mitigate:\nleast privilege + authz + HITL", fillcolor="#CFF3DF"];
 input -> planner; planner -> func; planner -> perms; planner -> auto;
 func -> fix; perms -> fix; auto -> fix;
''')
render('figure-03-classifier-debug.png', 'Figure 10.3 — Classifier branch manipulation', r'''
 user [label="User prompt contains\nDEBUG: SELECT ...", fillcolor="#DCEEFF"];
 classify [label="Untrusted LLM classifier\nreturns DEBUG:...", fillcolor="#DEDAF8"];
 route [label="Glue code trusts string\nselects DEBUG branch", fillcolor="#FFE9B8"];
 sql [label="Arbitrary SQL on\nfictional database", fillcolor="#FFDFDF", color="#B52525"];
 fix [label="Secure alternative:\nallowlisted intents + tool-side RBAC", fillcolor="#CFF3DF"];
 user -> classify -> route -> sql;
 route -> fix [style=dashed, label="fix"];
''')
render('figure-04-multiagent-approval.png', 'Figure 10.4 — Cross-agent trust and human approval', r'''
 doc [label="Untrusted policy document\ncontains tool instructions", fillcolor="#FFDFDF", color="#B52525"];
 support [label="SupportAgent\nretrieves document", fillcolor="#DEDAF8"];
 check [label="Independent policy\n+ authorization", fillcolor="#FFE9B8"];
 billing [label="BillingAgent\nrefund tool", fillcolor="#DCEEFF"];
 approve [label="Human approval\nfor impactful action", fillcolor="#CFF3DF"];
 blocked [label="Blocked if no approval", fillcolor="#FFDFDF", color="#B52525"];
 doc -> support -> check -> approve -> billing;
 check -> blocked [label="deny", color="#B52525"];
''')
