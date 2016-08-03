#! /usr/bin/env python2.7
# -*- coding: utf8 -*-

import json

from os import walk
from os.path import join

from PIL import Image, ImageDraw, ImageFont  # pip install Pillow

from node_generator import COORDS, TRIBES_COLORS
from node_generator import get_characters, add_couples


PATH = 'source/tiles'

SCALE = 1
WIDTH, HEIGHT = int(4200 * SCALE), int(3500 * SCALE)

MARGIN = 5

def get_name(filename):
    return filename.split('_', 2)[2].split('.')[0]

if __name__ == '__main__':
    (_, _, filenames) = walk(PATH).next()
    tiles = {get_name(f): Image.open(join(PATH, f))
             for f in sorted(filenames) if f.endswith('.png')}

    with open(COORDS, 'r') as f:
        presetCoords = json.load(f)

    characters, additional = get_characters()

    characters = {c['id']: c for c in characters if c['id']}

    add_couples(characters, additional)

    layers = []

    font = ImageFont.truetype("arial.ttf", 38)

    for c in characters.values():
        bg = tiles[c['gender']]
        if c['birth_tribe'] is not None:
            c1, c2 = TRIBES_COLORS[c['birth_tribe']]
            m1, m2 = tiles[c1 + '_'], tiles['_' + c2]
            markers = Image.alpha_composite(m1, m2)
            tile = Image.alpha_composite(bg, markers)
        else:
            tile = bg.copy()

        tile_w, tile_h = tile.size

        draw = ImageDraw.Draw(tile)
        lines = c['plain_text_name'].split(' ', 1)
        text = '\n'.join(lines)

        if len(lines) == 1:
            text_w, text_h = font.getsize(lines[0])
        else:
            l0w, l0h = font.getsize(lines[0])
            l1w, l1h = font.getsize(lines[1])

            text_w, text_h = max(l0w, l1w), l0h + l1h

        tx, ty = (tile_w - text_w) / 2, (tile_h - text_h) / 2

        draw.multiline_text((tx, ty),
                            text=text, align='center',
                            font=font, fill='black')

        x = int(c['x'] * SCALE - tile_w / 2)
        y = int(c['y'] * SCALE - tile_h / 2)

        if x < MARGIN:
            x = MARGIN
        if x > WIDTH - tile_w - MARGIN:
            x = WIDTH - tile_w - MARGIN
        if y < MARGIN:
            y = MARGIN
        if y > HEIGHT - tile_h - MARGIN:
            y = HEIGHT - tile_h - MARGIN

        layer_id = 0
        while True:
            if len(layers) == layer_id:
                layers.append(Image.new('RGBA', (WIDTH, HEIGHT)))

            destination = layers[layer_id]
            place = destination.crop((x - MARGIN, y - MARGIN,
                                      x + tile_w + MARGIN,
                                      y + tile_h + MARGIN))
            if place.getcolors(1) is None:
                layer_id += 1
            else:
                destination.paste(tile, (x, y))
                break

    for layer_id, layer in enumerate(layers):
        layer.save('output/big_tree_layer_%d.png' % layer_id, 'PNG')
