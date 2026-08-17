#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
parts/ klasöründeki dört parçayı birleştirip index.html dosyasını üretir.

  python3 birlestir.py

Tek kaynak parts/*.html — düzenlemeleri ORADA yap, sonra bu aracı çalıştır.
index.html türetilmiş dosyadır, elle düzenleme.
"""
import os, sys

BURASI = os.path.dirname(os.path.abspath(__file__))
PARCA  = os.path.join(BURASI, "parts")
HEDEF  = os.path.join(BURASI, "index.html")
SIRA   = ["01_head.html", "02_svg.html", "03_pages.html", "04_js.html"]


def main():
    parcalar = []
    for ad in SIRA:
        yol = os.path.join(PARCA, ad)
        if not os.path.isfile(yol):
            sys.exit(f"❌ Parça bulunamadı: {yol}")
        metin = open(yol, encoding="utf-8").read()
        parcalar.append(metin.rstrip("\n"))
        print(f"  ✓ {ad}  ({len(metin.splitlines())} satır)")

    cikti = "\n".join(parcalar) + "\n"
    open(HEDEF, "w", encoding="utf-8").write(cikti)
    print(f"\n🎉 index.html yazıldı — {len(cikti.splitlines())} satır, {len(cikti)//1024} KB")


if __name__ == "__main__":
    main()
