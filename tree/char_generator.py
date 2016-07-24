#! /usr/bin/env python2.7
# -*- coding: utf8 -*-

SOURCE = "source/timeline.tsv"
OUTPUT = "characters.tsv"


def split_cell(cell):
    if cell == '':
        return '', '', set()

    split = cell.split(':')
    if len(split) == 1:
        name_and_tribe = cell
        parents = []
    else:
        name_and_tribe = split[0]
        parents = split[1].split(u' и ')

    name, tribe = name_and_tribe.split(u' ', 1)

    return name, tribe, set(parents)


def save_character(characters, name, info):
    if name is None:
        return
    name = name.strip()
    name = name.replace(' (', '(').replace('(', ' (')
    if name not in characters or characters[name] is None:
        characters[name] = info

if __name__ == '__main__':
    characters = {}

    with open(SOURCE, 'r') as f:
        timeline = f.readlines()
    for line in timeline:
        line = line.decode('utf-8')
        line = line.replace('\r\n', '')
        cells = line.split('\t')
        if cells[0] == '':
            continue

        player_name = cells[0]

        character_name = None
        character_info = None
        for i, cell in enumerate(cells[1:]):
            if cell not in ['', '-']:
                save_character(characters, character_name, character_info)
                char_name, tribe, parents = split_cell(cell)

                character_name = '%s (%s)' % (char_name, player_name)
                character_info = {'tribe': tribe,
                                  'parents': parents,
                                  'start': i, 'stop': i}

                for parent in parents:
                    save_character(characters, parent, None)
            else:
                if character_info is not None:
                    character_info['stop'] = i # pylint: disable=E1136

        save_character(characters, character_name, character_info)

    names = sorted(characters.keys(), key=lambda name: name.split('(')[1])

    def write_character(name):
        info = characters[name]
        if info is None:
            return name
        parents = list(info['parents'] or []) + ['', '']
        return u'\t'.join([name, info['tribe'],
                           parents[0], parents[1],
                           str(info['start']), str(info['stop'])])

    data = u'\n'.join([write_character(name) for name in names])

    with open(OUTPUT, 'w') as f:
        f.write(data.encode('utf-8'))
