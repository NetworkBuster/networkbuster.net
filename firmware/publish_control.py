#!/usr/bin/env python3
"""Simple helper to publish a control message to a device control topic."""
import argparse
import json
from paho.mqtt import client as mqtt_client

parser = argparse.ArgumentParser()
parser.add_argument('--broker', default='test.mosquitto.org')
parser.add_argument('--port', type=int, default=1883)
parser.add_argument('--id', default='device-01')
parser.add_argument('--payload', default='{"set_mode":"low_power"}')
args = parser.parse_args()

c = mqtt_client.Client('pubctl')
c.connect(args.broker, args.port)
c.loop_start()
topic = f'device/{args.id}/power/control'
c.publish(topic, args.payload)
print('Published', topic, args.payload)
c.loop_stop()
c.disconnect()