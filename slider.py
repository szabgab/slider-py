import argparse
import json

from slider import Slider

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
    parser.add_argument("--md", help="Name of and md file")
    parser.add_argument("--dir", help="Path to the HTML directory")
    parser.add_argument("--templates", help="Directory of the HTML templates")
    parser.add_argument("--static", help="Directory of the static files that will be copied to the html directory")

    args = parser.parse_args()

    if args.parse:
        if not args.md:
            print("--md was missing")
            parser.print_help()
            exit(1)
        slider = Slider()
        dom = slider.parse(args.md)
        json_str = json.dumps(dom, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)
        print(json_str)
        exit()

    if args.html:
        if not args.md:
            print("--md was missing")
            parser.print_help()
            exit(1)
        if not args.dir:
            print("--dir was missing")
            parser.print_help()
            exit(1)
        slider = Slider(templates = args.templates, static = args.static)
        slider.parse(args.md)
        slider.generate_html_files(args.dir)
        exit()

    parser.print_help()

if __name__ == '__main__':
    main()
