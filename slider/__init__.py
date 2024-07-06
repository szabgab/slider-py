import argparse
import json
import os

from .parser import MultiSlider, Slider, SliderError
from .html import HTML, Book, OnePage


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
    parser.add_argument("--config", help="Name of the JSON config file of each course/book")
    parser.add_argument("--md", help="Name of an md file")
    parser.add_argument("--dir", help="Path to the HTML directory")
    parser.add_argument("--templates", help="Directory of the HTML templates")
    parser.add_argument("--static", help="Directory of the static files that will be copied to the html directory")
    parser.add_argument("--url", help="Canonical base-url", default="")
    parser.add_argument("--ext", help="File extension. Defaults to no extension.")

    args = parser.parse_args()

    if not args.parse and not args.html:
        parser.print_help()
        exit()

    if args.html and not args.dir:
        print("--dir was missing")
        parser.print_help()
        exit(1)
    if not args.config and not args.md:
        print("--md or --config is required")
        parser.print_help()
        exit(1)

    return args


def main():
    args = get_params()

    if args.config:
        multi_slider = MultiSlider()
        book = multi_slider.process_config(args.config)
    if args.md:
        slider = Slider()
        dom = slider.parse(args.md)

    if args.parse:
        if args.config:
            json_str = json.dumps(book, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)
        if args.md:
            json_str = json.dumps(dom, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)

        print(json_str)
        exit()

    if args.html:
        if args.config:
            #exit(args.url)
            html = Book(
                templates = args.templates,
                static    = args.static,
                url       = args.url,
                book      = book,
                includes  = os.path.dirname(args.config),
                ext       = args.ext,
            )
            html.generate_book(args.dir)
            exit()

        if args.md:
            html = OnePage(
                templates = args.templates,
                static    = args.static,
                chapter   = dom,
                includes  = os.path.dirname(args.md),
                ext       = args.ext,
            )
            html.generate_html_files(args.dir)
            exit()

