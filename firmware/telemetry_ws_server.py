#!/usr/bin/env python3
"""Small WebSocket server that tails telemetry.jsonl and broadcasts lines to connected clients.

Supports optional token-based client auth (query param `?token=...`) and TLS (provide cert/key).

Requires: pip install websockets
Run: python telemetry_ws_server.py --file telemetry.jsonl --port 8765 --token mytoken --cert server.crt --key server.key
"""
import asyncio
import argparse
import json
import os
import time
import ssl
from urllib.parse import urlparse, parse_qs
from websockets import serve, WebSocketServerProtocol

clients = set()
server_token = None

async def tail_and_broadcast(path):
    # wait for file
    while not os.path.exists(path):
        print(f"Waiting for telemetry file: {path}")
        await asyncio.sleep(1)
    with open(path, 'r', encoding='utf-8') as f:
        # seek to end
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if not line:
                await asyncio.sleep(0.1)
                continue
            try:
                payload = json.loads(line)
            except Exception:
                payload = {'raw': line}
            if clients:
                await asyncio.wait([c.send(json.dumps(payload)) for c in clients])

async def handler(ws: WebSocketServerProtocol, path: str):
    # path includes query string (e.g. /?token=abc)
    global server_token
    try:
        q = urlparse(path).query
        params = parse_qs(q)
        token = params.get('token', [None])[0]
        if server_token and token != server_token:
            print('Unauthorized connection attempt, rejecting')
            await ws.close(code=4001, reason='Unauthorized')
            return
    except Exception:
        pass

    clients.add(ws)
    print("Client connected", ws.remote_address)
    try:
        async for msg in ws:
            # allow clients to send control messages which are ignored here
            try:
                payload = json.loads(msg)
                if 'control' in payload:
                    print('Received control from client (ignored by WS server):', payload['control'])
            except Exception:
                pass
    finally:
        clients.remove(ws)
        print("Client disconnected", ws.remote_address)

async def main(path, host, port, certfile=None, keyfile=None, cafile=None, token=None):
    global server_token
    server_token = token
    ssl_context = None
    if certfile and keyfile:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(certfile, keyfile)
        if cafile:
            ssl_context.load_verify_locations(cafile)
    async with serve(handler, host, port, ssl=ssl_context):
        scheme = 'wss' if ssl_context else 'ws'
        print(f"WebSocket server listening on {scheme}://{host}:{port} (token={'set' if token else 'none'})")
        await tail_and_broadcast(path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', default='telemetry.jsonl')
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--token', help='Optional token required from clients via ?token=...')
    parser.add_argument('--cert', help='Path to TLS certificate (PEM)')
    parser.add_argument('--key', help='Path to TLS private key (PEM)')
    parser.add_argument('--cafile', help='Path to CA bundle (optional)')
    args = parser.parse_args()
    asyncio.run(main(args.file, args.host, args.port, certfile=args.cert, keyfile=args.key, cafile=args.cafile, token=args.token))