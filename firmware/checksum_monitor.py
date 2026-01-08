#!/usr/bin/env python3
"""Checksum Monitor

Provides persistent checks for files against expected SHA-256 values.

Commands:
  init   --dir <path> --db <file>       Create baseline DB from files in directory
  check  --db <file>                    Run a single check and print results
  monitor --db <file> --interval N      Run continuously, write alerts to alerts.log

DB format (JSON):
{
  "files": {
    "relative/path/to/file": {
       "sha256": "...",
       "size": 12345,
       "mtime": 1600000000,
       "status": "good|bad",
       "last_checked": 1600000000,
       "current_sha256": "..."
    },
    ...
  }
}

Examples:
  python firmware/checksum_monitor.py init --dir releases --db checksums_db.json
  python firmware/checksum_monitor.py check --db checksums_db.json
  python firmware/checksum_monitor.py monitor --db checksums_db.json --interval 60

"""
import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path
import logging

DEFAULT_DB = 'checksums_db.json'
ALERT_LOG = 'firmware/alerts.log'

logger = logging.getLogger('checksum-monitor')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(handler)


def compute_sha256(path, block_size=65536):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(block_size), b''):
            h.update(block)
    return h.hexdigest()


def load_db(db_path):
    if not os.path.exists(db_path):
        return {'files': {}}
    with open(db_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_db(db, db_path):
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=2, sort_keys=True)


def scan_dir(base_dir, recursive=True, pattern=None):
    base_dir = Path(base_dir)
    out = []
    if recursive:
        it = base_dir.rglob('*')
    else:
        it = base_dir.glob('*')
    for p in it:
        if p.is_file():
            if pattern and not p.match(pattern):
                continue
            out.append(p)
    return out


def init_db(base_dir, db_path, recursive=True, pattern=None):
    base_dir = Path(base_dir)
    files = scan_dir(base_dir, recursive=recursive, pattern=pattern)
    db = {'files': {}}
    for p in files:
        rel = str(p.relative_to(base_dir))
        sha = compute_sha256(p)
        db['files'][rel] = {
            'sha256': sha,
            'size': p.stat().st_size,
            'mtime': int(p.stat().st_mtime),
            'status': 'good',
            'last_checked': None,
            'current_sha256': sha
        }
        logger.info('Baseline: %s -> %s', rel, sha[:16])
    save_db(db, db_path)
    logger.info('Wrote DB with %d files to %s', len(db['files']), db_path)
    return db


def check_once(db_path, base_dir='.', add_new=False):
    db = load_db(db_path)
    base_dir = Path(base_dir)
    results = {'good': [], 'bad': [], 'missing': [], 'added': []}

    # Check each entry
    for rel, meta in list(db['files'].items()):
        p = base_dir / rel
        if not p.exists():
            meta['status'] = 'missing'
            meta['last_checked'] = int(time.time())
            results['missing'].append(rel)
            logger.warning('Missing: %s', rel)
            continue
        cur_sha = compute_sha256(p)
        meta['current_sha256'] = cur_sha
        meta['last_checked'] = int(time.time())
        if cur_sha.lower() == meta['sha256'].lower():
            meta['status'] = 'good'
            results['good'].append(rel)
            logger.info('Good: %s', rel)
        else:
            meta['status'] = 'bad'
            results['bad'].append(rel)
            logger.error('BAD: %s expected %s found %s', rel, meta['sha256'][:12], cur_sha[:12])
            # write alert
            alert = {'ts': int(time.time()), 'file': rel, 'expected': meta['sha256'], 'found': cur_sha}
            with open(ALERT_LOG, 'a', encoding='utf-8') as af:
                af.write(json.dumps(alert) + '\n')
            # optionally notify via MQTT or email (configured via env or parameters)
            try:
                from .notify_helper import notify_mqtt, notify_email
            except Exception:
                try:
                    from notify_helper import notify_mqtt, notify_email
                except Exception:
                    notify_mqtt = None; notify_email = None
            if notify_mqtt and os.environ.get('CHECK_MON_MQTT') == '1':
                try:
                    notify_mqtt(broker=os.environ.get('CHECK_MON_MQTT_HOST','127.0.0.1'), port=int(os.environ.get('CHECK_MON_MQTT_PORT','1883')), topic=os.environ.get('CHECK_MON_MQTT_TOPIC','checksums/alerts'), payload=alert, username=os.environ.get('CHECK_MON_MQTT_USER'), password=os.environ.get('CHECK_MON_MQTT_PASS'))
                except Exception as e:
                    logger.warning('MQTT notify failed: %s', str(e))
            if notify_email and os.environ.get('CHECK_MON_EMAIL') == '1':
                try:
                    notify_email(smtp_host=os.environ.get('CHECK_MON_SMTP_HOST','localhost'), smtp_port=int(os.environ.get('CHECK_MON_SMTP_PORT','25')), from_addr=os.environ.get('CHECK_MON_FROM','no-reply@example.com'), to_addrs=os.environ.get('CHECK_MON_TO','admin@example.com').split(','), subject=f'Checksum alert: {rel}', body=json.dumps(alert, indent=2), username=os.environ.get('CHECK_MON_SMTP_USER'), password=os.environ.get('CHECK_MON_SMTP_PASS'))
                except Exception as e:
                    logger.warning('Email notify failed: %s', str(e))

    # Optionally find new files not in db
    all_files = scan_dir(base_dir, recursive=True)
    for p in all_files:
        rel = str(p.relative_to(base_dir))
        if rel not in db['files']:
            sha = compute_sha256(p)
            db['files'][rel] = {
                'sha256': sha,
                'size': p.stat().st_size,
                'mtime': int(p.stat().st_mtime),
                'status': 'new',
                'last_checked': int(time.time()),
                'current_sha256': sha
            }
            results['added'].append(rel)
            logger.info('New file added to DB: %s', rel)

    # Write last scan summary for dashboard consumption
    last_scan = {'ts': int(time.time()), 'results': results}
    try:
        with open('firmware/last_scan.json', 'w', encoding='utf-8') as lf:
            json.dump(last_scan, lf, indent=2)
        # copy to web-app data folder if exists
        webdata = os.path.join('web-app', 'data')
        os.makedirs(webdata, exist_ok=True)
        with open(os.path.join(webdata, 'checksums.json'), 'w', encoding='utf-8') as wf:
            json.dump(last_scan, wf, indent=2)
    except Exception as e:
        logger.warning('Could not write last_scan: %s', e)

    save_db(db, db_path)
    return results


def monitor(db_path, base_dir='.', interval=60, add_new=False):
    logger.info('Starting monitor: db=%s base=%s interval=%s', db_path, base_dir, interval)
    try:
        while True:
            res = check_once(db_path, base_dir=base_dir, add_new=add_new)
            logger.info('Scan result: good=%d bad=%d missing=%d added=%d', len(res['good']), len(res['bad']), len(res['missing']), len(res['added']))
            # sleep
            time.sleep(interval)
    except KeyboardInterrupt:
        logger.info('Monitor stopped by user')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest='cmd')

    init_p = sub.add_parser('init')
    init_p.add_argument('--dir', default='releases')
    init_p.add_argument('--db', default=DEFAULT_DB)
    init_p.add_argument('--pattern', help='glob pattern to include')

    check_p = sub.add_parser('check')
    check_p.add_argument('--db', default=DEFAULT_DB)
    check_p.add_argument('--dir', default='releases')

    mon_p = sub.add_parser('monitor')
    mon_p.add_argument('--db', default=DEFAULT_DB)
    mon_p.add_argument('--dir', default='releases')
    mon_p.add_argument('--interval', type=int, default=60)

    args = p.parse_args()

    if args.cmd == 'init':
        init_db(args.dir, args.db, pattern=args.pattern)
        sys.exit(0)
    elif args.cmd == 'check':
        results = check_once(args.db, base_dir=args.dir)
        print(json.dumps(results, indent=2))
        sys.exit(0 if len(results['bad'])==0 and len(results['missing'])==0 else 2)
    elif args.cmd == 'monitor':
        monitor(args.db, base_dir=args.dir, interval=args.interval)
    else:
        p.print_help()
        sys.exit(1)
