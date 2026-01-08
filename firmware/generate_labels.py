#!/usr/bin/env python3
"""Generate printable labels (PNG + PDF) for kits with SHA256 and QR codes.

Outputs per-file PNG and a combined PDF sheet.

Usage:
  python firmware/generate_labels.py --db firmware/checksums_db.json --out labels --base-url https://github.com/Cleanskiier27/Networkbuster.net/releases
"""
import argparse
import json
import os
from PIL import Image, ImageDraw, ImageFont
import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

FONT_PATH = None  # system default
LABEL_W = 400
LABEL_H = 200


def load_db(db_path):
    with open(db_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def make_label_png(name, sha, out_path, base_url=None):
    short = sha[:12]
    img = Image.new('RGB', (LABEL_W, LABEL_H), color='white')
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(FONT_PATH or 'arial.ttf', 14)
    except Exception:
        font = ImageFont.load_default()
    d.text((10,10), f"{name}", fill='black', font=font)
    d.text((10,36), f"SHA256: {sha}", fill='black', font=font)
    d.text((10,60), f"Short: {short}", fill='black', font=font)
    # QR
    qr_data = base_url + '/' + name if base_url else sha
    qr = qrcode.make(qr_data)
    qr = qr.resize((120,120))
    img.paste(qr, (LABEL_W - 130, 10))
    img.save(out_path)
    return out_path


def make_pdf(label_files, pdf_path):
    c = canvas.Canvas(pdf_path, pagesize=A4)
    w, h = A4
    x = 40; y = h - 220
    for i, lf in enumerate(label_files):
        c.drawImage(lf, x, y, width=200, height=100)
        x += 220
        if x > w - 200:
            x = 40; y -= 140
        if y < 40:
            c.showPage(); x = 40; y = h - 220
    c.save()


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--db', default='firmware/checksums_db.json')
    p.add_argument('--out', default='labels')
    p.add_argument('--base-url', default='')
    args = p.parse_args()

    db = load_db(args.db)
    os.makedirs(args.out, exist_ok=True)
    label_files = []
    for name, meta in db['files'].items():
        safe_name = name.replace('\\','-').replace('/','-')
        png = os.path.join(args.out, safe_name + '.png')
        make_label_png(safe_name, meta['sha256'], png, base_url=args.base_url)
        label_files.append(png)
    pdf = os.path.join(args.out, 'labels.pdf')
    make_pdf(label_files, pdf)
    print('Wrote', len(label_files), 'labels ->', args.out)
