#! /usr/bin/env python2.7
# -*- coding: utf8 -*-

import json

from random import random

from transliterate import translit


SOURCE = u"source/Исход 2016_ Персонажи - Sheet1.tsv"

TREE_TEMPLATE = "tree_template.html"

OUTPUT = "output/tree.html"

COORDS = "overwriteCoords.json"

TRIBES = {u'из колена Рувимова': 'Reuben',
          u'из колена Симеонова': 'Simeon',
          u'из колена Левия': 'Levi',
          u'из колена Иудина': 'Judah',
          u'из колена Данова': 'Dan',
          u'из колена Неффалимова': 'Naphtali',
          u'из колена Гадова': 'Gad',
          u'из колена Асирова': 'Asher',
          u'из колена Иссахарова': 'Issachar',
          u'из колена Завулонова': 'Zebulun',
          u'из колена Манассиина': 'Manasseh',
          u'из колена Ефремова': 'Ephraim',
          u'из колена Вениаминова': 'Benjamin'}

TRIBES_ORDER = ['Reuben', 'Simeon', 'Levi', 'Judah',
                'Dan', 'Naphtali', 'Gad', 'Asher',
                'Issachar', 'Zebulun', 'Manasseh',
                'Ephraim', 'Benjamin']

TRIBES_COLORS = {'Reuben': ['white', 'red'],
                 'Simeon': ['yellow', 'green'],
                 'Levi': ['black', 'red'],
                 'Judah': ['yellow', 'red'],
                 'Dan': ['blue', 'green'],
                 'Naphtali': ['yellow', 'blue'],
                 'Gad': ['white', 'black'],
                 'Asher': ['green', 'black'],
                 'Issachar': ['blue', 'white'],
                 'Zebulun': ['yellow', 'white'],
                 'Manasseh': ['black', 'blue'],
                 'Ephraim': ['black', 'yellow'],
                 'Benjamin': ['red', 'blue']}

GENDER = {u'М': 'male', u'Ж': 'female'}

AGES = ['I', 'II', 'III', 'IV', 'V', 'VI',
        'VII', 'VIII', 'IX', 'X', 'XI', 'XII']

CSS_TEMPLATE = ('   .{tribe} {{border-left-color: {color_1};' +
                ' border-top-color: {color_1};' +
                ' border-right-color: {color_2};' +
                ' border-bottom-color: {color_2}}}')

CHARACTER_TEMPLATE = u'  <div id="{id}" style="left: {x}px; top: {y}px" class="{classes}"><br>{name}</div>'

LINK_TEMPLATE = u'  <div id="{id}" style="left: {x}px; top: {y}px" class="link">&nbsp</div>'

WIDTH = 4000
HEIGHT = 4000

PRESCALE = 1


with open(COORDS, 'r') as f:
    presetCoords = json.load(f)


def get_coord(tribe, mean_age):

    if tribe is None:
        tribe_x = 0
    else:
        tribe_x = TRIBES_ORDER.index(tribe) + 1

    x_range = float(WIDTH) / (len(TRIBES_ORDER) + 1)
    x = x_range * (tribe_x + random()) + 32

    y_range = float(HEIGHT - 1000) / len(AGES)
    y = y_range * (mean_age + random() * 0) + 1000

    return int(x), int(y)


def to_id(text):
    return (translit(text, 'ru', reversed=True)
            .replace("'", "").replace('(', '')
            .replace(')', '').replace(' ', '')
            .replace('-', '').replace('?', 'Unknown'))


def get_ages(ages):
    if (ages[0] and ages[1]):
        ages = [int(a) for a in ages]
        min_age = ages[0]  # sum(ages) / 2
        if ages[0] < 0:
            ages[0] = 0
        return [AGES[a] for a in xrange(ages[0], ages[1] + 1)], min_age
    else:
        return [], 0


def parse_line(line):
    values = line.split('\t')

    id = to_id(values[0])
    name = values[0].split(' (')[0]

    nick = to_id(values[0].split(' (')[1][:-1])

    tribe = TRIBES.get(values[1], None)
    birth_tribe = TRIBES.get(values[2], None)
    gender = GENDER.get(values[3], None)

    parents = frozenset([to_id(v) for v in values[4:6] if v])

    ages, min_age = get_ages(values[6:8])

    classes = [nick, birth_tribe, gender] + ages

    classes = ['person'] + [c for c in classes if c is not None]

    classes = ' '.join(classes)

    name = values[0]

    if id in presetCoords['chars']:
        x, y = presetCoords['chars'][id][1:]

        x, y = x * PRESCALE, y * PRESCALE
    else:
        x, y = get_coord(tribe, min_age)

    return {'id': id, 'name': name, 'gender': gender, 'parents': parents,
            'classes': classes, 'x': x, 'y': y, 'tribe': tribe, 'age': min_age}

if __name__ == '__main__':
    with open(SOURCE, 'r') as f:
        lines = f.read().decode('utf-8').replace('\r', '').split('\n')

    css = [CSS_TEMPLATE.format(tribe=tribe, color_1=color_1, color_2=color_2)
           for tribe, (color_1, color_2) in TRIBES_COLORS.items()]

    characters = [parse_line(line) for line in lines[1:]]

    tribe_matrix = {}

    for age in xrange(-7, 12):
        for tribe in [None] + TRIBES_ORDER:
            tribe_matrix[age, tribe] = []

    for c in characters:
        tribe_matrix[c['age'], c['tribe']].append(c)

    tribes_width = [max([len(tribe_matrix[age, tribe])
                         for age in xrange(-7, 12)])
                    for tribe in [None] + TRIBES_ORDER]

    offsets = [sum(tribes_width[:i]) for i in xrange(len(tribes_width))]
    offsets = {key: value for key, value
               in zip([None] + TRIBES_ORDER, offsets)}

    tribes_width = {key: value for key, value
                    in zip([None] + TRIBES_ORDER, tribes_width)}

    char_width = 200
    char_height = 400

    for age in xrange(-7, 12):
        for tribe in [None] + TRIBES_ORDER:
            tribe_row = sorted(tribe_matrix[age, tribe],
                               key=lambda c: c['gender'])

            center_offset = 0.5 * (tribes_width[tribe] - len(tribe_row))

            offset = offsets[tribe] + center_offset

            for index, character in enumerate(tribe_row):
                if character['id'] not in presetCoords['chars']:
                    character['x'] = ((offset + index) * char_width +
                                      (char_width / 2))
                    character['y'] = (((age + 7) * char_height) +
                                      char_height / 2)

    WIDTH = (sum(tribes_width.values()) + 1) * char_width
    HEIGHT = 19 * char_height

    WIDTH, HEIGHT = WIDTH * PRESCALE, HEIGHT * PRESCALE

    WIDTH, HEIGHT = 3900, 3200

    characters = {c['id']: c for c in characters}

    characters_html = [CHARACTER_TEMPLATE.format(**c)
                       for c in characters.values()]

    links = set(character['parents'] for character in characters.values())

    links = links.union({frozenset(("MarijaTinde", "ElisejRingl")),
                         frozenset(("GabrielNastjaNikulshina",
                                    "HiramVerdalin"))})

    def get_link(link):
        id = '_'.join(sorted(link))
        if id in presetCoords['links']:
            x, y = presetCoords['links'][id][2:]

            x, y = x * PRESCALE, y * PRESCALE
        else:
            parents = [characters[l] for l in link]
            xs = [p['x'] for p in parents]
            ys = [p['y'] for p in parents]
            x = sum(xs) / len(xs)
            y = sum(ys) / len(ys)

            y = max(ys) + char_height * (0.5 if len(link) == 2 else 0.25)
        return {'id': id, 'x': x, 'y': y}

    links = [get_link(link) for link in links if link]

    links_html = [LINK_TEMPLATE.format(**link) for link in links]

    def get_links_js(data):
        return ['     %s: ["%s", "%s", %d, %d]' % (id, id.split('_')[0],
                                                   id.split('_')[-1],
                                                   value['x'], value['y'])
                for id, value in data.items()]

    def get_chars_js(data):
        return ['     %s: ["%s", %d, %d]' %
                (id, '_'.join(sorted(value['parents'])),
                 value['x'], value['y'])
                for id, value in data.items()]

    chars_js = u',\n'.join(get_chars_js(characters))
    links_js = u',\n'.join(get_links_js({l['id']: l for l in links}))

    with open(TREE_TEMPLATE, 'r') as t:
        template = unicode(t.read())
        text = template.format(width=WIDTH,
                               height=HEIGHT,
                               tribes=u'\n'.join(css),
                               chars_js=chars_js,
                               links_js=links_js,
                               characters=u'\n'.join(characters_html),
                               links=u'\n'.join(links_html))
        with open(OUTPUT, 'w') as o:
            o.write(text.encode('utf-8'))
