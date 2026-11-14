"""Recolour a logo's dark text to white so it reads on footage. Usage: logo_white.py in.png out.png"""
import sys
import numpy as np
from PIL import Image
a = np.array(Image.open(sys.argv[1]).convert("RGBA")).astype(int)
dark = (a[..., :3].max(-1) < 90) & (a[..., 3] > 0)
a[dark, :3] = 255
Image.fromarray(a.astype("uint8")).save(sys.argv[2])
print(f"logo: {dark.sum()} dark pixels -> white")
