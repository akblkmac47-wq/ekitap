#!/bin/bash
# Çift tıkla: yerel sunucuyu başlatır ve ÜRETİCİ sayfasını Chrome'da açar.
cd "$(dirname "$0")"
echo "════════════════════════════════════════════════════"
echo "  SANAT ORMANI'NIN SIRRI"
echo "════════════════════════════════════════════════════"
if [ -z "$(ls -A ses 2>/dev/null | grep -v .gitkeep)" ]; then
  HEDEF="http://localhost:8000/uretici.html"
  echo "  Sesler henüz üretilmemiş → ÜRETİCİ sayfası açılıyor."
  echo "  Açılan sayfada tek düğmeye bas, 'ekitap' klasörünü seç."
else
  HEDEF="http://localhost:8000/index.html"
  echo "  Kitap açılıyor…"
fi
echo "  (Bu pencereyi kapatınca sunucu durur.)"
echo "════════════════════════════════════════════════════"
( sleep 1; open -a "Google Chrome" "$HEDEF" 2>/dev/null || open "$HEDEF" ) &
python3 -m http.server 8000
