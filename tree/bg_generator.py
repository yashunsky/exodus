#! /usr/bin/env python2.7
# -*- coding: utf8 -*-

from os import walk
from os.path import join

from PIL import Image, ImageDraw, ImageFont  # pip install Pillow

from node_generator import get_characters_and_links

import svgwrite

import math

from random import random, seed

SVG = "output/tree.svg"

PATH = 'source/tiles'

THREADS = "A1/threads/"
TILES = "A1/tiles/"

WIDTH, HEIGHT = 9933, 7016  # A1 @ 300dpi

OFFSET_Y = 220

SCALE_X = float(WIDTH) / 4200
SCALE_Y = float(HEIGHT - OFFSET_Y) / 3500

MARGIN = 5

XPLUS = 83
YPLUS = -38


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
        return filename.split('.')[0]

    (_, _, filenames) = walk(PATH).next()
    tiles = {get_name(f): Image.open(join(PATH, f))
             for f in sorted(filenames) if f.endswith('.png')}

    layers = []

    font_c = ImageFont.truetype("agatha-modern.ttf", 78)
    font_m = ImageFont.truetype("agatha-modern.ttf", 50)
    font_p = ImageFont.truetype("agatha-modern.ttf", 38)

    for c in characters.values():
        key = c['gender']

        if c['birth_tribe'] is not None:
            key = c['birth_tribe'] + ' ' + key  # + ' 2'

        tile = tiles[key].copy()

        tile_w, tile_h = tile.size

        draw = ImageDraw.Draw(tile)
        lines = c['plain_text_name'].split(' ', 1)
        text = '\n'.join(lines)

        if len(lines) == 1:
            text_w, text_h = font_c.getsize(lines[0])
            tx, ty = (tile_w - text_w) / 2, (tile_h - text_h) / 2

            draw.text((tx, ty),
                      text=text, align='center',
                      font=font_c, fill='black')
        else:
            font_l0 = font_c

            l0w, l0h = font_c.getsize(lines[0])
            l1w, l1h = font_p.getsize(lines[1])

            if l0w > tile_w:
                font_l0 = font_m
                l0w, l0h = font_m.getsize(lines[0])

            w = max(l0w, l1w)

            margin = (tile_w - w) / 2

            draw.text((margin, 67 - (l0h / 2)),
                      text=lines[0], align='center',
                      font=font_l0, fill='black')

            draw.text((margin, 120 - (l1h / 2)),
                      text=lines[1], align='center',
                      font=font_p, fill='black')

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

        destination = Image.new('RGBA', (WIDTH, HEIGHT))
        destination.paste(tile, (x, y))
        destination.save('output/layers/%s.png' % c['id'], 'PNG')

    #     layer_id = 0
    #     while True:
    #         if len(layers) == layer_id:
    #             layers.append(Image.new('RGBA', (WIDTH, HEIGHT)))

    #         destination = layers[layer_id]
    #         place = destination.crop((x - MARGIN, y - MARGIN,
    #                                   x + tile_w + MARGIN,
    #                                   y + tile_h + MARGIN))
    #         if place.getcolors(1) is None:
    #             layer_id += 1
    #         else:
    #             destination.paste(tile, (x, y))
    #             break

    # for layer_id, layer in enumerate(layers):
    #     layer.save('output/layers/layer_%d.png' % layer_id, 'PNG')


class BgCreator(object):
    def __init__(self):
        super(BgCreator, self).__init__()
        self.threads_image = Image.new('RGBA', (WIDTH, HEIGHT))
        self.knots_image = Image.new('RGBA', (WIDTH, HEIGHT))

        self.tiles_image = Image.new('RGBA', (WIDTH, HEIGHT))

        self.text_image = Image.new('RGBA', (WIDTH, HEIGHT))

        self.markers_image = Image.new('RGBA', (WIDTH, HEIGHT))

        (_, _, filenames) = walk(THREADS).next()
        self.threads = {self.get_name(f): Image.open(join(THREADS, f))
                        for f in sorted(filenames) if f.endswith('.png')}

        (_, _, filenames) = walk(TILES).next()
        self.tiles = {self.get_name(f): Image.open(join(TILES, f))
                      for f in sorted(filenames) if f.endswith('.png')}

        self.max_length = 0

    def to_a1_size(self, x, y):
        return int(x * SCALE_X) + XPLUS, int(OFFSET_Y + y * SCALE_Y) + YPLUS

    def get_name(self, filename):
        return filename.split('.')[0]

    def place_thread(self, thread, source, dest):
        x1, y1 = source
        x2, y2 = dest

        if (y1 > y2):
            x1, y1 = dest
            x2, y2 = source

        dx, dy = x2 - x1, y2 - y1

        _, thread_h = thread.size

        lendth = int(math.sqrt(dx ** 2 + dy ** 2))

        if lendth > self.max_length:
            self.max_length = lendth
            print self.max_length

        inner_thread = thread.crop((0, 0, lendth, thread_h))

        angle = math.atan2(dy, dx) * 180 / math.pi

        adjust_angle = angle > 90

        angle = angle - 180 if adjust_angle else angle

        inner_thread = inner_thread.rotate(-angle, resample=Image.BICUBIC, expand=True)
        i_w, i_h = inner_thread.size

        w, h = abs(dx), abs(dy)

        if adjust_angle:
            point = (x2 + (w - i_w) / 2, y1 + (h - i_h) / 2)
        else:
            point = (x1 + (w - i_w) / 2, y1 + (h - i_h) / 2)

        layer = Image.new('RGBA', (WIDTH, HEIGHT))
        layer.paste(inner_thread, point)
        self.threads_image = Image.alpha_composite(layer, self.threads_image)

        # draw = ImageDraw.Draw(self.threads_image)
        # draw.ellipse((x1 - 20, y1 - 20, x1 + 20, y1 + 20), 'red')
        # draw.ellipse((x2 - 20, y2 - 20, x2 + 20, y2 + 20), 'blue')

        # font_p = ImageFont.truetype("agatha-modern.ttf", 38)

        # draw.text(source,
        #           text=str(angle), align='center',
        #           font=font_p, fill='black')

    def add_foster_line(self, character, foster):
        self.place_thread(self.threads['blue-thin'],
                          self.to_a1_size(foster['x'], foster['y']),
                          self.to_a1_size(character['x'], character['y']))

    def create_threads(self, characters, links):

        for link in links:
            c1, c2 = (characters[key] for key in link['id'].split('_'))

            if ('?' in c1['plain_text_name'] and
               '?' in c2['plain_text_name']):
                c1['x'] = link['x']
                c1['y'] = link['y']
                c2['x'] = link['x']
                c2['y'] = link['y']
            elif ('?' in c1['plain_text_name'] or
                  '?' in c2['plain_text_name']):
                x = c1['x'] if '?' not in c1['plain_text_name'] else c2['x']
                y = c1['y'] if '?' not in c1['plain_text_name'] else c2['y']
                c1['x'] = x
                c1['y'] = y
                c2['x'] = x
                c2['y'] = y
                link['x'] = x
                link['y'] = y

        for link in links:
            c1, c2 = (characters[key] for key in link['id'].split('_'))

            if not link['childfree']:
                k_w, k_h = self.threads['knot'].size

                x, y = self.to_a1_size(link['x'], link['y'])
                point = (x - k_w / 2, y - k_h / 2)
                self.knots_image.paste(self.threads['knot'], point)

            if ('?' not in c1['plain_text_name'] and
               '?' not in c2['plain_text_name']):

                if link['childfree']:
                    self.place_thread(self.threads['red'],
                                      self.to_a1_size(c1['x'], c1['y']),
                                      self.to_a1_size(c2['x'], c2['y']))
                else:

                    self.place_thread(self.threads['red'],
                                      self.to_a1_size(c1['x'], c1['y']),
                                      self.to_a1_size(link['x'], link['y']))

                    self.place_thread(self.threads['red'],
                                      self.to_a1_size(link['x'], link['y']),
                                      self.to_a1_size(c2['x'], c2['y']))

        links_dict = {link['id']: link for link in links}

        for character in characters.values():
            if character['parents']:
                link = links_dict['_'.join(sorted(character['parents']))]
                self.place_thread(self.threads['green-thin'],
                                  self.to_a1_size(link['x'], link['y']),
                                  self.to_a1_size(character['x'], character['y']))

            if character['fosters']:
                if len(character['fosters']) == 1:
                    self.add_foster_line(character,
                                         characters[list(character['fosters'])[0]])
                else:
                    link_id = '_'.join(sorted(character['fosters']))
                    if link_id in links_dict:
                        self.add_foster_line(character, links_dict[link_id])
                    else:
                        for f in character['fosters']:
                            self.add_foster_line(character, characters[f])

        self.threads_image = Image.alpha_composite(self.threads_image, self.knots_image)

        self.threads_image.save('A1/result/threads.png', 'PNG')

    def create_tiles(self, characters):
        font_c = ImageFont.truetype("agatha-modern.ttf", 78)
        font_p = ImageFont.truetype("agatha-modern.ttf", 38)

        draw = ImageDraw.Draw(self.text_image)

        max_tile_width = 0

        for c in characters.values():
            if '?' in c['plain_text_name']:
                continue

            key = c['gender']

            lines = c['plain_text_name'].split(' ', 1)

            if len(lines) == 1:
                w, _ = font_c.getsize(lines[0])
            else:
                lines[1] = lines[1][1:-1]
                l0w, l0h = font_c.getsize(lines[0])
                l1w, l1h = font_p.getsize(lines[1])

                w = max(l0w, l1w)

                if ((w + 80 - l1w) / 2) < 80:
                    w = 80 + l1w

            w += 80

            if w > max_tile_width:
                max_tile_width = w
                print w

            tw, h = self.tiles[key].size

            x, y = self.to_a1_size(c['x'], c['y'])

            x -= w / 2
            y -= h / 2

            offset = int((tw - w) * random())

            self.tiles_image.paste(self.tiles[key].crop((offset, 0, w + offset, h)), (x, y))

            if c['birth_tribe'] is not None:
                marker_image = self.tiles[c['birth_tribe']]

                self.markers_image.paste(marker_image, (x - 30, y + 99))

            if len(lines) == 1:
                text_w, text_h = font_c.getsize(lines[0])
                tx, ty = x + (w - text_w) / 2, y + (h - text_h) / 2

                draw.text((tx, ty),
                          text=lines[0], align='center',
                          font=font_c, fill='black')
            else:
                l0w, l0h = font_c.getsize(lines[0])
                l1w, l1h = font_p.getsize(lines[1])

                draw.text((x + ((w - l0w) / 2), y + 51 - (l0h / 2)),
                          text=lines[0], align='center',
                          font=font_c, fill='black')

                draw.text((x + ((w - l1w) / 2), y + 104 - (l1h / 2)),
                          text=lines[1], align='center',
                          font=font_p, fill='black')

        self.text_image.save('A1/result/texts.png', 'PNG')
        self.tiles_image.save('A1/result/tiles.png', 'PNG')
        self.markers_image.save('A1/result/markers.png', 'PNG')


if __name__ == '__main__':
    seed(3485723)

    from time import time
    start = time()
    characters, links = get_characters_and_links()

    # create_swg(characters, links)
    # create_pngs(characters)

    bgCreator = BgCreator()
    bgCreator.create_threads(characters, links)
    bgCreator.create_tiles(characters)
    stop = time()

    print 'done in', stop - start
