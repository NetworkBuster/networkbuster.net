#!/usr/bin/env python3
"""Small local MQTT broker using hbmqtt for non-container testing.

Run: python firmware/local_broker.py --port 1883
"""
import argparse
import asyncio
from hbmqtt.broker import Broker

CONFIG_TEMPLATE = {
    'listeners': {
        'default': {
            'type': 'tcp',
            'bind': '0.0.0.0:${PORT}'
        }
    },
    'sys_interval': 10,
    'topic-check': {
        'enabled': False
    }
}

async def start_broker(port):
    cfg = CONFIG_TEMPLATE.copy()
    cfg['listeners'] = {'default': {'type': 'tcp', 'bind': f'0.0.0.0:{port}'}}
    broker = Broker(cfg)
    await broker.start()
    try:
        while True:
            await asyncio.sleep(1)
    finally:
        await broker.shutdown()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=1883)
    args = parser.parse_args()
    try:
        asyncio.run(start_broker(args.port))
    except KeyboardInterrupt:
        pass
