# Makes the menu photos in web/hr/ from the shop's HungerRush item photos in img/hungerrush/:
# name.jpg is 3:2 for the preview and the order sheet, name-s.jpg is a square thumbnail.
# A few HungerRush photos are upright; those sit whole on the site's near-black instead of being cropped.
import os
from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC, OUT = os.path.join(ROOT, "img", "hungerrush"), os.path.join(ROOT, "web", "hr")
W, H = 900, 600

for f in sorted(os.listdir(SRC)):
    if not f.endswith(".jpg"):
        continue
    im = Image.open(os.path.join(SRC, f)).convert("RGB")
    w, h = im.size
    if w / h >= 1.4:  # wide photo: crop to 3:2
        cw = h * 3 // 2
        big = im.crop(((w - cw) // 2, 0, (w + cw) // 2, h)).resize((W, H), Image.LANCZOS)
    else:  # upright or near-square: whole photo, centred on the site's near-black
        big = Image.new("RGB", (W, H), (17, 17, 17))
        s = min(W / w, H / h)
        fit = im.resize((round(w * s), round(h * s)), Image.LANCZOS)
        big.paste(fit, ((W - fit.width) // 2, (H - fit.height) // 2))
    big.filter(ImageFilter.UnsharpMask(radius=1.2, percent=60, threshold=2)).save(os.path.join(OUT, f), quality=84, optimize=True, progressive=True)
    side = min(w, h)
    im.crop(((w - side) // 2, (h - side) // 2, (w + side) // 2, (h + side) // 2)).resize((160, 160), Image.LANCZOS) \
      .save(os.path.join(OUT, f[:-4] + "-s.jpg"), quality=82, optimize=True)
    print(f, im.size)
