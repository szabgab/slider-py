import argparse
import json

from .parser import MultiSlider, Slider, SliderError
from .html import HTML

def main():
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

    if args.parse:
        if args.yaml:
            multi_slider = MultiSlider()
            book = multi_slider.process_yml(args.yaml)
            json_str = json.dumps(book, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)
            print(json_str)
            exit()

        if args.md:
            slider = Slider()
            dom = slider.parse(args.md)
            json_str = json.dumps(dom, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)
            print(json_str)
            exit()

        print("--md was missing")
        parser.print_help()
        exit(1)

    if args.html:
        if not args.dir:
            print("--dir was missing")
            parser.print_help()
            exit(1)
        if not args.md:
            print("--md was missing")
            parser.print_help()
            exit(1)
        slider = Slider()
        pages = slider.parse(args.md)
        html = HTML(
            templates = args.templates,
            static = args.static,
            chapter = pages,
            filename = args.md,
            ext      = args.ext,
        )
        html.generate_html_files(args.dir)
        exit()

    parser.print_help()


