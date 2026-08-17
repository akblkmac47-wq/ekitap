# 🎨 Sanat Ormanı'nın Sırrı

**Görsel Sanatlar · İlkokul 1. Sınıf** için etkileşimli, **sesli** ve **animasyonlu** dijital hikâye kitabı.

> Deniz ve sihirli fırçası **Fırçacan**, renkleri kaçmış Sanat Ormanı'nı kurtarmak için
> **çizgi · şekil · renk · doku** anahtarlarını toplar.

| | |
|---|---|
| **Sayfa** | 19 |
| **Etkinlik** | 9 (hepsi gerçekten çalışır) |
| **Anahtar** | 4 (çizgi, şekil, renk, doku) |
| **Ses** | Gemini TTS ile üretilmiş Türkçe anlatım + WebAudio efektleri |
| **Görsel** | Gemini Image ile üretilmiş sahneler (+ gömülü SVG yedek) |
| **Bağımlılık** | Yok — tek HTML dosyası |

---

## 🚀 3 ADIMDA ÇALIŞTIR

### 1) Anahtarı koy
Proje klasöründe `.env` dosyası oluştur (`.env.ornek`'i kopyalayabilirsin):

```
GEMINI_API_KEY=senin_anahtarin
```

> `.env` dosyası `.gitignore` içinde — **GitHub'a asla gitmez.**

### 2) Sesleri ve görselleri üret
Terminal'de proje klasöründe:

```bash
pip3 install requests
python3 uret.py
```

*(veya Finder'da `uret.command` dosyasına çift tıkla)*

Bu komut:
- `index.html` içindeki **19 anlatım metnini** okur → `ses/s01.mp3 … s19.mp3`
- Önce **karakter sayfasını** üretir → sonra 15 sahneyi o görseli **referans vererek** üretir
  (böylece Deniz ve Fırçacan her sayfada **aynı** görünür) → `gorseller/*.png`

Faydalı seçenekler:

```bash
python3 uret.py --sadece ses       # sadece seslendirme
python3 uret.py --sadece gorsel    # sadece görseller
python3 uret.py --yenile           # var olanların üzerine yaz
python3 uret.py --sayfa 5 7 12     # sadece bu sayfaların sesi
```

### 3) Aç
`baslat.command` dosyasına çift tıkla → tarayıcıda açılır.
(Ya da `python3 -m http.server 8000` çalıştırıp `http://localhost:8000` adresine git.)

> Ses ve görsel dosyaları **yoksa** kitap yine sorunsuz çalışır:
> anlatım tarayıcının Türkçe sesiyle okunur, sahneler gömülü SVG çizimlerle görünür.

---

## 🌍 CANLIYA ALMA

### GitHub Pages (en kolay)
```bash
git init
git add .
git commit -m "Sanat Ormanı'nın Sırrı"
git branch -M main
git remote add origin https://github.com/akblkmac47-wq/ekitap.git
git push -u origin main
```
Sonra: **Settings → Pages → Source: `main` / `root` → Save.**
Adres: `https://akblkmac47-wq.github.io/ekitap/`

### Netlify / Vercel
Klasörü sürükle-bırak yeterli — build adımı yok, statik site.

---

## 📖 SAYFA HARİTASI

| # | Sayfa | Etkinlik | Kazanım |
|---|---|---|---|
| 1 | Kapak | — | — |
| 2 | Konuşan Fırça (okul bahçesi) | — | Giriş |
| 3 | Renkleri Kaçmış Orman | — | Problem kurulumu |
| 4 | Görev Haritası | — | Yönlendirme |
| 5 | **1. Durak: Çizgi Nehri** (Kıvrım) | — | Çizgi türlerini tanıma |
| 6 | Hangisi Doğru Çizgi? | ⭐1 | Ayırt etme |
| 7 | Çizgiyi Doğada Bul | ⭐2 🔑 **çizgi** | İlişkilendirme |
| 8 | **2. Durak: Şekil Kayalıkları** (Köşe) | — | Temel şekiller |
| 9 | Nesneyi Şekliyle Eşleştir | ⭐3 | İlişkilendirme |
| 10 | Şekilleri Say | ⭐4 🔑 **şekil** | Sayma + ayırt etme |
| 11 | **3. Durak: Renk Şelalesi** (Ebru) | — | Ana/ara renkler |
| 12 | Renkler Karışınca | ⭐5 | Tahmin |
| 13 | Sıcak mı, Soğuk mu? | ⭐6 🔑 **renk** | Sınıflandırma |
| 14 | **4. Durak: Doku Mağarası** (Pütür) | — | Doku kavramı |
| 15 | Dokuları Eşleştir | ⭐7 🔑 **doku** | İlişkilendirme |
| 16 | Orman Galerisi | ⭐8 | Estetik yargı / duygu ifadesi |
| 17 | **Büyük Final: Ormanı Sen Boya** | ⭐9 | Özgün ürün oluşturma |
| 18 | Öğrenme Günlüğüm | — | Değerlendirme |
| 19 | Kapanış + Belge | — | Paylaşma |

---

## 🎬 NELER VAR?

**Sesler**
- Her sayfa açılınca **otomatik** Türkçe anlatım (Gemini TTS, `Aoede` sesi)
- Oynat/durdur + **ilerleme çubuğu** + ses dalgası göstergesi
- Doğru/yanlış melodileri, yıldız fanfarı, **anahtar kazanma** jingle'ı, sayfa çevirme, fırça sesi
- `🔔` ile efektler, `🎵 Oto` ile otomatik anlatım kapatılabilir

**Animasyonlar**
- 3D sayfa çevirme (ileri/geri yönüne göre farklı)
- Arka planda süzülen renk zerrecikleri
- Hikâye cümleleri sırayla kayarak gelir, kartlar teker teker belirir
- Çizgiler **kendi kendine çizilir**, şekiller nabız atar, kelebek kanat çırpar
- Tıklamada **dalgacık (ripple)** efekti
- Anahtar kazanınca ekranda büyük **🔑 rozeti** + konfeti + haritada durak yeşile döner

**Etkileşim**
- Çoktan seçmeli, eşleştirme, sayma, sınıflandırma (sıcak/soğuk), duygu seçimi
- **Dijital tuval:** 12 renk, 3 fırça kalınlığı, 4 şekil damgası, **2 doku fırçası**, geri al, PNG indir
- Öğrenme günlüğü önceki seçimlerden **otomatik dolar**, `.txt` olarak inebilir
- Klavye: `←` `→` sayfa, `boşluk` ses

---

## 🔒 GÜVENLİK NOTU

API anahtarını sohbet/paylaşım ortamlarına yazdıysan, işin bitince
[Google AI Studio](https://aistudio.google.com/apikey) üzerinden **anahtarı iptal edip yenisini üret**.
Bu depoda anahtar `.env` içinde tutulur ve `.gitignore` ile dışarıda bırakılır.

---

## 🛠 TEKNİK

- Tek dosya `index.html` (HTML + CSS + JS, ~110 KB) — çerçeve/kütüphane yok
- Tarayıcı deposu (localStorage) **kullanılmaz**
- `prefers-reduced-motion` desteklenir (animasyonlar otomatik kapanır)
- Yazdırma stili var: `🖨️` ile 19 sayfa PDF olarak çıkar → **Heyzine Flipbooks**'a yüklenebilir
- Kaynak parçalar `parts/` klasöründedir; `index.html` bunların birleşimidir:
  ```bash
  cat parts/01_head.html parts/02_svg.html parts/03_pages.html parts/04_js.html > index.html
  ```

## 📁 Klasör yapısı
```
ekitap/
├── index.html          ← kitabın kendisi
├── uret.py             ← Gemini ses + görsel üretici
├── uret.command        ← çift tıkla üret (macOS)
├── baslat.command      ← çift tıkla aç (macOS)
├── .env                ← API anahtarı (gitignore'da)
├── .env.ornek
├── ses/                ← s01.mp3 … s19.mp3   (uret.py doldurur)
├── gorseller/          ← 00_karakterler.png, 01_kapak.png … (uret.py doldurur)
└── parts/              ← kaynak parçalar
```
