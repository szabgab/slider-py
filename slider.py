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

    # TODO: error when md file is missing
    with open(filename) as fh:
        for row in fh:
            match = re.search(r'# (.*)', row)
            if match:
            # TODO: error if duplicate chapter title in the same file
                if 'title' in chapter:
                    raise SliderError('Second chapter found in the same file in {}'.format(filename))
                chapter['title'] = match.group(1)
                continue

            # TODO: error if something follows a Chapter title that is not an id - probably not needed
            # TODO: error if there are duplicate chapter ids
            match = re.search(r'id: ([a-z-]+)', row)
            if match:
                chapter['id'] = match.group(1)
                continue

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