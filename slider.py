import argparse
import re

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Name of and md file")

    args = parser.parse_args()

    parse(args.file)

def parse(filename):
    chapter = {}
    with open(filename) as fh:
        for row in fh:
            match = re.search(r'# (.*)', row)
            if match:
            #    if 'title' in chapter
                chapter['title'] = match.group(1)
                continue

    return chapter



if __name__ == '__main__':
    main()