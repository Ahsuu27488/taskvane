"""Generate assets/icon.ico (blue rounded square with a pulse line)."""
import os
from PIL import Image, ImageDraw

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "icon.ico")
S = 256
img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
d.rounded_rectangle((8, 8, S - 8, S - 8), radius=58, fill=(57, 135, 229))
pts = [(48, 140), (92, 140), (112, 84), (144, 184), (166, 118), (180, 140), (208, 140)]
d.line(pts, fill="white", width=22, joint="curve")
for p in (pts[0], pts[-1]):
    d.ellipse((p[0] - 11, p[1] - 11, p[0] + 11, p[1] + 11), fill="white")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
img.save(OUT, sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
img.save(os.path.join(os.path.dirname(OUT), "logo.png"))  # README / website
print("wrote", OUT)
