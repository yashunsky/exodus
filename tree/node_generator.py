#! /usr/bin/env python2.7
# -*- coding: utf8 -*-

from copy import copy

import json

from random import random

from transliterate import translit


SOURCE = u"source/Исход 2016_ Персонажи - Sheet1.tsv"

FILES = (("tree_template.html", "output/tree.html"),
         ("tree_template_ro.html", "output/tree_ro.html"))

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

AGES = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII']

CSS_TEMPLATE = ('   .{tribe} {{border-left-color: {color_1};' +
                ' border-top-color: {color_1};' +
                ' border-right-color: {color_2};' +
                ' border-bottom-color: {color_2}}}')

CHARACTER_TEMPLATE = u'   <div id="{id}" style="left: {x}px; top: {y}px" class="{classes}">{name}{torah}</div>'

TORAH_TEMPLATE = u'<a href="http://jolaf.jnm.ru/exodus/torah/#{page}"><img alt="[тора]" class="torah" src="images/torah.png"></a>'

LINK_TEMPLATE = u'   <div id="{id}" style="left: {x}px; top: {y}px" class="link">&nbsp;</div>'

WIDTH = 4000
HEIGHT = 4000

PRESCALE = 1

HTML_SCALE = 1


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
    if ages[0] and ages[1]:
        ages = [int(a) for a in ages]
        min_age = ages[0]  # sum(ages) / 2
        if ages[0] < 0:
            ages[0] = 0
        return [AGES[a] for a in xrange(ages[0], ages[1] + 1)], min_age
    else:
        return [], 0


def parse_line(line, add_char):
    values = line.split('\t')

    id = to_id(values[0])
    name = values[0].split(' (')[0]

    nick = to_id(values[0].split(' (')[1][:-1]) if id else ''

    tribe = TRIBES.get(values[1], None)
    birth_tribe = TRIBES.get(values[2], None)
    gender = GENDER.get(values[3], None)

    parents = frozenset([to_id(v) for v in values[4:6] if v])

    fosters = frozenset([to_id(v) for v in values[6:8]
                         if v and not v.startswith('#')])

    ages, min_age = get_ages(values[8:10])

    post = values[10]
    torah = values[11]

    torah = TORAH_TEMPLATE.format(page=torah) if torah.isdigit() else ''

    classes = [nick, birth_tribe, gender] + ages

    classes = ['person'] + [c for c in classes if c is not None]

    classes = ' '.join(classes) # pylint: disable=R0204

    def get_html_name():
        if '?' in name:
            return '&nbsp;?&nbsp;'
        elif 'X' in values[0]:
            return name
        elif not post:
            return values[0]
        else:
            return u'<a href="{href}">{name}</a>'.format(href=post,
                                                         name=values[0])

    name = get_html_name()

    if id in presetCoords['chars']:
        x, y = presetCoords['chars'][id][1:]

        x, y = x * PRESCALE, y * PRESCALE
    else:
        x, y = get_coord(tribe, min_age)

    if len(parents) == 1:
        id_p = list(parents)[0]
        id_c = id_p + 'C'
        add_char(id_c)
        parents = frozenset({id_p, id_c})

    return {'id': id, 'name': name, 'gender': gender,
            'parents': parents, 'fosters': fosters, 'post': post, 'torah': torah,
            'classes': classes, 'x': x, 'y': y, 'tribe': tribe, 'age': min_age}

if __name__ == '__main__':
    with open(SOURCE, 'r') as f:
        lines = f.read().decode('utf-8').replace('\r', '').split('\n')

    css = [CSS_TEMPLATE.format(tribe=tribe, color_1=color_1, color_2=color_2)
           for tribe, (color_1, color_2) in TRIBES_COLORS.items()]

    additional = set()

    characters = [parse_line(line, additional.add) for line in lines[1:]]

    childfree = [c for c in characters if c['id'] == '']

    characters = [c for c in characters if c['id']]

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

    WIDTH, HEIGHT = 4200, 3500

    characters = {c['id']: c for c in characters}

    for id_c in additional:
        original = characters[id_c[:-1]]
        couple = copy(original)
        couple['id'] = id_c
        couple['name'] = '&nbsp;?&nbsp;'
        couple['gender'] = 'female' if original['gender'] == 'male' else 'male'
        if id_c in presetCoords['chars']:
            couple['x'] = presetCoords['chars'][id_c][1] * PRESCALE
        else:
            couple['x'] = original['x'] + 100
        couple['parents'] = frozenset()
        couple['fosters'] = frozenset()
        couple['post'] = ''
        couple['classes'] = 'person %s %s' % (couple['gender'], couple['tribe'])

        characters[id_c] = couple

    characters_html = [CHARACTER_TEMPLATE.format(**c)
                       for c in characters.values()]

    links = set(character['parents'] for character in characters.values())

    links = links.union(set(c['parents'] for c in childfree))

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

            y = max(ys) + 32  # char_height * (0.5 if len(link) == 2 else 0.25)
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

    def get_fosters_js(data):
        characters = [value for value in data.values() if value['fosters']]
        result = []
        link_ids = [l['id'] for l in links]
        for c in characters:
            if len(c['fosters']) == 1:
                result.append('     ["%s", "c", "%s"]' % (c['id'], list(c['fosters'])[0]))
            else:
                link_id = '_'.join(sorted(c['fosters']))
                if link_id in link_ids:
                    result.append('     ["%s", "l", "%s"]' % (c['id'], link_id))
                else:
                    for f in c['fosters']:
                        result.append('     ["%s", "c", "%s"]' % (c['id'], f))
        return result

    chars_js = u',\n'.join(get_chars_js(characters))
    links_js = u',\n'.join(get_links_js({l['id']: l for l in links}))
    fosters_js = u',\n'.join(get_fosters_js(characters))

    for (template, output) in FILES:
        with open(template) as t:
            template = unicode(t.read())
            text = template.format(width=WIDTH,
                                   height=HEIGHT,
                                   scale=HTML_SCALE,
                                   tribes=u'\n'.join(css),
                                   chars_js=chars_js,
                                   links_js=links_js,
                                   fosters_js=fosters_js,
                                   characters=u'\n'.join(characters_html),
                                   links=u'\n'.join(links_html))
            with open(output, 'w') as o:
                o.write(text.encode('utf-8'))
