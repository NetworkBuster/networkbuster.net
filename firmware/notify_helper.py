#!/usr/bin/env python3
"""Notification helpers: MQTT and Email

Functions:
 - notify_mqtt(broker,port,topic,payload,username=None,password=None)
 - notify_email(smtp_host, smtp_port, from_addr, to_addrs, subject, body, username=None, password=None)
"""
import json
import smtplib
from email.message import EmailMessage
from paho.mqtt import client as mqtt_client


def notify_mqtt(broker='127.0.0.1', port=1883, topic='checksums/alerts', payload=None, username=None, password=None):
    client = mqtt_client.Client()
    if username:
        client.username_pw_set(username, password)
    client.connect(broker, port)
    client.loop_start()
    try:
        client.publish(topic, json.dumps(payload))
    finally:
        client.loop_stop()
        client.disconnect()


def notify_email(smtp_host, smtp_port, from_addr, to_addrs, subject, body, username=None, password=None, use_tls=True):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = ', '.join(to_addrs) if isinstance(to_addrs, (list,tuple)) else to_addrs
    msg.set_content(body)

    server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
    try:
        if use_tls:
            server.starttls()
        if username:
            server.login(username, password)
        server.send_message(msg)
    finally:
        try:
            server.quit()
        except Exception:
            pass
