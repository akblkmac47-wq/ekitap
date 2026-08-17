# 🚀 Canlıya Alma — Adım Adım

Depo **hazır ve commit'lenmiş** durumda (`~/Desktop/ekitap`).
Kalan tek şey: GitHub'a göndermek (push) ve Pages'i açmak.

---

## ADIM 0 — Durum kontrolü (isteğe bağlı)

Terminal'i aç (Spotlight → "Terminal") ve yapıştır:

```bash
cd ~/Desktop/ekitap
git log --oneline
git remote -v
```

Görmen gereken:
```
a13b3c5 gitignore: gecici klasor
70e6f8b Sanat Ormani'nin Sirri - etkilesimli sesli e-kitap (19 sayfa, 9 etkinlik)
origin  https://github.com/akblkmac47-wq/ekitap.git (fetch)
origin  https://github.com/akblkmac47-wq/ekitap.git (push)
```

---

## ADIM 1 — GitHub'a gönder (push)

### Yol A · GitHub CLI (en kolay, tavsiye)

```bash
brew install gh          # kuruluysa atla
gh auth login            # GitHub.com → HTTPS → Y → tarayıcıda giriş yap
cd ~/Desktop/ekitap
git push -u origin main
```

### Yol B · Token ile (brew yoksa)

1. Şu adrese git: **https://github.com/settings/tokens/new**
2. Note: `ekitap`, Expiration: 90 gün, **repo** kutusunu işaretle → **Generate token**
3. Çıkan `ghp_...` kodunu kopyala.
4. Terminal:

```bash
cd ~/Desktop/ekitap
git push -u origin main
```
   - `Username:` → `akblkmac47-wq`
   - `Password:` → **token'ı yapıştır** (şifreni değil!)

### Yol C · Hiç terminal istemiyorsan

**https://github.com/akblkmac47-wq/ekitap/upload/main** adresine git,
`~/Desktop/ekitap` içindeki şu dosya/klasörleri sürükle-bırak:

```
index.html   uretici.html   README.md   uret.py
baslat.command   uret.command   .gitignore   .env.ornek
parts/  (klasör)   ses/  (varsa)   gorseller/  (varsa)
```

> ⚠️ **`.env` dosyasını ASLA yükleme** — API anahtarın içinde.

---

## ADIM 2 — GitHub Pages'i aç

1. **https://github.com/akblkmac47-wq/ekitap/settings/pages**
2. **Source** → `Deploy from a branch`
3. **Branch** → `main`  ·  **Folder** → `/ (root)`
4. **Save**

1–2 dakika bekle. Sayfanın üstünde yeşil kutuda adres çıkar:

### 🌍 https://akblkmac47-wq.github.io/ekitap/

Telefondan, tabletten, akıllı tahtadan — herkes bu adresten açabilir.

---

## ADIM 3 — Sonradan değişiklik yaptığında

```bash
cd ~/Desktop/ekitap
git add .
git commit -m "guncelleme"
git push
```
Push'tan ~1 dakika sonra canlı site kendini yeniler.

---

## ADIM 4 — Ses ve görselleri ekleme (kredi gelince)

Şu an Gemini hesabının kredisi bitti (`429: prepayment credits are depleted`).
Kredi yüklediğinde: **https://aistudio.google.com/apikey** → faturalandırma

Sonra:
1. `baslat.command` dosyasına çift tıkla
2. Açılan sayfada **📂 Klasörü Seç ve Üretimi Başlat** → `ekitap` klasörünü seç
3. Bitince:

```bash
cd ~/Desktop/ekitap
git add ses gorseller
git commit -m "ses ve gorseller"
git push
```

> Ses ve görsel dosyaları **olmasa da site tam çalışır**:
> anlatım tarayıcının Türkçe sesiyle okunur, sahneler gömülü SVG çizimlerle görünür.

---

## ALTERNATİF — Git'siz yayın (Netlify Drop)

1. **https://app.netlify.com/drop**
2. `~/Desktop/ekitap` klasörünü tarayıcıya **sürükle-bırak**
3. 10 saniye içinde `https://rastgele-isim.netlify.app` adresi hazır

> Buraya da `.env` göndermemek için önce klasörden çıkar ya da masaüstüne taşı.

---

## 🔒 GÜVENLİK

- `.env` `.gitignore` içinde → push'a **girmiyor** (kontrol edildi ✅)
- API anahtarını sohbette paylaştın: iş bitince
  **https://aistudio.google.com/apikey** → eski anahtarı **sil**, yenisini üret,
  `~/Desktop/ekitap/.env` içine yaz.

---

## 🧹 Küçük temizlik

`~/Desktop/ekitap/_to_delete/` klasörünü Finder'dan silebilirsin (geçici git dosyaları).
