#! /usr/bin/env python2.7

from os import walk
from os.path import join

from PIL import Image  # pip install Pillow

PARTS_PATH = 'parts'
TORAH_HEMPLATE_PATH = 'torah_template.html'
OUTPUT = 'index.html'

PAGE_HEIGHT = 800
PAGE_WIDTH = 605

ANCHOR_HEIGHT = 10

MAIN_TEMPLATE = '<td colspan="{colspan}"><img src="{filename}" width="{width}" height="{height}"></td>'
ANCHOR_TEMPLATE = '<td align="center" width="{width}"><a name="{page}">{page}</a></td>'
CONTENT_TEMPLATE = ' <a href="#{page}">{page}</a> '


def main_row_segment(filename, width, height, pages_count):
    return MAIN_TEMPLATE.format(colspan=pages_count,
                                filename=filename,
                                width=width,
                                height=height)


def anchor_row_segment(width, pages_count, start_number):
    return ''.join([ANCHOR_TEMPLATE.format(width=width / pages_count, page=page) for page
                    in xrange(start_number, start_number + pages_count)])

if __name__ == '__main__':
    _, _, filenames = walk(PARTS_PATH).next()
    filenames = [join(PARTS_PATH, f)
                 for f in sorted(filenames) if f.endswith('.jpg')]

    page_number = 1
    main_row = ''
    anchor_row = ''
    content_table = ''

    for filename in filenames:
        img = Image.open(filename)
        width, height = img.size
        assert height == PAGE_HEIGHT

        pages_count = int(round(float(width) / PAGE_WIDTH))

        if pages_count == 9:
            pages_count = 10  # hack for long tapes troubles

        main_row += main_row_segment(filename, width, height, pages_count)
        anchor_row += anchor_row_segment(width, pages_count, page_number)
        page_number += pages_count

    content_table = ''.join([CONTENT_TEMPLATE.format(page=page)
                             for page in xrange(1, page_number)])

    torah_width = PAGE_WIDTH * 2
    torah_height = PAGE_HEIGHT + ANCHOR_HEIGHT * 2

    with open(TORAH_HEMPLATE_PATH, 'r') as t:
        template = t.read()
        with open(OUTPUT, 'w') as o:
            o.write(template.format(page_height=PAGE_HEIGHT,
                                    anchor_height=ANCHOR_HEIGHT,
                                    main_row=main_row,
                                    anchor_row=anchor_row,
                                    content_table=content_table))
