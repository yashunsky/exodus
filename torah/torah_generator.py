#! /usr/bin/env python2.7

from os import walk
from os.path import join

from PIL import Image  # pip install Pillow

PARTS_PATH = 'parts'
TORAH_TEMPLATE_PATH = 'torah_template.html'
OUTPUT = 'index.html'

PAGE_HEIGHT = 1725
PAGE_WIDTH = 1241

ANCHOR_TEMPLATE = '<td id="{page}">{page}<br><img alt="" src="1x1.png" style="width: {width}px"></td>'
MAIN_TEMPLATE = '<td colspan="{colspan}"><img alt="" src="{filename}" style="width: {width}px"></td>'
CONTENT_TEMPLATE = '<a href="#{page}">{page}</a>'

def main_row_segment(filename, width, height, pages_count):
    return MAIN_TEMPLATE.format(colspan = pages_count,
                                filename = filename,
                                width = width,
                                height = height)

def anchor_row_segment(width, pages_count, start_number):
    return ''.join([ANCHOR_TEMPLATE.format(width = width / pages_count, page = page)
                    for page in xrange(start_number, start_number + pages_count)])

def main():
    (_, _, filenames) = walk(PARTS_PATH).next()
    filenames = [join(PARTS_PATH, f)
                 for f in sorted(filenames) if f.endswith('.jpg')]

    page_number = 1
    main_row = ''
    anchor_row = ''
    content_table = ''

    for filename in filenames:
        img = Image.open(filename)
        (width, height) = img.size
        assert height == PAGE_HEIGHT

        pages_count = int(round(float(width) / PAGE_WIDTH))

        if pages_count == 9:
            pages_count = 10  # hack for long tapes troubles

        main_row += main_row_segment(filename.replace('\\', '/'), width, height, pages_count)
        anchor_row += anchor_row_segment(width, pages_count, page_number)
        page_number += pages_count

    content_table = ' &nbsp;'.join([CONTENT_TEMPLATE.format(page = page)
                             for page in xrange(1, page_number)])

    with open(TORAH_TEMPLATE_PATH, 'r') as f:
        template = f.read()

    with open(OUTPUT, 'w') as f:
        f.write(template.replace('{anchor_row}', anchor_row)
                        .replace('{main_row}', main_row)
                        .replace('{content_table}', content_table))

if __name__ == '__main__':
    main()
