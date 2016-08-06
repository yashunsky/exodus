#! /usr/bin/env python2.7
# -*- coding: utf8 -*-

from os import walk
from os.path import join

from PIL import Image, ImageDraw, ImageFont  # pip install Pillow

from node_generator import TRIBES_COLORS
from node_generator import get_characters_and_links

import svgwrite

SVG = "output/tree.svg"

PATH = 'source/tiles'

WIDTH, HEIGHT = 9933, 7016  # A1 @ 300dpi

SCALE_X = float(WIDTH) / 4200
SCALE_Y = float(HEIGHT) / 3500

MARGIN = 5


def create_swg(characters, links):
    def to_swg_size(x, y):
        return x * SCALE_X, y * SCALE_Y

    dwg = svgwrite.Drawing(SVG, profile='tiny', size=(u'%dpx' % WIDTH,
                                                      u'%dpx' % HEIGHT))

    svg_links = svgwrite.container.Group()
    svg_chars = svgwrite.container.Group()
    svg_fosters = svgwrite.container.Group()
    svg_birthes = svgwrite.container.Group()
    for link in links:
        c1, c2 = (characters[key] for key in link['id'].split('_'))
        svg_links.add(dwg.polyline([to_swg_size(c1['x'], c1['y']),
                                    to_swg_size(link['x'], link['y']),
                                    to_swg_size(c2['x'], c2['y'])],
                                   stroke='red', fill='none'))

    links_dict = {link['id']: link for link in links}

    def add_foster_line(dwg, character, foster):
        svg_fosters.add(dwg.polyline([to_swg_size(foster['x'], foster['y']),
                                      to_swg_size(character['x'], character['y'])],
                                     stroke='blue', fill='none'))

    for character in characters.values():
        if character['parents']:
            link = links_dict['_'.join(sorted(character['parents']))]
            svg_birthes.add(dwg.polyline([to_swg_size(link['x'], link['y']),
                                          to_swg_size(character['x'], character['y'])],
                                         stroke='green', fill='none'))

        svg_chars.add(dwg.text(character['plain_text_name'],
                               insert=to_swg_size(character['x'], character['y']),
                               text_anchor='middle',
                               fill='black'))

        if character['fosters']:
            if len(character['fosters']) == 1:
                add_foster_line(dwg, character,
                                characters[list(character['fosters'])[0]])
            else:
                link_id = '_'.join(sorted(character['fosters']))
                if link_id in links_dict:
                    add_foster_line(dwg, character, links_dict[link_id])
                else:
                    for f in character['fosters']:
                        add_foster_line(dwg, character, characters[f])

    dwg.add(svg_links)
    dwg.add(svg_birthes)
    dwg.add(svg_fosters)
    dwg.add(svg_chars)
    dwg.save()


def create_pngs(characters):

    def get_name(filename):
        return filename.split('_', 2)[2].split('.')[0]

    (_, _, filenames) = walk(PATH).next()
    tiles = {get_name(f): Image.open(join(PATH, f))
             for f in sorted(filenames) if f.endswith('.png')}

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

        x = int(c['x'] * SCALE_X - tile_w / 2)
        y = int(c['y'] * SCALE_Y - tile_h / 2)

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

if __name__ == '__main__':
    characters, links = get_characters_and_links()

    create_swg(characters, links)
    create_pngs(characters)
