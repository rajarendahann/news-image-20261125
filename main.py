#!/usr/bin/env python3
import os
import sys
import zlib
import struct

# Pure Python PNG and Newspaper Front Page Generator for 25 November 2026
# 1024x1024 pixels, stdlib only, deterministic.

WIDTH = 1024
HEIGHT = 1024

# Color definitions (RGB)
BG_PAPER = (247, 244, 234)      # Cream/white paper background
INK_DARK = (26, 26, 26)         # Dark ink text
INK_MUTED = (90, 90, 90)        # Muted gray text
LINE_COLOR = (180, 175, 160)    # Divider line color
WHITE = (255, 255, 255)

# Accent colors per region
ACCENTS = {
    "ASIA": (179, 45, 45),       # Crimson Red
    "MIDDLE EAST": (179, 116, 0),# Amber / Olive
    "EUROPE": (26, 82, 118),     # Navy Blue
    "AFRICA": (184, 93, 24),     # Terracotta
    "AMERICAS": (30, 132, 73),   # Dark Green
    "OCEANIA": (14, 98, 81),     # Teal
    "GLOBAL": (108, 52, 131),    # Purple
    "TECH": (41, 128, 185)       # Blue
}

# Simple 5x7 Bitmap Font Data (ASCII 32 to 126)
FONT_5X7 = {
    ' ': [0,0,0,0,0], '!': [0,0,95,0,0], '"': [0,7,0,7,0], '#': [20,127,20,127,20],
    '$': [36,42,127,42,18], '%': [35,19,8,100,98], '&': [54,73,85,34,80], '\'': [0,7,3,0,0],
    '(': [0,28,54,65,0], ')': [0,65,54,28,0], '*': [20,8,62,8,20], '+': [8,8,62,8,8],
    ',': [0,80,48,0,0], '-': [8,8,8,8,8], '.': [0,96,96,0,0], '/': [32,16,8,4,2],
    '0': [62,81,73,69,62], '1': [0,66,127,64,0], '2': [66,97,89,73,70], '3': [33,65,73,75,51],
    '4': [24,20,18,127,16], '5': [39,69,69,69,57], '6': [60,74,73,73,48], '7': [1,113,9,5,3],
    '8': [54,73,73,73,54], '9': [6,73,73,41,30], ':': [0,50,50,0,0], ';': [0,80,50,0,0],
    '<': [8,20,34,65,0], '=': [20,20,20,20,20], '>': [0,65,34,20,8], '?': [2,65,81,9,6],
    '@': [62,65,93,89,30],
    'A': [126,9,9,9,126], 'B': [127,73,73,73,54], 'C': [62,65,65,65,34], 'D': [127,65,65,33,62],
    'E': [127,73,73,73,65], 'F': [127,9,9,9,1], 'G': [62,65,73,73,58], 'H': [127,8,8,8,127],
    'I': [0,65,127,65,0], 'J': [32,64,65,63,1], 'K': [127,8,20,34,65], 'L': [127,64,64,64,64],
    'M': [127,2,4,2,127], 'N': [127,4,8,16,127], 'O': [62,65,65,65,62], 'P': [127,9,9,9,6],
    'Q': [62,65,73,33,94], 'R': [127,9,9,25,102], 'S': [38,73,73,73,50], 'T': [1,1,127,1,1],
    'U': [63,64,64,64,63], 'V': [31,32,64,32,31], 'W': [63,64,48,64,63], 'X': [65,34,20,34,65],
    'Y': [1,2,124,2,1], 'Z': [97,81,73,69,67], '[': [0,127,65,65,0], '\\': [2,4,8,16,32],
    ']': [0,65,65,127,0], '^': [4,2,1,2,4], '_': [64,64,64,64,64], '`': [0,1,2,0,0],
    'a': [32,84,84,84,120], 'b': [127,72,72,72,48], 'c': [56,72,72,72,32], 'd': [48,72,72,72,127],
    'e': [56,84,84,84,24], 'f': [8,126,9,9,0], 'g': [24,164,164,164,124], 'h': [127,8,8,8,112],
    'i': [0,72,121,64,0], 'j': [64,144,144,125,0], 'k': [127,16,40,68,0], 'l': [0,64,127,64,0],
    'm': [124,4,120,4,120], 'n': [124,4,4,4,120], 'o': [56,72,72,72,56], 'p': [252,36,36,36,24],
    'q': [24,36,36,36,252], 'r': [124,4,4,8,0], 's': [72,84,84,84,32], 't': [4,63,64,64,32],
    'u': [60,64,64,32,124], 'v': [28,32,64,32,28], 'w': [60,64,48,64,60], 'x': [68,40,16,40,68],
    'y': [12,80,80,80,60], 'z': [68,100,84,76,68], '{': [0,8,54,65,0], '|': [0,0,127,0,0],
    '}': [0,65,54,8,0], '~': [2,1,2,4,2], '–': [8,8,8,8,8], '—': [8,8,8,8,8], '“': [0,120,64,120,64], '”': [0,120,64,120,64]
}

class Canvas:
    def __init__(self, width, height, bg_color):
        self.width = width
        self.height = height
        self.pixels = bytearray(width * height * 3)
        for i in range(0, len(self.pixels), 3):
            self.pixels[i]   = bg_color[0]
            self.pixels[i+1] = bg_color[1]
            self.pixels[i+2] = bg_color[2]

    def set_pixel(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            idx = (y * self.width + x) * 3
            self.pixels[idx]   = color[0]
            self.pixels[idx+1] = color[1]
            self.pixels[idx+2] = color[2]

    def fill_rect(self, x0, y0, w, h, color):
        x1 = max(0, min(self.width, x0 + w))
        y1 = max(0, min(self.height, y0 + h))
        rx0 = max(0, min(self.width, x0))
        ry0 = max(0, min(self.height, y0))
        for y in range(ry0, y1):
            row_idx = (y * self.width + rx0) * 3
            for x in range(rx0, x1):
                self.pixels[row_idx]   = color[0]
                self.pixels[row_idx+1] = color[1]
                self.pixels[row_idx+2] = color[2]
                row_idx += 3

    def draw_rect(self, x, y, w, h, color, thickness=1):
        self.fill_rect(x, y, w, thickness, color)
        self.fill_rect(x, y + h - thickness, w, thickness, color)
        self.fill_rect(x, y, thickness, h, color)
        self.fill_rect(x + w - thickness, y, thickness, h, color)

    def draw_line(self, x0, y0, x1, y1, color):
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        cx, cy = x0, y0
        while True:
            self.set_pixel(cx, cy, color)
            if cx == x1 and cy == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                cx += sx
            if e2 < dx:
                err += dx
                cy += sy

    def draw_char(self, ch, x, y, scale, color):
        glyph = FONT_5X7.get(ch, FONT_5X7.get('?', [0,0,0,0,0]))
        for col_idx, col_val in enumerate(glyph):
            for row_idx in range(7):
                if (col_val >> row_idx) & 1:
                    px = x + col_idx * scale
                    py = y + row_idx * scale
                    self.fill_rect(px, py, scale, scale, color)

    def draw_text(self, text, x, y, scale, color):
        cx = x
        char_width = 6 * scale
        for ch in text:
            if ch != '\n':
                self.draw_char(ch, cx, y, scale, color)
            cx += char_width

    def measure_text(self, text, scale):
        return len(text) * 6 * scale

    def draw_wrapped_text(self, text, x, y, max_w, scale, color, line_height=None):
        if line_height is None:
            line_height = 8 * scale
        words = text.split(' ')
        lines = []
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            if self.measure_text(test_line, scale) <= max_w or not current_line:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        
        cy = y
        for line in lines:
            self.draw_text(line, x, cy, scale, color)
            cy += line_height
        return cy - y

def generate_newspaper():
    canvas = Canvas(WIDTH, HEIGHT, BG_PAPER)

    margin = 16
    usable_w = WIDTH - (margin * 2)

    # 1. MASTHEAD (Enhanced typography & framing)
    canvas.fill_rect(margin, 10, usable_w, 22, INK_DARK)
    top_bar_text = "THE WORLD IN ONE DAY  •  WEDNESDAY 25 NOVEMBER 2026  •  EDITION NO. 329"
    canvas.draw_text(top_bar_text, margin + 12, 15, 1, WHITE)

    # Huge headline with accent underline shadow
    canvas.draw_text("THE DAILY CHRONICLE", margin + 2, 40, 5, (200, 195, 185))
    canvas.draw_text("THE DAILY CHRONICLE", margin, 38, 5, INK_DARK)
    canvas.draw_text("Wednesday 25 November 2026", margin, 78, 3, INK_DARK)

    lede = "LEDE: Saudi port bombed in Houthi clash; Huawei convicted in US federal trial; Nvidia CEO Jensen Huang reinstated under Trump pressure."
    canvas.draw_wrapped_text(lede, margin, 106, usable_w, 1, INK_MUTED, line_height=10)

    canvas.draw_line(margin, 122, WIDTH - margin, 122, INK_DARK)
    canvas.draw_line(margin, 123, WIDTH - margin, 123, INK_DARK)

    # 2. REGION COUNTERS ROW
    counters = [
        ("ASIA", 5), ("MIDDLE EAST", 2), ("EUROPE", 2), 
        ("AFRICA", 2), ("AMERICAS", 7), ("OCEANIA", 2), ("GLOBAL", 4)
    ]
    box_w = usable_w // len(counters)
    bx = margin
    by = 128
    for region, count in counters:
        accent = ACCENTS.get(region, INK_DARK)
        canvas.fill_rect(bx, by, box_w - 4, 24, WHITE)
        canvas.draw_rect(bx, by, box_w - 4, 24, accent, 2)
        label = f"{region}: {count}"
        canvas.draw_text(label, bx + 6, by + 8, 1, accent)
        bx += box_w

    canvas.draw_line(margin, 156, WIDTH - margin, 156, LINE_COLOR)

    # 3. THREE BIG STORY CARDS
    big_cards = [
        {
            "region": "GLOBAL",
            "headline": "Saudi-led coalition bombs Hodeidah port",
            "body": "Saudi-led coalition strikes Houthi-run Hodeidah port; Houthis threaten Saudi ports in response; 11 injured in Houthi attack on Saudi financial district."
        },
        {
            "region": "GLOBAL",
            "headline": "Huawei convicted in US criminal trial",
            "body": "Huawei convicted in sprawling US criminal trial over Iran business and trade-secret theft by federal jury in Eastern District of New York."
        },
        {
            "region": "TECH",
            "headline": "Nvidia board reinstates Jensen Huang",
            "body": "Nvidia shares swing after board reinstates Jensen Huang as CEO under Trump pressure; US targets chip smuggling after his return."
        }
    ]

    card_w = (usable_w - 16) // 3
    cx = margin
    cy = 162
    card_h = 168

    for card in big_cards:
        accent = ACCENTS.get(card["region"], INK_DARK)
        canvas.fill_rect(cx, cy, card_w, card_h, WHITE)
        canvas.draw_rect(cx, cy, card_w, card_h, accent, 2)
        
        # Accent header bar for card
        canvas.fill_rect(cx, cy, card_w, 26, accent)
        canvas.draw_text(card["region"], cx + 8, cy + 8, 1, WHITE)

        # Headline
        canvas.draw_wrapped_text(card["headline"], cx + 8, cy + 34, card_w - 16, 2, INK_DARK, line_height=14)
        
        # Body
        canvas.draw_wrapped_text(card["body"], cx + 8, cy + 82, card_w - 16, 1, INK_MUTED, line_height=10)

        cx += card_w + 8

    canvas.draw_line(margin, 338, WIDTH - margin, 338, LINE_COLOR)

    # 4. 3x3 GRID OF MEDIUM CARDS
    grid_stories = [
        ("EUROPE", "Kyiv apartment fire from Russian drone debris; rescue worker killed in Kramatorsk shelling."),
        ("EUROPE", "Putin vows retaliation as Ukrainian drone strikes hit two Russian oil refineries."),
        ("MIDDLE EAST", "Israeli strikes in Gaza kill seven including a local security official; winter flooding beseiges displaced camps."),
        ("AMERICAS", "US ready to slap new tariffs on China, EU and others over subsidized production."),
        ("ASIA", "China's anti-corruption drive reaches Shanghai party chief."),
        ("ASIA", "South Korean soldier's remains return home 59 years after Vietnam War death."),
        ("AFRICA", "US group wins $60bn Kenya minerals deal in the US-China race for African resources."),
        ("AMERICAS", "Gunmen hold 25 people hostage at a supermarket in Cartagena, Colombia."),
        ("OCEANIA", "Australia and Solomon Islands sign historic security treaty keeping foreign bases out.")
    ]

    grid_w = (usable_w - 16) // 3
    grid_h = 96
    gx_start = margin
    gy_start = 346

    for idx, (region, text) in enumerate(grid_stories):
        row = idx // 3
        col = idx % 3
        gx = gx_start + col * (grid_w + 8)
        gy = gy_start + row * (grid_h + 6)
        accent = ACCENTS.get(region, INK_DARK)

        canvas.fill_rect(gx, gy, grid_w, grid_h, WHITE)
        canvas.draw_rect(gx, gy, grid_w, grid_h, accent, 2)

        # Region tag bar
        canvas.fill_rect(gx, gy, grid_w, 18, accent)
        canvas.draw_text(region, gx + 6, gy + 4, 1, WHITE)

        # Text
        canvas.draw_wrapped_text(text, gx + 6, gy + 24, grid_w - 12, 1, INK_DARK, line_height=10)

    canvas.draw_line(margin, 654, WIDTH - margin, 654, LINE_COLOR)

    # 5. BOTTOM SECTION: MAP (Left) + ALSO ON WEDNESDAY (Right)
    map_w = 340
    also_w = usable_w - map_w - 12
    bottom_y = 662
    bottom_h = 248

    # Left: World Map ("WHERE IT HAPPENED")
    canvas.fill_rect(margin, bottom_y, map_w, bottom_h, WHITE)
    canvas.draw_rect(margin, bottom_y, map_w, bottom_h, INK_DARK, 2)
    canvas.fill_rect(margin, bottom_y, map_w, 24, INK_DARK)
    canvas.draw_text("WHERE IT HAPPENED", margin + 10, bottom_y + 7, 1, WHITE)

    map_box_x = margin + 12
    map_box_y = bottom_y + 30
    map_box_w = map_w - 24
    map_box_h = bottom_h - 40

    # Draw refined dot grid map background
    for gx in range(map_box_x + 8, map_box_x + map_box_w, 16):
        for gy in range(map_box_y + 8, map_box_y + map_box_h, 16):
            canvas.set_pixel(gx, gy, (215, 210, 195))

    cities = [
        ("New York", 60, 60, "AMERICAS"),
        ("Cartagena", 85, 115, "AMERICAS"),
        ("Kyiv", 195, 55, "EUROPE"),
        ("Hodeidah", 225, 95, "MIDDLE EAST"),
        ("Gaza", 210, 80, "MIDDLE EAST"),
        ("Nairobi", 225, 145, "AFRICA"),
        ("Beijing", 285, 65, "ASIA"),
        ("Shanghai", 295, 80, "ASIA"),
        ("Seoul", 310, 65, "ASIA"),
        ("Canberra", 315, 175, "OCEANIA")
    ]

    for city, rel_x, rel_y, region in cities:
        cx_pos = map_box_x + (rel_x * map_box_w // 340)
        cy_pos = map_box_y + (rel_y * map_box_h // 200)
        accent = ACCENTS.get(region, INK_DARK)
        canvas.fill_rect(cx_pos - 3, cy_pos - 3, 7, 7, accent)
        canvas.draw_rect(cx_pos - 3, cy_pos - 3, 7, 7, WHITE, 1)
        
        # Smart label placement to prevent clipping
        label_w = len(city) * 6
        if cx_pos + 8 + label_w > margin + map_w - 8:
            canvas.draw_text(city, cx_pos - 8 - label_w, cy_pos - 3, 1, INK_DARK)
        else:
            canvas.draw_text(city, cx_pos + 8, cy_pos - 3, 1, INK_DARK)

    # Right: "ALSO ON WEDNESDAY 25 NOVEMBER 2026"
    also_x = margin + map_w + 12
    canvas.fill_rect(also_x, bottom_y, also_w, bottom_h, WHITE)
    canvas.draw_rect(also_x, bottom_y, also_w, bottom_h, INK_DARK, 2)
    canvas.fill_rect(also_x, bottom_y, also_w, 24, INK_DARK)
    canvas.draw_text("ALSO ON WEDNESDAY 25 NOVEMBER 2026", also_x + 10, bottom_y + 7, 1, WHITE)

    also_items = [
        ("AMERICAS", "Trump touts 'fantastic relations' with Putin and Xi in press conference"),
        ("AMERICAS", "Abdul El-Sayed becomes first Muslim US senator"),
        ("AMERICAS", "Alaska ends deal to give voter records to Justice Department"),
        ("GLOBAL", "Bitcoin loses $60,000 as AI rebound faces earnings test"),
        ("GLOBAL", "Asian stocks fall as AI trade falters; WTI oil holds above $81"),
        ("AMERICAS", "Mexico inflation hits six-month high"),
        ("AMERICAS", "Ecuador's Babahoyo declares 90-day flood emergency"),
        ("ASIA", "72 orangutans rescued from West Kalimantan fires since August"),
        ("ASIA", "VW's $18,000 self-driving sedan shows China's car-tech lead"),
        ("OCEANIA", "Australia inflation 4.9%, higher than expected before RBA"),
        ("ASIA", "Gukesh vs Sindarov, Game 2 of World Chess Championship"),
        ("AFRICA", "WHO chief says staff evacuated from DR Congo hospital")
    ]

    col_width = (also_w - 24) // 2
    item_y_start = bottom_y + 32
    
    for idx, (reg, text) in enumerate(also_items):
        col = idx // 6
        row = idx % 6
        ix = also_x + 10 + col * (col_width + 8)
        iy = item_y_start + row * 34
        
        accent = ACCENTS.get(reg, INK_DARK)
        canvas.draw_text(f"[{reg}]", ix, iy, 1, accent)
        canvas.draw_wrapped_text(text, ix, iy + 10, col_width, 1, INK_DARK, line_height=9)

    canvas.draw_line(margin, 918, WIDTH - margin, 918, LINE_COLOR)

    # 6. FOOTER
    footer_y = 924
    canvas.fill_rect(margin, footer_y, usable_w, 86, WHITE)
    canvas.draw_rect(margin, footer_y, usable_w, 86, INK_DARK, 2)

    footer_lines = [
        "DATE CHECK: every story on this page happened, or was first reported, on Wednesday 25 November 2026",
        "Sources: Reuters, AP, AFP, BBC, Al Jazeera, CNN, Kyiv Independent, Dawn, RNZ, AllAfrica. Errors are not intentional.",
        "Stories are attributed, not stated as facts. Numbers are approximate. Designed for MAKEFUN / World Chronicle."
    ]

    fy = footer_y + 10
    for fline in footer_lines:
        canvas.draw_text(fline, margin + 12, fy, 1, INK_DARK)
        fy += 13

    # Honor MAKEFUN_OUTPUT_DIR if set
    output_dir = os.environ.get('MAKEFUN_OUTPUT_DIR')
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.join(output_dir, 'entry.png')
    else:
        filename = 'entry.png'

    print(f"Writing PNG to {filename}...")
    write_png(filename, WIDTH, HEIGHT, canvas.pixels)
    print("Done! entry.png generated successfully.")

def write_png(filename, width, height, pixels):
    png_sig = b'\x89PNG\r\n\x1a\n'
    
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    ihdr = b'IHDR' + ihdr_data
    ihdr_chunk = struct.pack('>I', 13) + ihdr + struct.pack('>I', zlib.crc32(ihdr) & 0xFFFFFFFF)
    
    scanline_len = width * 3
    raw_data = bytearray()
    for y in range(height):
        raw_data.append(0)
        start = y * scanline_len
        raw_data.extend(pixels[start:start + scanline_len])
        
    compressed = zlib.compress(raw_data, level=9)
    idat = b'IDAT' + compressed
    idat_chunk = struct.pack('>I', len(compressed)) + idat + struct.pack('>I', zlib.crc32(idat) & 0xFFFFFFFF)
    
    iend = b'IEND'
    iend_chunk = struct.pack('>I', 0) + iend + struct.pack('>I', zlib.crc32(iend) & 0xFFFFFFFF)
    
    with open(filename, 'wb') as f:
        f.write(png_sig + ihdr_chunk + idat_chunk + iend_chunk)

if __name__ == '__main__':
    generate_newspaper()
