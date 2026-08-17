#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════
 SANAT ORMANI'NIN SIRRI — Gemini üretim aracı
 · SESLENDİRME : Gemini TTS (gemini-2.5-flash-preview-tts) → ses/s01..s19
 · GÖRSELLER   : Gemini Image (gemini-2.5-flash-image)     → gorseller/*.png
═══════════════════════════════════════════════════════════════════════════
KULLANIM
  python3 uret.py              # ses + görsel, hepsi
  python3 uret.py --sadece ses
  python3 uret.py --sadece gorsel
  python3 uret.py --yenile     # var olan dosyaların üzerine yaz
  python3 uret.py --env /baska/yol/.env

Anlatım metinleri index.html içindeki data-ses özniteliklerinden OKUNUR —
metni HTML'de değiştirirsen ses de otomatik olarak ona göre üretilir.

Gereksinim: pip3 install requests     (ffmpeg varsa mp3, yoksa wav üretilir)
═══════════════════════════════════════════════════════════════════════════
"""
import os, sys, re, json, time, base64, wave, shutil, argparse, subprocess

try:
    import requests
except ImportError:
    sys.exit("Önce şunu çalıştır:  pip3 install requests")

KOK        = "https://generativelanguage.googleapis.com/v1beta/models"
MODEL_TTS  = "gemini-2.5-flash-preview-tts"
MODEL_IMG  = "gemini-2.5-flash-image"
IMG_YEDEK  = ["gemini-2.5-flash-image-preview", "gemini-2.0-flash-preview-image-generation"]
BURASI     = os.path.dirname(os.path.abspath(__file__))
SES_KLASOR = os.path.join(BURASI, "ses")
IMG_KLASOR = os.path.join(BURASI, "gorseller")
HTML       = os.path.join(BURASI, "index.html")

# ─────────────────────────── SES AYARLARI ───────────────────────────
# Google TTS ön tanımlı sesleri: Kore, Puck, Zephyr, Charon, Fenrir, Aoede,
# Leda, Orus, Callirrhoe, Enceladus, Iapetus, Umbriel, Algieba, Despina ...
ANLATICI_SES = "Aoede"      # sıcak, neşeli kadın hikâye anlatıcısı
STIL_YONERGE = (
    "Bir ilkokul 1. sınıf öğrencisine masal anlatan sıcak, neşeli ve şefkatli "
    "bir anlatıcı gibi, net bir Türkçe telaffuzla, biraz yavaş ve tane tane, "
    "cümle sonlarında kısa duraklar vererek, meraklandırıcı bir tonla oku:\n\n"
)

# ────────────────────── GÖRSEL: KARAKTER + STİL ──────────────────────
DENIZ = (
    "DENIZ, a cheerful 7-year-old Turkish first-grade child: round friendly face, warm light skin, "
    "big dark eyes, rosy cheeks, short wavy dark-brown hair, wearing a yellow t-shirt under blue denim "
    "dungarees (overalls) with two yellow buttons, and red sneakers. Always exactly the same character."
)
FIRCACAN = (
    "FIRCACAN, a friendly talking magic paintbrush character: warm orange wooden handle, silver ferrule, "
    "bright blue bristles, with two big cartoon eyes and a small smile on the handle, tiny golden sparkles around it."
)
STIL = (
    " Style: flat vector children's picture-book illustration, thick soft dark-brown outlines, rounded friendly "
    "shapes, limited palette of coral red #FF5A4E, sunny yellow #FFD34E, mint green #22D3A5, sky blue #3FA9F5, "
    "violet #A66BFF on a warm cream background #FFF8EC. Simple and uncluttered, NO text, NO letters, NO numbers "
    "anywhere in the image, no watermark, safe and cheerful for 6-7 year olds. "
    "Wide 16:9 composition with generous empty space on one side for text."
)

KARAKTER_SAYFASI = (
    "Character reference sheet on a plain cream background, three views side by side: "
    f"(1) {DENIZ} standing and smiling, front view. (2) the same child in three-quarter view, waving. "
    f"(3) {FIRCACAN} floating next to the child." + STIL
)

GORSELLER = [
 ("01_kapak",
  f"Storybook cover illustration. {DENIZ} stands smiling in the centre with arms slightly open. "
  f"{FIRCACAN} floats beside the child. Around them float a red straight line, a blue wavy line, a yellow "
  "zigzag, a purple circle, a green triangle and a rainbow arc, like a burst of art magic. "
  "A big soft pale-yellow glow behind them." + STIL),

 ("02_bahce",
  f"{DENIZ} kneels under a big green tree in a sunny school garden and picks up an old paintbrush from the grass. "
  f"The paintbrush is {FIRCACAN} — its eyes are just opening, tiny golden sparkles around it. "
  "A simple school building with a red roof in the background." + STIL),

 ("03_kapi",
  f"A completely COLOURLESS, grey and faded forest — grey trees, pale drooping flowers, washed-out sky. "
  f"In the middle stands a glowing magic doorway with a bright violet frame and warm yellow light pouring out — "
  f"the only colour in the whole picture. {DENIZ} stands in front of the doorway, seen from behind-side, "
  f"with {FIRCACAN} floating beside. Melancholic but hopeful mood." + STIL),

 ("04_harita",
  "A cute hand-drawn treasure map of a magic art forest on aged cream paper, with a dashed violet path winding "
  "between four stops: a blue winding river, tall geometric purple rock formations, a three-coloured waterfall "
  "(red, yellow, blue), and a dark cave entrance. Small trees and hills around. Top-down storybook map view. "
  "NO text or labels anywhere." + STIL),

 ("05_nehir",
  f"A wide blue river whose surface is made of drawn LINES: a straight line, a wavy line, a zigzag line and a "
  f"curly line, each in a different colour, floating on the water. A friendly long light-blue water snake with "
  f"big eyes (the guardian KIVRIM) rises smoothly from the water in a wavy S shape. {DENIZ} stands on the bank "
  f"looking at it with wonder, {FIRCACAN} floating nearby." + STIL),

 ("06_cizgiler",
  "Four huge thick coloured lines floating separately on a plain cream background, clearly separated and stacked: "
  "a straight red line, a blue wavy line, a yellow zigzag line and a purple curly line. Flashcard style, no people, "
  "no text." + STIL),

 ("08_kayalik",
  f"Tall purple rock formations shaped like perfect geometric solids — cubes, pyramids, cylinders and spheres — "
  f"stacked into cliffs. On top perches KOSE, a friendly owl whose whole body is built from geometric shapes: "
  f"a triangle head, a square body, two big circular eyes, a yellow triangular beak. {DENIZ} stands below looking up." + STIL),

 ("09_sekiller",
  "Eight items arranged in two clearly separated rows on a plain cream background: top row a basketball, a slice of "
  "pizza, a wooden door and a square window; bottom row a large yellow circle, a red triangle, a blue rectangle and "
  "a green square. Flashcard style, no people, no text." + STIL),

 ("11_selale",
  f"A magical waterfall with three separate falls of paint — bright red, bright yellow and bright blue — pouring into "
  f"a pool below where they mix into orange, green and purple swirls. EBRU, a friendly butterfly whose four wings are "
  f"red, yellow, purple and green, flies above the pool. {DENIZ} stands at the edge, delighted." + STIL),

 ("12_renkler",
  "Three horizontal rows on a plain cream background; each row shows two big round paint blobs and an empty white "
  "circle after them: row one red and yellow, row two yellow and blue, row three red and blue. "
  "Clean, simple, no people, no text, no symbols." + STIL),

 ("14_magara",
  f"Inside a cosy cave with glowing crystals on the walls. Along the cave floor lie four objects with strongly "
  f"exaggerated surfaces: a rough grey stone, a soft yellow sponge, a smooth shiny glass pane and a green leaf with "
  f"visible veins. PUTUR, a small friendly brown hedgehog with soft spines, stands among them. {DENIZ} kneels and "
  f"reaches out a hand to touch." + STIL),

 ("15_dokular",
  "Five large texture swatch cards in a row on a plain cream background: a rough grey stone surface, a soft yellow "
  "sponge, a smooth clear glass with a highlight, a green leaf with veins, and a pink woven fabric. Each swatch "
  "clearly separated, flashcard style, no people, no text." + STIL),

 ("16_galeri",
  f"A small bright forest art gallery: four children's paintings hang in simple wooden frames on a light wall — "
  f"one of joyful colourful circles, one calm in soft blues, one energetic with bold zigzags on dark background, "
  f"and one earthy with layered rough textures. {DENIZ} stands looking at them thoughtfully, {FIRCACAN} floating beside." + STIL),

 ("17_tuval",
  f"{DENIZ} stands happily in front of a wooden easel, holding a palette, with {FIRCACAN} in the other hand. "
  "On the white canvas the child has painted a straight line, a wavy line, a yellow circle, a green square and a "
  "purple triangle. Bright and encouraging mood." + STIL),

 ("19_final",
  f"The magic forest has burst back into full colour: lush green trees, bright flowers, a huge rainbow arc across "
  f"the sky, wavy lines in the grass, triangular treetops, circular clouds. {DENIZ} stands in the middle with arms "
  f"raised in joy, {FIRCACAN} spinning happily above. Warm golden light, celebratory." + STIL),
]


# ═══════════════════════════ YARDIMCILAR ═══════════════════════════
def anahtar_bul(env_yolu=None):
    adaylar = ["GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_GENAI_API_KEY",
               "NEXT_PUBLIC_GEMINI_API_KEY", "VITE_GEMINI_API_KEY", "API_KEY"]
    for a in adaylar:
        if os.environ.get(a):
            return os.environ[a].strip()
    yollar = [env_yolu] if env_yolu else []
    yollar += [os.path.join(BURASI, x) for x in (".env", ".env.local")]
    yollar += [os.path.join(os.path.expanduser("~"), x) for x in (".env",)]
    for y in yollar:
        if y and os.path.isfile(y):
            for satir in open(y, encoding="utf-8", errors="ignore"):
                m = re.match(r'\s*(?:export\s+)?([A-Za-z0-9_]+)\s*=\s*["\']?([^"\'\s#]+)', satir)
                if m and m.group(1).upper() in adaylar:
                    print(f"  🔑 Anahtar okundu: {m.group(1)}  ({y})")
                    return m.group(2).strip()
    return None


def metinleri_oku():
    """index.html içindeki data-ses metinlerini sırayla döndürür."""
    if not os.path.isfile(HTML):
        sys.exit("❌ index.html bulunamadı: " + HTML)
    ham = open(HTML, encoding="utf-8").read()
    bulunan = re.findall(r'<section class="sayfa[^"]*"\s+data-ses="([^"]*)"', ham)
    if not bulunan:
        bulunan = re.findall(r'data-ses="([^"]*)"', ham)
    coz = lambda s: (s.replace("&quot;", '"').replace("&amp;", "&")
                      .replace("&lt;", "<").replace("&gt;", ">").replace("&#39;", "'"))
    return [coz(b) for b in bulunan]


def pcm_wav_yaz(yol, pcm, hiz=24000):
    with wave.open(yol, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(hiz)
        w.writeframes(pcm)


def mp3_yap(wav_yol, mp3_yol):
    if not shutil.which("ffmpeg"):
        return False
    try:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav_yol,
                        "-codec:a", "libmp3lame", "-b:a", "64k", "-ar", "24000", "-ac", "1", mp3_yol],
                       check=True)
        return True
    except Exception:
        return False


def tts_uret(anahtar, metin):
    govde = {
        "contents": [{"parts": [{"text": STIL_YONERGE + metin}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": ANLATICI_SES}}},
        },
    }
    r = requests.post(f"{KOK}/{MODEL_TTS}:generateContent",
                      headers={"x-goog-api-key": anahtar, "Content-Type": "application/json"},
                      json=govde, timeout=240)
    if r.status_code != 200:
        raise RuntimeError(f"TTS HTTP {r.status_code}: {r.text[:280]}")
    for c in r.json().get("candidates", []):
        for p in c.get("content", {}).get("parts", []):
            d = p.get("inlineData") or p.get("inline_data")
            if d and d.get("data"):
                return base64.b64decode(d["data"])
    raise RuntimeError("TTS yanıtında ses yok: " + r.text[:280])


def img_uret(anahtar, prompt, referans=None):
    son_hata = None
    for model in [MODEL_IMG] + IMG_YEDEK:
        parcalar = []
        if referans:
            parcalar.append({"inline_data": {"mime_type": "image/png",
                                             "data": base64.b64encode(referans).decode()}})
        parcalar.append({"text": prompt})
        if referans:
            parcalar.append({"text": "Use the characters from the reference image EXACTLY as they are — "
                                     "same face, same hair, same clothes, same colours. Do not redesign them."})
        govde = {"contents": [{"role": "user", "parts": parcalar}],
                 "generationConfig": {"responseModalities": ["IMAGE", "TEXT"]}}
        try:
            r = requests.post(f"{KOK}/{model}:generateContent",
                              headers={"x-goog-api-key": anahtar, "Content-Type": "application/json"},
                              json=govde, timeout=240)
            if r.status_code != 200:
                son_hata = f"{model} HTTP {r.status_code}: {r.text[:200]}"; continue
            for c in r.json().get("candidates", []):
                for p in c.get("content", {}).get("parts", []):
                    d = p.get("inlineData") or p.get("inline_data")
                    if d and d.get("data"):
                        return base64.b64decode(d["data"])
            son_hata = f"{model}: yanıtta görsel yok"
        except Exception as e:
            son_hata = f"{model}: {e}"
    raise RuntimeError(son_hata or "bilinmeyen hata")


# ═══════════════════════════════ ANA ═══════════════════════════════
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--env")
    ap.add_argument("--sadece", choices=["ses", "gorsel"])
    ap.add_argument("--yenile", action="store_true")
    ap.add_argument("--sayfa", nargs="*", type=int, help="sadece bu sayfaların sesi")
    a = ap.parse_args()

    print("═" * 68)
    print("  SANAT ORMANI'NIN SIRRI — Gemini ses + görsel üretimi")
    print("═" * 68)

    anahtar = anahtar_bul(a.env)
    if not anahtar:
        sys.exit("❌ API anahtarı bulunamadı.\n"
                 "   Proje klasöründeki .env dosyasına şunu ekle:\n"
                 "   GEMINI_API_KEY=buraya_anahtarin")

    os.makedirs(SES_KLASOR, exist_ok=True)
    os.makedirs(IMG_KLASOR, exist_ok=True)
    ffmpeg_var = bool(shutil.which("ffmpeg"))
    print(f"  🎧 ffmpeg: {'var → mp3 üretilecek' if ffmpeg_var else 'yok → wav üretilecek (sorun değil)'}")

    # ───────────── SESLENDİRME ─────────────
    if a.sadece != "gorsel":
        metinler = metinleri_oku()
        print(f"\n🔊 SESLENDİRME — index.html içinde {len(metinler)} sayfa metni bulundu\n")
        for i, metin in enumerate(metinler, 1):
            if a.sayfa and i not in a.sayfa:
                continue
            ad  = f"s{i:02d}"
            mp3 = os.path.join(SES_KLASOR, ad + ".mp3")
            wav = os.path.join(SES_KLASOR, ad + ".wav")
            if not a.yenile and (os.path.exists(mp3) or os.path.exists(wav)):
                print(f"  [{i:02d}/{len(metinler)}] ⏭  zaten var")
                continue
            print(f"  [{i:02d}/{len(metinler)}] 🎙  {metin[:58]}…")
            for deneme in range(3):
                try:
                    pcm = tts_uret(anahtar, metin)
                    pcm_wav_yaz(wav, pcm)
                    if ffmpeg_var and mp3_yap(wav, mp3):
                        os.remove(wav)
                        print(f"              ✅ ses/{ad}.mp3  ({os.path.getsize(mp3)//1024} KB)")
                    else:
                        print(f"              ✅ ses/{ad}.wav  ({os.path.getsize(wav)//1024} KB)")
                    break
                except Exception as e:
                    print(f"              ⚠️  deneme {deneme+1}: {e}")
                    time.sleep(5 + deneme * 6)
            time.sleep(1.2)

    # ───────────── GÖRSELLER ─────────────
    if a.sadece != "ses":
        print(f"\n🖼  GÖRSELLER — {len(GORSELLER)} sahne\n")
        ref_yol = os.path.join(IMG_KLASOR, "00_karakterler.png")
        referans = None
        if os.path.exists(ref_yol) and not a.yenile:
            referans = open(ref_yol, "rb").read()
            print("  ♻️  Mevcut karakter sayfası kullanılıyor (karakter tutarlılığı).")
        else:
            print("  🎨 Karakter sayfası üretiliyor (Deniz + Fırçacan)…")
            try:
                referans = img_uret(anahtar, KARAKTER_SAYFASI)
                open(ref_yol, "wb").write(referans)
                print("      ✅ gorseller/00_karakterler.png")
            except Exception as e:
                print("      ⚠️  Karakter sayfası üretilemedi, referanssız devam:", e)

        for i, (ad, prompt) in enumerate(GORSELLER, 1):
            hedef = os.path.join(IMG_KLASOR, ad + ".png")
            if not a.yenile and os.path.exists(hedef):
                print(f"  [{i:02d}/{len(GORSELLER)}] ⏭  {ad}.png zaten var")
                continue
            print(f"  [{i:02d}/{len(GORSELLER)}] 🎨 {ad}")
            for deneme in range(3):
                try:
                    png = img_uret(anahtar, prompt, referans)
                    open(hedef, "wb").write(png)
                    print(f"              ✅ gorseller/{ad}.png  ({len(png)//1024} KB)")
                    break
                except Exception as e:
                    print(f"              ⚠️  deneme {deneme+1}: {e}")
                    time.sleep(5 + deneme * 6)
            time.sleep(1.5)

    print("\n🎉 Bitti!  Şimdi index.html dosyasını tarayıcıda aç.")
    print("   Sesler ses/ klasöründen, görseller gorseller/ klasöründen otomatik yüklenir.")
    print("   Yayınlamak için:  git add . && git commit -m 'ses ve gorseller' && git push\n")


if __name__ == "__main__":
    main()
