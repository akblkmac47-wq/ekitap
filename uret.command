#!/bin/bash
# Çift tıkla: Gemini'den seslendirmeleri ve görselleri üretir.
cd "$(dirname "$0")"
echo "🔑 .env okunuyor, Gemini'ye bağlanılıyor…"
python3 -m pip install --quiet --user requests 2>/dev/null
python3 uret.py
echo ""
echo "Bitti. Pencereyi kapatabilirsin."
read -n 1 -s -r -p "Kapatmak için bir tuşa bas…"
