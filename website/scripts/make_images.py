"""Build website images from the app's real screenshots (docs/screenshots) and icon.
Run: python website/scripts/make_images.py
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SHOTS = os.path.join(ROOT, "docs", "screenshots")
PUB = os.path.join(ROOT, "website", "public")
OUT = os.path.join(PUB, "img")
os.makedirs(OUT, exist_ok=True)

# 1) screenshots -> webp at two widths (full window incl. title bar: it reads as a real app)
for name in ("overview", "performance", "processes", "sensors", "power"):
    im = Image.open(os.path.join(SHOTS, f"{name}.png")).convert("RGB")
    for w in (1600, 800):
        r = im if im.width == w else im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        r.save(os.path.join(OUT, f"{name}-{w}.webp"), "WEBP", quality=86, method=6)
    print("shot", name, im.size)

# 2) icon / logo
icon = Image.open(os.path.join(ROOT, "assets", "icon.ico"))
icon.size = (256, 256)
logo = icon.convert("RGBA")
logo.resize((192, 192), Image.LANCZOS).save(os.path.join(OUT, "logo-192.png"))
logo.resize((512, 512), Image.LANCZOS).save(os.path.join(OUT, "logo-512.png"))
logo.save(os.path.join(PUB, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])

# 3) Open Graph card 1200x630: headline left, real screenshot bleeding off the right edge
W, H = 1200, 630
fog, ink, slate = (238, 242, 246), (21, 34, 50), (79, 96, 115)
card = Image.new("RGB", (W, H), fog)
d = ImageDraw.Draw(card)


def font(names, size):
    for n in names:
        try:
            return ImageFont.truetype(n, size)
        except OSError:
            pass
    return ImageFont.load_default()


bold = font(["seguibl.ttf", "segoeuib.ttf", "arialbd.ttf"], 58)
reg = font(["segoeui.ttf", "arial.ttf"], 28)
brand = font(["segoeuib.ttf", "arialbd.ttf"], 34)

shot = Image.open(os.path.join(SHOTS, "overview.png")).convert("RGB")
shot = shot.resize((900, round(shot.height * 900 / shot.width)), Image.LANCZOS)
mask = Image.new("L", shot.size, 0)
ImageDraw.Draw(mask).rounded_rectangle((0, 0, shot.width, shot.height), 18, fill=255)
card.paste(shot, (560, 150), mask)

card.paste(logo.resize((64, 64), Image.LANCZOS), (64, 64), logo.resize((64, 64), Image.LANCZOS))
d.text((144, 74), "Taskvane", font=brand, fill=ink)
y = 190
for line in ("A better", "Task Manager", "for Windows 11"):
    d.text((64, y), line, font=bold, fill=ink)
    y += 70
d.text((64, y + 24), "Temperatures, power draw and usage", font=reg, fill=slate)
d.text((64, y + 62), "in one free, open-source app.", font=reg, fill=slate)
card.save(os.path.join(OUT, "og.png"), optimize=True)
print("og.png, logos, favicon written")

# 4) content-area crops for feature rows: drop the app's sidebar and title bar so text reads larger
for name in ("overview", "performance", "processes", "sensors", "power"):
    im = Image.open(os.path.join(SHOTS, f"{name}.png")).convert("RGB")
    c = im.crop((274, 38, im.width, im.height))
    for w in (1300, 700):
        r = c.resize((w, round(c.height * w / c.width)), Image.LANCZOS)
        r.save(os.path.join(OUT, f"{name}-crop-{w}.webp"), "WEBP", quality=88, method=6)
print("crops written", c.size)
