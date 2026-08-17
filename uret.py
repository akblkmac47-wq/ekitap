#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════
 SANAT ORMANI'NIN SIRRI — yapay zekâ üretim aracı
 · GÖRSELLER   : Gemini Image  veya  OpenAI gpt-image-1   → gorseller/*.png
 · SESLENDİRME : Gemini TTS    veya  OpenAI TTS           → ses/s01..s19
═══════════════════════════════════════════════════════════════════════════
KULLANIM
  python3 uret.py                      # ses + görsel, hepsi
  python3 uret.py --sadece gorsel
  python3 uret.py --sadece ses
  python3 uret.py --saglayici openai   # zorla OpenAI kullan
  python3 uret.py --saglayici gemini   # zorla Gemini kullan
  python3 uret.py --yenile             # var olanların üzerine yaz
  python3 uret.py --sayfa 1 2 3        # sadece bu sayfaların sesi
  python3 uret.py --gorsel 01_kapak    # sadece bu görsel(ler)

ANAHTAR — proje klasöründeki .env dosyasına yaz (GitHub'a gitmez):
  OPENAI_API_KEY=sk-...          ← tavsiye (mp3 üretir, ffmpeg gerekmez)
  GEMINI_API_KEY=...             ← alternatif

Anlatım metinleri index.html içindeki data-ses özniteliklerinden OKUNUR —
metni HTML'de değiştirirsen ses de otomatik olarak ona göre üretilir.

Gereksinim: pip3 install requests
═══════════════════════════════════════════════════════════════════════════
"""
import os, sys, re, json, time, base64, wave, shutil, argparse, subprocess, html as _html

try:
    import requests
except ImportError:
    sys.exit("Önce şunu çalıştır:  pip3 install requests")

BURASI     = os.path.dirname(os.path.abspath(__file__))
SES_KLASOR = os.path.join(BURASI, "ses")
IMG_KLASOR = os.path.join(BURASI, "gorseller")
HTML       = os.path.join(BURASI, "index.html")

# ── Gemini ──
GKOK       = "https://generativelanguage.googleapis.com/v1beta/models"
G_IMG      = ["gemini-3-pro-image", "gemini-3.1-flash-image", "gemini-2.5-flash-image"]
G_TTS      = ["gemini-2.5-flash-preview-tts", "gemini-3.1-flash-tts-preview"]
G_SES      = "Aoede"          # sıcak, neşeli kadın anlatıcı

# ── OpenAI ──
OKOK       = "https://api.openai.com/v1"
O_IMG      = "gpt-image-1"
O_TTS      = "gpt-4o-mini-tts"
O_SES      = "shimmer"        # yumuşak, sıcak kadın sesi (alt: nova, coral, sage)

# ─────────────────────────── SES YÖNERGESİ ───────────────────────────
STIL_YONERGE = (
    "Bir ilkokul 1. sınıf öğrencisine masal anlatan sıcak, neşeli ve şefkatli "
    "bir anne gibi, net bir Türkçe telaffuzla, biraz yavaş ve tane tane, "
    "cümle sonlarında kısa duraklar vererek, meraklandırıcı bir tonla oku:\n\n"
)
# OpenAI'nin ayrı "instructions" alanı var — metnin içine karışmaz.
O_YONERGE = (
    "Türkçe. Altı-yedi yaşındaki bir çocuğa masal okuyan sıcak, şefkatli ve neşeli "
    "bir kadın anlatıcı ol. Tane tane, biraz yavaş konuş. Cümle sonlarında kısa dur. "
    "Karakterlerin repliklerinde sesini hafifçe renklendir. Telaffuz net ve doğal olsun."
)

# ══════════════════ GÖRSEL: KARAKTER + STİL ══════════════════
DENIZ = (
    "DENIZ, a cheerful 7-year-old Turkish first-grade girl: round friendly face, warm light skin, "
    "big dark expressive eyes with long lashes, rosy cheeks, small smile, medium-length wavy dark-brown "
    "hair with a small yellow bow clip on one side, wearing a bright yellow t-shirt under blue denim "
    "dungarees with two yellow buttons, white sneakers. Always exactly the same character in every image."
)
FIRCACAN = (
    "FIRCACAN, a friendly living magic paintbrush: warm orange wooden handle, silver ferrule, bright blue "
    "bristles, two big expressive cartoon eyes and a small happy smile on the handle, tiny golden sparkles "
    "floating around it. Always exactly the same character."
)
STIL = (
    " ART STYLE: warm, soft, richly detailed children's picture-book illustration in a polished digital "
    "painting style — smooth soft shading, gentle golden light, delicate rim light, cosy inviting atmosphere, "
    "lush detailed backgrounds full of small charming props, bright cheerful saturated colours with warm "
    "cream and pastel undertones. Storybook quality, clean and joyful, safe and friendly for 6-7 year olds. "
    "Absolutely NO text, NO letters, NO numbers, NO writing, NO labels, NO watermark anywhere in the image."
)
BOSLUK_SOL  = " Composition: the subject sits on the RIGHT side; leave the LEFT third soft and uncluttered for text."
BOSLUK_YOK  = " Composition: centred, evenly balanced, plain soft cream background."

KARAKTER_SAYFASI = (
    "Character reference sheet on a plain soft cream background, three views side by side: "
    f"(1) {DENIZ} standing and smiling, front view, full body. (2) the same girl in three-quarter view, waving. "
    f"(3) {FIRCACAN} floating on its own." + STIL
)

# 19 sayfanın tamamı — hikâye sayfaları + etkinlik sayfaları
GORSELLER = [
 ("01_kapak",
  f"Storybook cover illustration. {DENIZ} stands smiling in the centre with arms open in wonder. "
  f"{FIRCACAN} floats beside her leaving a trail of sparkles. Around them swirl a red straight line, a blue "
  "wavy line, a yellow zigzag, a purple circle, a green triangle and a big rainbow arc, like a burst of art "
  "magic. Behind her a lush enchanted forest glows with warm golden light and floating paint droplets."
  + STIL + " Composition: centred hero shot, magical and inviting."),

 ("02_bahce",
  f"{DENIZ} kneels on the grass under a big leafy tree in a sunny school garden and picks up an old paintbrush. "
  f"The paintbrush is {FIRCACAN} — its eyes are just opening, golden sparkles swirling around it. "
  "A cheerful school building with a red roof, flower beds, a bench and a ball in the background. "
  "Warm afternoon sunlight, dappled shadows through leaves." + STIL + BOSLUK_SOL),

 ("03_kapi",
  f"A completely COLOURLESS grey world — grey drooping trees, faded wilted flowers, washed-out pale sky, "
  f"everything desaturated like an old photograph. In the middle stands a glowing magic doorway with a bright "
  f"violet frame and warm golden light pouring out of it — the ONLY colour in the whole picture. {DENIZ} stands "
  f"before it seen from behind-side, {FIRCACAN} floating at her shoulder. Melancholic but hopeful." + STIL + BOSLUK_SOL),

 ("04_harita",
  "A charming hand-drawn treasure map of a magic art forest on aged cream parchment, gently curled edges. "
  "A dashed violet path winds between four illustrated stops: a blue winding river, tall geometric purple rock "
  "formations, a three-coloured waterfall (red, yellow, blue), and a dark glowing cave entrance. Tiny trees, "
  "hills, mushrooms and a compass rose around them. Top-down storybook map view." + STIL + BOSLUK_SOL),

 ("05_nehir",
  f"A wide sparkling blue river. A friendly long light-blue water snake with big kind eyes (the guardian KIVRIM) "
  f"rises gracefully from the water in a wavy S curve, smiling. On the water's surface float four glowing drawn "
  f"lines in different colours: straight, wavy, zigzag and curly. {DENIZ} stands on the mossy bank looking up in "
  f"wonder, {FIRCACAN} floating beside her. Lush riverside plants, dragonflies, warm light." + STIL + BOSLUK_SOL),

 ("06_cizgiler",
  "Four huge thick colourful lines floating separately on a plain soft cream background, clearly separated and "
  "stacked in four rows: a straight red line, a blue wavy line, a yellow zigzag line and a purple curly line. "
  "Each line is glossy and slightly three-dimensional with a soft shadow. Flashcard style, no people."
  + STIL + BOSLUK_YOK),

 ("07_esles_cizgi",
  "Four separate illustrated cards in a row on a soft cream background: (1) a railway track running straight to "
  "the horizon, (2) a calm sea with gentle rolling waves, (3) a dramatic yellow lightning bolt in a grey storm "
  "cloud, (4) a friendly green snake coiled in a curly spiral on grass. Each in its own rounded frame, clearly "
  "separated, bright and simple. No people." + STIL + BOSLUK_YOK),

 ("08_kayalik",
  f"Tall majestic purple rock formations shaped like perfect geometric solids — cubes, pyramids, cylinders and "
  f"spheres — stacked into dramatic cliffs against a warm sky. On top perches KOSE, a friendly wise owl whose "
  f"whole body is built from geometric shapes: a triangle head, a square body, two big circular eyes, a yellow "
  f"triangular beak. {DENIZ} stands below looking up in amazement, {FIRCACAN} beside her." + STIL + BOSLUK_SOL),

 ("09_sekiller",
  "Eight everyday objects arranged in two clearly separated rows on a plain soft cream background: top row a "
  "basketball, a slice of pizza, a wooden door, a square window; bottom row a large yellow circle, a red "
  "triangle, a blue rectangle, a green square. Each object glossy with a soft drop shadow, flashcard style, "
  "no people." + STIL + BOSLUK_YOK),

 ("10_say",
  f"KOSE the geometric owl proudly presents a big wooden easel on the forest floor. On the canvas is a simple "
  f"cheerful painted picture made only of shapes: a house from a square and a triangle roof, a round sun, three "
  f"circular clouds and two triangular trees. {DENIZ} stands beside pointing and counting on her fingers."
  + STIL + BOSLUK_SOL),

 ("11_selale",
  f"A magical waterfall with three separate falls of liquid paint — vivid red, sunny yellow and bright blue — "
  f"pouring down mossy rocks into a glowing pool below where they swirl together into orange, green and purple. "
  f"EBRU, a friendly butterfly with four wings coloured red, yellow, purple and green, flutters above the pool "
  f"trailing sparkles. {DENIZ} stands at the edge, delighted, {FIRCACAN} beside her." + STIL + BOSLUK_SOL),

 ("12_renkler",
  "Three horizontal rows on a plain soft cream background. Each row shows two big glossy round paint blobs, a "
  "plus sign made of paint, and an empty white outlined circle after them: row one red and yellow, row two "
  "yellow and blue, row three red and blue. Clean, simple, no people, no written characters."
  + STIL + BOSLUK_YOK),

 ("13_sicak_soguk",
  "A soft cream background split gently into two halves. The LEFT half is warm: a glowing sun, a cosy campfire "
  "and paint blobs in red, orange and yellow. The RIGHT half is cool: a calm blue sea wave, a snowy mountain "
  "and paint blobs in blue, turquoise and violet. Balanced, simple, no people." + STIL + BOSLUK_YOK),

 ("14_magara",
  f"Inside a cosy cave with softly glowing crystals on the walls casting gentle blue and violet light. Along the "
  f"sandy cave floor lie four objects with strongly exaggerated surface texture: a rough grey stone, a soft "
  f"yellow sponge, a smooth shiny glass pane, and a green leaf with visible veins. PUTUR, a small friendly brown "
  f"hedgehog with soft spines and a shy smile, stands among them. {DENIZ} kneels and reaches out to touch."
  + STIL + BOSLUK_SOL),

 ("15_dokular",
  "Five large square texture swatch cards in a row on a plain soft cream background, each in a rounded frame: "
  "a rough grey stone surface, a soft yellow sponge, smooth clear glass with a bright highlight, a green leaf "
  "with detailed veins, and pink woven fabric. Extreme close-up texture detail, clearly separated, no people."
  + STIL + BOSLUK_YOK),

 ("16_galeri",
  f"A bright cosy forest art gallery with wooden walls and warm spotlights. Four children's paintings hang in "
  f"simple wooden frames: one of joyful colourful circles, one calm in soft blues, one energetic with bold "
  f"zigzags on a dark background, one earthy with layered rough textures. {DENIZ} stands looking at them "
  f"thoughtfully with a hand on her chin, {FIRCACAN} floating beside her." + STIL + BOSLUK_SOL),

 ("17_tuval",
  f"{DENIZ} stands happily at a wooden easel in a sunny forest clearing, holding a wooden palette in one hand "
  f"and {FIRCACAN} in the other, mid-brushstroke. On the white canvas she has painted a red straight line, a "
  f"blue wavy line, a yellow circle, a green square and a purple triangle. Paint jars, brushes in a pot and "
  f"colourful splatters around her feet. Bright, encouraging, joyful." + STIL + BOSLUK_SOL),

 ("18_gunluk",
  f"A cosy scene on a wooden table seen slightly from above: an open notebook with blank cream pages, a pot of "
  f"colouring pencils, a watercolour paint set, a few pressed flowers and a small stack of finished drawings. "
  f"{DENIZ} sits at the table with her chin on her hand, smiling thoughtfully, {FIRCACAN} resting on the "
  "notebook. Warm lamp light. The notebook pages are completely blank." + STIL + BOSLUK_SOL),

 ("19_final",
  f"The magic forest bursts back into full glorious colour: lush green trees, bright blooming flowers, a huge "
  f"rainbow arc across a golden sky, wavy lines rippling through the grass, triangular treetops, round fluffy "
  f"clouds, butterflies and floating paint droplets everywhere. {DENIZ} stands in the middle with both arms "
  f"raised in pure joy, {FIRCACAN} spinning happily above her trailing sparkles. Warm celebratory golden light."
  + STIL + BOSLUK_SOL),
]

EN_BOY = {"01_kapak": ("4:3", "1024x1024")}     # diğerleri 16:9 / 1536x1024
def en_boy(ad, saglayici):
    g, o = EN_BOY.get(ad, ("16:9", "1536x1024"))
    return g if saglayici == "gemini" else o


# ═══════════════════════════ YARDIMCILAR ═══════════════════════════
def env_oku(env_yolu=None):
    """Ortam değişkenleri + .env dosyalarından anahtarları toplar."""
    bulunan = {}
    for ad in ("OPENAI_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_GENAI_API_KEY"):
        if os.environ.get(ad):
            bulunan[ad] = os.environ[ad].strip()
    yollar = ([env_yolu] if env_yolu else []) + [os.path.join(BURASI, x) for x in (".env", ".env.local")]
    for y in yollar:
        if y and os.path.isfile(y):
            for satir in open(y, encoding="utf-8", errors="ignore"):
                m = re.match(r'\s*(?:export\s+)?([A-Za-z0-9_]+)\s*=\s*["\']?([^"\'\s#]+)', satir)
                if m and m.group(1).upper() in ("OPENAI_API_KEY", "GEMINI_API_KEY",
                                                "GOOGLE_API_KEY", "GOOGLE_GENAI_API_KEY"):
                    bulunan.setdefault(m.group(1).upper(), m.group(2).strip())
    return bulunan


def saglayici_sec(anahtarlar, zorla=None):
    o = anahtarlar.get("OPENAI_API_KEY")
    g = (anahtarlar.get("GEMINI_API_KEY") or anahtarlar.get("GOOGLE_API_KEY")
         or anahtarlar.get("GOOGLE_GENAI_API_KEY"))
    if zorla == "openai":
        if not o: sys.exit("❌ .env içinde OPENAI_API_KEY yok.")
        return "openai", o
    if zorla == "gemini":
        if not g: sys.exit("❌ .env içinde GEMINI_API_KEY yok.")
        return "gemini", g
    if o: return "openai", o          # mp3 döndürdüğü için öncelikli
    if g: return "gemini", g
    sys.exit("❌ API anahtarı bulunamadı.\n"
             "   Proje klasöründeki .env dosyasına şunlardan birini ekle:\n"
             "     OPENAI_API_KEY=sk-...        (tavsiye)\n"
             "     GEMINI_API_KEY=...")


def metinleri_oku():
    if not os.path.isfile(HTML):
        sys.exit("❌ index.html bulunamadı: " + HTML)
    ham = open(HTML, encoding="utf-8").read()
    bulunan = re.findall(r'<section class="sayfa[^"]*"\s+data-ses="([^"]*)"', ham)
    if not bulunan:
        bulunan = re.findall(r'data-ses="([^"]*)"', ham)
    return [_html.unescape(b) for b in bulunan]


def pcm_wav_yaz(yol, pcm, hiz=24000):
    with wave.open(yol, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(hiz)
        w.writeframes(pcm)


def mp3_yap(wav_yol, mp3_yol):
    """Önce lameenc (saf python), yoksa ffmpeg dener. Başarılıysa True."""
    try:
        import lameenc
        with wave.open(wav_yol, "rb") as w:
            kanal, hiz, cerceve = w.getnchannels(), w.getframerate(), w.getnframes()
            pcm = w.readframes(cerceve)
        enc = lameenc.Encoder()
        enc.set_bit_rate(64)
        enc.set_in_sample_rate(hiz)
        enc.set_channels(kanal)
        enc.set_quality(2)
        veri = enc.encode(pcm) + enc.flush()
        open(mp3_yol, "wb").write(bytes(veri))
        return True
    except ImportError:
        pass
    except Exception:
        return False
    if not shutil.which("ffmpeg"):
        return False
    try:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav_yol,
                        "-codec:a", "libmp3lame", "-b:a", "64k", "-ar", "24000", "-ac", "1", mp3_yol],
                       check=True)
        return True
    except Exception:
        return False


# ─────────────────────────── SES ÜRETİMİ ───────────────────────────
def tts_openai(anahtar, metin):
    """mp3 bayt döndürür."""
    r = requests.post(f"{OKOK}/audio/speech",
                      headers={"Authorization": "Bearer " + anahtar, "Content-Type": "application/json"},
                      json={"model": O_TTS, "voice": O_SES, "input": metin,
                            "instructions": O_YONERGE, "response_format": "mp3", "speed": 0.95},
                      timeout=300)
    if r.status_code != 200:
        raise RuntimeError(f"OpenAI TTS HTTP {r.status_code}: {r.text[:280]}")
    return ("mp3", r.content)


def tts_gemini(anahtar, metin):
    """ham PCM döndürür."""
    govde = {"contents": [{"parts": [{"text": STIL_YONERGE + metin}]}],
             "generationConfig": {"responseModalities": ["AUDIO"],
                                  "speechConfig": {"voiceConfig":
                                      {"prebuiltVoiceConfig": {"voiceName": G_SES}}}}}
    son = None
    for model in G_TTS:
        r = requests.post(f"{GKOK}/{model}:generateContent",
                          headers={"x-goog-api-key": anahtar, "Content-Type": "application/json"},
                          json=govde, timeout=300)
        if r.status_code != 200:
            son = f"{model} HTTP {r.status_code}: {r.text[:220]}"; continue
        for c in r.json().get("candidates", []):
            for p in c.get("content", {}).get("parts", []):
                d = p.get("inlineData") or p.get("inline_data")
                if d and d.get("data"):
                    return ("pcm", base64.b64decode(d["data"]))
        son = f"{model}: yanıtta ses yok"
    raise RuntimeError(son or "TTS başarısız")


# ────────────────────────── GÖRSEL ÜRETİMİ ──────────────────────────
def img_openai(anahtar, prompt, boyut):
    r = requests.post(f"{OKOK}/images/generations",
                      headers={"Authorization": "Bearer " + anahtar, "Content-Type": "application/json"},
                      json={"model": O_IMG, "prompt": prompt, "size": boyut,
                            "quality": "high", "n": 1},
                      timeout=600)
    if r.status_code != 200:
        raise RuntimeError(f"OpenAI görsel HTTP {r.status_code}: {r.text[:280]}")
    d = r.json()["data"][0]
    if d.get("b64_json"):
        return base64.b64decode(d["b64_json"])
    return requests.get(d["url"], timeout=300).content


def img_gemini(anahtar, prompt, oran, referans=None):
    son = None
    for model in G_IMG:
        parcalar = []
        if referans:
            parcalar.append({"inline_data": {"mime_type": "image/png",
                                             "data": base64.b64encode(referans).decode()}})
        parcalar.append({"text": prompt})
        if referans:
            parcalar.append({"text": "Use the characters from the reference image EXACTLY as they are — "
                                     "same face, same hair, same clothes, same colours. Do not redesign them."})
        govde = {"contents": [{"role": "user", "parts": parcalar}],
                 "generationConfig": {"responseModalities": ["IMAGE"],
                                      "imageConfig": {"aspectRatio": oran}}}
        try:
            r = requests.post(f"{GKOK}/{model}:generateContent",
                              headers={"x-goog-api-key": anahtar, "Content-Type": "application/json"},
                              json=govde, timeout=600)
            if r.status_code != 200:
                son = f"{model} HTTP {r.status_code}: {r.text[:220]}"; continue
            for c in r.json().get("candidates", []):
                for p in c.get("content", {}).get("parts", []):
                    d = p.get("inlineData") or p.get("inline_data")
                    if d and d.get("data"):
                        return base64.b64decode(d["data"])
            son = f"{model}: yanıtta görsel yok"
        except Exception as e:
            son = f"{model}: {e}"
    raise RuntimeError(son or "görsel üretilemedi")


# ═══════════════════════════════ ANA ═══════════════════════════════
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--env")
    ap.add_argument("--saglayici", choices=["openai", "gemini"])
    ap.add_argument("--sadece", choices=["ses", "gorsel"])
    ap.add_argument("--yenile", action="store_true")
    ap.add_argument("--sayfa", nargs="*", type=int)
    ap.add_argument("--gorsel", nargs="*")
    a = ap.parse_args()

    print("═" * 70)
    print("  SANAT ORMANI'NIN SIRRI — yapay zekâ ses + görsel üretimi")
    print("═" * 70)

    anahtarlar = env_oku(a.env)
    saglayici, anahtar = saglayici_sec(anahtarlar, a.saglayici)
    print(f"  🔌 Sağlayıcı : {saglayici.upper()}")
    print(f"  🎙  Ses       : {O_SES if saglayici=='openai' else G_SES} (kadın anlatıcı)")
    print(f"  🎨 Görsel    : {O_IMG if saglayici=='openai' else G_IMG[0]}")

    os.makedirs(SES_KLASOR, exist_ok=True)
    os.makedirs(IMG_KLASOR, exist_ok=True)
    try:
        import lameenc; ffmpeg_var = True
    except ImportError:
        ffmpeg_var = bool(shutil.which("ffmpeg"))

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
            print(f"  [{i:02d}/{len(metinler)}] 🎙  {metin[:56]}…")
            for deneme in range(3):
                try:
                    if saglayici == "openai":
                        _, veri = tts_openai(anahtar, metin)
                        open(mp3, "wb").write(veri)
                        print(f"              ✅ ses/{ad}.mp3  ({len(veri)//1024} KB)")
                    else:
                        _, pcm = tts_gemini(anahtar, metin)
                        pcm_wav_yaz(wav, pcm)
                        if ffmpeg_var and mp3_yap(wav, mp3):
                            os.remove(wav)
                            print(f"              ✅ ses/{ad}.mp3  ({os.path.getsize(mp3)//1024} KB)")
                        else:
                            print(f"              ✅ ses/{ad}.wav  ({os.path.getsize(wav)//1024} KB)")
                    break
                except Exception as e:
                    print(f"              ⚠️  deneme {deneme+1}: {str(e)[:200]}")
                    time.sleep(5 + deneme * 6)
            time.sleep(1.0)

    # ───────────── GÖRSELLER ─────────────
    if a.sadece != "ses":
        secili = [(ad, p) for ad, p in GORSELLER if not a.gorsel or ad in a.gorsel]
        print(f"\n🖼  GÖRSELLER — {len(secili)} sahne\n")

        referans = None
        if saglayici == "gemini":
            ref_yol = os.path.join(IMG_KLASOR, "00_karakterler.png")
            if os.path.exists(ref_yol) and not a.yenile:
                referans = open(ref_yol, "rb").read()
                print("  ♻️  Mevcut karakter sayfası kullanılıyor (karakter tutarlılığı).")
            else:
                print("  🎨 Karakter sayfası üretiliyor (Deniz + Fırçacan)…")
                try:
                    referans = img_gemini(anahtar, KARAKTER_SAYFASI, "4:3")
                    open(ref_yol, "wb").write(referans)
                    print("      ✅ gorseller/00_karakterler.png")
                except Exception as e:
                    print("      ⚠️  Karakter sayfası üretilemedi, referanssız devam:", str(e)[:160])

        for i, (ad, prompt) in enumerate(secili, 1):
            hedef = os.path.join(IMG_KLASOR, ad + ".png")
            if not a.yenile and os.path.exists(hedef):
                print(f"  [{i:02d}/{len(secili)}] ⏭  {ad}.png zaten var")
                continue
            print(f"  [{i:02d}/{len(secili)}] 🎨 {ad}")
            for deneme in range(3):
                try:
                    if saglayici == "openai":
                        png = img_openai(anahtar, prompt, en_boy(ad, "openai"))
                    else:
                        png = img_gemini(anahtar, prompt, en_boy(ad, "gemini"), referans)
                    open(hedef, "wb").write(png)
                    print(f"              ✅ gorseller/{ad}.png  ({len(png)//1024} KB)")
                    break
                except Exception as e:
                    print(f"              ⚠️  deneme {deneme+1}: {str(e)[:200]}")
                    time.sleep(5 + deneme * 6)
            time.sleep(1.2)

    print("\n🎉 Bitti!  index.html dosyasını tarayıcıda aç.")
    print("   Yayınlamak için:  git add -A && git commit -m 'ses ve gorseller' && git push\n")


if __name__ == "__main__":
    main()
