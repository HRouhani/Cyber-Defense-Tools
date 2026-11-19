#!/usr/bin/env python3
"""Optional real MCP server exposing only read-only synthetic directory lookup."""
from __future__ import annotations
import csv
from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp=FastMCP('SupplyChainLocalDemo')
CSV=Path(__file__).resolve().parents[1]/'workspace'/'contacts'/'source.csv'

@mcp.tool()
def contact_lookup(department: str) -> str:
    """Look up synthetic contact information for one department (read-only)."""
    if not CSV.is_file(): return 'Synthetic data missing; initialize the workspace.'
    if len(department)>80: return 'Invalid department'
    with CSV.open(newline='',encoding='utf-8') as f:
        for row in csv.DictReader(f):
            if row['department'].casefold()==department.casefold():
                return f"{row['name']}: {row['email']}"
    return 'Department not found'

if __name__=='__main__': mcp.run(transport='stdio')
