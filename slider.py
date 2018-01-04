import argparse
import re
from jinja2 import Environment, FileSystemLoader

class SliderError(Exception):
    pass

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Name of and md file")

    args = parser.parse_args()

    parse(args.file)

def parse(filename):
    chapter = {}
    chapter['pages'] = []
    page = {}

    # TODO: error when md file is missing
    with open(filename) as fh:
        for row in fh:
            row = row.rstrip('\n')
            match = re.search(r'\A# (.*)\Z', row)
            if match:
            # TODO: error if duplicate chapter title in the same file
                if 'title' in chapter:
                    raise SliderError('Second chapter found in the same file in {}'.format(filename))
                chapter['title'] = match.group(1)
                continue

            # TODO: error if something follows a Chapter title that is not an id - probably not needed
            # TODO: error if there are duplicate chapter ids
            match = re.search(r'\Aid: ([a-z0-9-]+)\Z', row)
            if match:
                if page:
                    if 'id' in page:
                        raise SliderError('Second page id found in the same file in {} in page {}'.format(filename), page)
                    page['id'] = match.group(1)
                else:
                    if 'id' in chapter:
                        raise SliderError('Second chapter id found in the same file in {}'.format(filename))
                    chapter['id'] = match.group(1)
                continue

            match = re.search(r'\A## (.*)\Z', row)
            if match:
                if page:
                    # TODO: check if page has a title, id etc
                    chapter['pages'].append(page)
                    page = {}
                page['title'] = match.group(1)
                continue

        if page:
            chapter['pages'].append(page)

    # TODO: error if id already exists anywhere in the slides (chapters, pages)



    if not 'title' in chapter:
        raise SliderError('Chapter title is missing in {}'.format(filename))

    if not 'id' in chapter:
        raise SliderError('Chapter id is missing in {}'.format(filename))

    return chapter

def generate_html(chapter):
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('chapter.html')
    html = template.render(
        title = chapter['title']
    )
    return [
        {
            'id'   : chapter['id'],
            'html' : html,
        }
    ]

if __name__ == '__main__':
    main()