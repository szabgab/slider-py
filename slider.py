import argparse
import re

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
            #    if 'title' in chapter
                chapter['title'] = match.group(1)
                continue

            # TODO: error if something follows a Chapter title that is not an id
            # TODO: error if there are duplicate chapter ids
            # TODO: error if chapter id is missing
            match = re.search(r'id: ([a-z-]+)', row)
            if match:
                chapter['id'] = match.group(1)
                continue

    if not 'title' in chapter:
        raise SliderError('Chapter title is missing from {}'.format(filename))

    return chapter


if __name__ == '__main__':
    main()