import argparse
import re
import os
import yaml
import shutil
import json
from jinja2 import Environment, FileSystemLoader

class SliderError(Exception):
    pass

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


class Slider(object):
    def __init__(self, **kw):
        self.root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        if 'templates' in kw and kw['templates']:
            self.templates = kw['templates']
        else:
            self.templates = os.path.join(self.root, 'templates')

        if 'static' in kw and kw['static']:
            self.static = kw['static']
        else:
            self.static = os.path.join(self.root, 'static')

    def process_yml(self, filename):
        with open(filename, 'r') as fh:
            conf = yaml.load(fh)
        return {}

    def parse(self, filename):
        self.chapter = {}
        self.chapter['pages'] = []
        self.page = {}
        self.tag = {}
        self.path_to_file = os.path.dirname(filename)

        # TODO: error when md file is missing
        with open(filename) as fh:
            line = 0
            for row in fh:
                line += 1
                row = row.rstrip('\n')

                if 'name' in self.tag and self.tag['name'] and self.tag['name'] == 'verbatim' and row != '```':
                    # inside verbatim quote we should not parse anything
                    self.tag['content'][0] += row + "\n"
                    continue


                match = re.search(r'\A# (.*)\Z', row)
                if match:
                # TODO: error if duplicate chapter title in the same file
                    if 'title' in self.chapter:
                        raise SliderError('Second chapter found in the same file in {}'.format(filename))
                    self.chapter['title'] = match.group(1)
                    continue

                # TODO: error if something follows a Chapter title that is not an id - probably not needed
                # TODO: error if there are duplicate chapter ids
                match = re.search(r'\A\{id: ([a-z0-9-]+)\}\s*\Z', row)
                if match:
                    if self.page:
                        if 'id' in self.page:
                            raise SliderError('Second page id found in the same file in {} in page {}'.format(filename), self.page)
                        self.page['id'] = match.group(1)
                    else:
                        if 'id' in self.chapter:
                            raise SliderError('Second chapter id found in the same file in {}'.format(filename))
                        self.chapter['id'] = match.group(1)
                    continue

                # {i: index field}
                # {i: index!field}
                match = re.search(r'\A\{i:\s+(.+)\}\s*\Z', row)
                #match = re.search(r'\A\{i:\s+(.+)', row)
                if match:
                    if not 'i' in self.page:
                        self.page['i'] = []
                    fields = match.group(1).split('!')
                    self.page['i'].append(fields)
                    continue


                match = re.search(r'\A## (.*)\Z', row)
                if match:
                    self.add_page()
                    self.page['title'] = match.group(1)
                    continue

                # ul, ol
                match = re.search(r'\A([\*1]) (.*)\Z', row)
                if match:
                    tag_name = 'ul'
                    if match.group(1) == '1':
                        tag_name = 'ol'

                    if not self.page:
                        raise SliderError('* Encountered outside of page {} in line {}'.format(filename, line))
                    if not self.tag:
                        self.tag['name'] = tag_name
                        self.tag['content'] = []
                    if self.tag:
                        if self.tag['name'] != tag_name:
                            raise SliderError('* Encountered outside of {} {} in {} in line {}'.format(tag_name, filename, self.page, line))
                        self.tag['content'].append(match.group(2))
                    continue

                match = re.search(r'\A```\Z', row)
                if match:
                    if not self.page:
                        raise SliderError('``` outside of page {} in line {}'.format(filename, line))
                    if not self.tag:
                        self.tag['name'] = 'verbatim'
                        self.tag['content'] = ['\n']
                        continue
                    if self.tag['name'] != 'verbatim':
                        raise SliderError('``` cannot be inside another tag {} in line {}'.format(filename, line))
                    self.add_tag()
                    continue


                # empty row ends the ol, ul tags
                # empty row is included in the verbatim tag
                match = re.search(r'\A\s*\Z', row)
                if match:
                    if self.tag:
                        if self.tag['name'] == 'verbatim':
                            if self.tag['name'] == 'verbatim':
                                self.tag['content'][0] += "\n"
                            continue
                        if self.tag['name'] == 'p':
                            self.add_tag()

                    self.add_tag()
                    continue


                # free text
                if not self.tag:
                    # include
                    # ![Title](sample/do.py)
                    match = re.search(r'\A\!\[([^]]*)\]\(([^)]+)\)\Z', row)
                    if match:
                        title = match.group(1)
                        include_file = match.group(2)
                        include_path = os.path.join(self.path_to_file, include_file)
                        file_name, file_extension = os.path.splitext(include_file)
                        if file_extension in ['.png']:
                            self.tag['name'] = 'image'
                            self.tag['title'] = title
                            self.tag['filename'] = include_file
                        else:
                            with open(include_path, 'r') as fh:
                                content = fh.read()
                            self.tag['name'] = 'include'
                            self.tag['filename'] = include_file
                            self.tag['content'] = [content]
                            self.tag['title'] = title
                            self.add_tag()
                        continue

                    self.tag['name'] = 'p'
                    self.tag['content'] = ['\n']

                if self.tag['name'] == 'verbatim' or self.tag['name'] == 'p':
                    self.tag['content'][0] += row + "\n"
                    continue

                raise SliderError('Unhandled row "{}" in {} in line {}'.format(row, filename, line))


            self.add_page()


        # TODO: error if id already exists anywhere in the slides (chapters, pages)

        if not 'title' in self.chapter:
            raise SliderError('Chapter title is missing in {}'.format(filename))

        if not 'id' in self.chapter:
            raise SliderError('Chapter id is missing in {}'.format(filename))

        return self.chapter

    def add_tag(self):
        if self.tag:
            if 'content' not in self.page:
                self.page['content'] = []
            self.page['content'].append(self.tag)
            self.tag = {}

    def add_page(self):
        self.add_tag()
        if self.page:
            # TODO: check if page has a title, id etc
            self.chapter['pages'].append(self.page)
            self.page = {}
        return

    def generate_html(self):
        env = Environment(loader=FileSystemLoader(self.templates))
        pages = []

        def _replace_links(html):
            html = re.sub(r'\[([^]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)
            html = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', html)
            return html

        chapter_template = env.get_template('chapter.html')
        html = chapter_template.render(
            title = self.chapter['title'],
            pages = self.chapter['pages']
        )
        html = _replace_links(html)
        pages.append(
            {
                'id'   : self.chapter['id'],
                'html' : html,
            }
        )
        page_template = env.get_template('page.html')
        for i in range(len(self.chapter['pages'])):
            page = self.chapter['pages'][i]
            if i > 0:
                page['prev'] = self.chapter['pages'][i-1]
            else:
                page['prev'] = {
                    'id' : self.chapter['id'],
                    'title' : self.chapter['title'],
                }
            if i < len(self.chapter['pages'])-1:
                page['next'] = self.chapter['pages'][i+1]

            html = page_template.render(
                page = page
            )
            html = _replace_links(html)
            pages.append(
                {
                    'id'   : page['id'],
                    'html' : html,
                }
            )

        return pages

    def generate_html_files(self, in_dir):
        work_dir = os.getcwd()
        html_path = os.path.join(work_dir, in_dir)

        if not os.path.exists(html_path):
                os.makedirs(html_path)
        pages = self.generate_html()
        for page in pages:
            filename = os.path.join(in_dir, page['id'] + '.html')
            with open(filename, 'w') as fh:
                fh.write(page['html'])

        # copy image files
        for page in self.chapter['pages']:
            if 'content' not in page:  # TODO: shall we make sure there is alway a content?
                continue

            for c in page['content']:
                if c['name'] == 'image':
                    img_dir = os.path.join(in_dir, os.path.dirname(c['filename']))
                    if not os.path.exists(img_dir):
                        os.makedirs(img_dir)
                    include_path = os.path.join(self.path_to_file, c['filename'])
                    #print(include_path)
                    shutil.copy(include_path, img_dir)

        # copy static files
        if os.path.exists(self.static):
            for entry in os.listdir(self.static):
                shutil.copy(os.path.join(self.static, entry), in_dir)


if __name__ == '__main__':
    main()
