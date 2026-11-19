#!/usr/bin/env python3
"""Optional official MCP SDK stdio client. Requires pip install mcp."""
import asyncio
import sys
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    server=Path(__file__).with_name('mcp_server.py')
    params=StdioServerParameters(command=sys.executable,args=[str(server)])
    async with stdio_client(params) as (read,write):
        async with ClientSession(read,write) as session:
            await session.initialize()
            tools=await session.list_tools()
            print('Available tools:',[t.name for t in tools.tools])
            result=await session.call_tool('contact_lookup',{'department':'IT Support'})
            print('Tool result:',result)

if __name__=='__main__': asyncio.run(main())
