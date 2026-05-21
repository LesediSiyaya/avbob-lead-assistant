"""
Generate placeholder PNG icons for the Chrome extension.
Uses Python stdlib only — no Pillow or other dependencies.
Run: python generate_icons.py
"""
import struct, zlib, os

def make_png(size: int, fill_rgb: tuple, circle_rgb: tuple) -> bytes:
    """Build a minimal valid PNG with a coloured background and inner circle."""
    r_bg, g_bg, b_bg = fill_rgb
    r_c,  g_c,  b_c  = circle_rgb
    cx = cy = size // 2
    radius = int(size * 0.42)

    rows = []
    for y in range(size):
        row = b'\x00'          # filter byte
        for x in range(size):
            dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            if dist <= radius:
                row += bytes([r_c, g_c, b_c])
            else:
                row += bytes([r_bg, g_bg, b_bg])
        rows.append(row)

    raw      = b''.join(rows)
    compress = zlib.compress(raw, 9)

    def chunk(name: bytes, data: bytes) -> bytes:
        body = name + data
        return struct.pack('>I', len(data)) + body + struct.pack('>I', zlib.crc32(body) & 0xFFFFFFFF)

    ihdr = struct.pack('>IIBBBBB', size, size, 8, 2, 0, 0, 0)

    return (
        b'\x89PNG\r\n\x1a\n'
        + chunk(b'IHDR', ihdr)
        + chunk(b'IDAT', compress)
        + chunk(b'IEND', b'')
    )

os.makedirs('extension/icons', exist_ok=True)

# AVBOB dark background + gold circle
BG   = (13, 17, 23)    # #0D1117
GOLD = (212, 175, 55)  # #D4AF37

for size in [16, 48, 128]:
    path = f'extension/icons/icon{size}.png'
    with open(path, 'wb') as f:
        f.write(make_png(size, BG, GOLD))
    print(f'✅  Created {path}  ({size}x{size})')

print('\nDone — icons ready in extension/icons/')
