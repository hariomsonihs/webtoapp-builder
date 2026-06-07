#!/usr/bin/env python3
"""Generate a valid PNG icon using only stdlib - no Pillow needed"""
import struct, zlib, sys, os

def create_png(filename, size, bg_color=(102, 126, 234)):
    width = height = size
    r, g, b = bg_color

    # Build raw image data (RGB, 8-bit)
    raw_rows = b''
    for y in range(height):
        row = b'\x00'  # filter type: None
        for x in range(width):
            # Simple rounded rectangle icon effect
            cx, cy = width // 2, height // 2
            dx, dy = x - cx, y - cy
            dist = (dx * dx + dy * dy) ** 0.5
            radius = width * 0.4
            if dist < radius:
                # Inner lighter color
                row += bytes([min(255, r + 40), min(255, g + 40), min(255, b + 40)])
            else:
                row += bytes([r, g, b])
        raw_rows += row

    compressed = zlib.compress(raw_rows, 9)

    def make_chunk(chunk_type, data):
        chunk_len = struct.pack('>I', len(data))
        chunk_data = chunk_type + data
        crc = struct.pack('>I', zlib.crc32(chunk_data) & 0xffffffff)
        return chunk_len + chunk_data + crc

    # PNG signature
    png = b'\x89PNG\r\n\x1a\n'
    # IHDR chunk
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    png += make_chunk(b'IHDR', ihdr_data)
    # IDAT chunk
    png += make_chunk(b'IDAT', compressed)
    # IEND chunk
    png += make_chunk(b'IEND', b'')

    os.makedirs(os.path.dirname(filename), exist_ok=True) if os.path.dirname(filename) else None
    with open(filename, 'wb') as f:
        f.write(png)

if __name__ == '__main__':
    output = sys.argv[1] if len(sys.argv) > 1 else 'icon.png'
    size = int(sys.argv[2]) if len(sys.argv) > 2 else 192
    create_png(output, size)
    print(f'Generated valid PNG: {output} ({size}x{size})')
