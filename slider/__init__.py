import argparse
import json
import os

from .parser import MultiSlider, Slider, SliderError
from .html import HTML


def get_params():
    '''
    Use cases:
    --parse --md cases/all.md
    --parse --md cases/all.md > cases/dom/all.json
    --html  --md cases/all.md --dir cases/html/all
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument("--parse", help="Create DOM of md file as JSON file", action='store_true')
    parser.add_argument("--html", help="Create HTML files", action='store_true')
    parser.add_argument("--yaml", help="Name of the yaml file")
    parser.add_argument("--md", help="Name of an md file")
    parser.add_argument("--dir", help="Path to the HTML directory")
    parser.add_argument("--templates", help="Directory of the HTML templates")
    parser.add_argument("--static", help="Directory of the static files that will be copied to the html directory")
    parser.add_argument("--ext", help="File extension. Defaults to no extension.")

    args = parser.parse_args()

    if not args.parse and not args.html:
        parser.print_help()
        exit()

    if args.html and not args.dir:
        print("--dir was missing")
        parser.print_help()
        exit(1)
    if not args.yaml and not args.md:
        print("--md or --yaml is required")
        parser.print_help()
        exit(1)

    return args


def main():
    args = get_params()

    if args.yaml:
        multi_slider = MultiSlider()
        book = multi_slider.process_yml(args.yaml)
    if args.md:
        slider = Slider()
        dom = slider.parse(args.md)

    if args.parse:
        if args.yaml:
            json_str = json.dumps(book, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)
        if args.md:
            json_str = json.dumps(dom, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)

        print(json_str)
        exit()

    if args.html:
        if args.yaml:
            html = HTML(
                templates = args.templates,
                static    = args.static,
                book      = book,
                includes  = os.path.dirname(args.yaml),
                ext       = args.ext,
            )
            html.generate_book(args.dir)
            exit()

        if args.md:
            html = HTML(
                templates = args.templates,
                static    = args.static,
                chapter   = dom,
                includes  = os.path.dirname(args.md),
                ext       = args.ext,
            )
            html.generate_html_files(args.dir)
            exit()

