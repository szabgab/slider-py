import re
import os
import yaml
import shutil
import datetime
from jinja2 import Environment, FileSystemLoader

class SliderError(Exception):
    pass

class HTML(object):
    def __init__(self, **kw):
        self.root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.timestamp = datetime.datetime.now()

        if 'chapter' in kw and kw['chapter']:
            self.chapter = kw['chapter']

        self.path_to_file = os.path.dirname(kw['filename'])

        self.ext = kw.get('ext')

        if 'templates' in kw and kw['templates']:
            self.templates = kw['templates']
        else:
            self.templates = os.path.join(self.root, 'templates')

        if 'static' in kw and kw['static']:
            self.static = kw['static']
        else:
            self.static = os.path.join(self.root, 'static')


    def generate_html(self):
        env = Environment(loader=FileSystemLoader(self.templates))
        pages = []

        def _replace_links(html):
            html = re.sub(r'\[([^]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)
            html = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', html)
            html = re.sub(r'`([^`]+)`', r'<span class="code">\1</span>', html)
            return html

        chapter_template = env.get_template('chapter.html')
        html = chapter_template.render(
            title = self.chapter['title'],
            pages = self.chapter['pages'],
            timestamp = self.timestamp,
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
                page = page,
                timestamp = self.timestamp,
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
            html_filename = os.path.join(in_dir, page['id'])
            if self.ext is not None:
                html_filename += '.' + self.ext
            with open(html_filename, 'w', encoding="utf-8") as fh:
                fh.write(page['html'])

        # copy image files
        for page in self.chapter['pages']:
            if 'content' not in page:  # TODO: shall we make sure there is alway a content?
                continue

            for c in page['content']:
                if c['name'] == 'image' or c['name'] == 'video':
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

        info = {
            "title": self.chapter['title'],
            "cnt": len(pages),
        }
        info_filename = os.path.join(in_dir, 'info.yaml')
        with open(info_filename, 'w', encoding="utf-8") as fh:
            fh.write(yaml.dump(info, default_flow_style=False))

class Slider(object):

    def process_yml(self, filename):
        with open(filename, 'r', encoding="utf-8") as fh:
            conf = yaml.load(fh, Loader=yaml.FullLoader)
        return {}


    def is_chapter_title(self, row):
        match = re.search(r'\A# (.*)\Z', row)
        if match:
            if 'title' in self.chapter:
                raise SliderError('Second chapter found in the same file in {}'.format(self.filename))
            self.chapter['title'] = match.group(1)
            return True
        return False


    def is_id(self, row):
        match = re.search(r'\A\{id: ([a-z0-9-]+)\}\s*\Z', row)
        if match:
            id = match.group(1)
            if self.page:
                if 'id' in self.page:
                    raise SliderError('Second page id found in the same file in {} in line {}'.format(self.filename, self.line))
                self.page['id'] = id
            else:
                if 'id' in self.chapter:
                    raise SliderError('Second chapter id found in the same file in {} in line {}'.format(self.filename, self.line))
                self.chapter['id'] = id
            if id in self.ids:
                raise SliderError('The id {} found twice in file {} in line {}'.format(id, self.filename, self.line))
            self.ids.add(id)
            return True
        return False


    def is_index(self, row):
        # {i: index field}
        # {i: index!field}
        match = re.search(r'\A\{i:\s+(.+)\}\s*\Z', row)
        #match = re.search(r'\A\{i:\s+(.+)', row)
        if match:
            if not 'i' in self.page:
                self.page['i'] = []
            fields = match.group(1).split('!')
            self.page['i'].append(fields)
            return True
        return False


    def is_page_title(self, row):
        match = re.search(r'\A## (.*)\Z', row)
        if match:
            self.add_page()
            self.page['title'] = match.group(1)
            return True
        return False


    def is_list(self, row):
        # ul, ol
        match = re.search(r'\A(\*|1.) (.*)\Z', row)
        if match:
            tag_name = 'ul'
            if match.group(1) == '1.':
                tag_name = 'ol'

            if not self.page:
                raise SliderError('* Encountered outside of page {} in line {}'.format(self.filename, self.line))
            if not self.tag:
                self.tag['name'] = tag_name
                self.tag['content'] = []
            if self.tag:
                if self.tag['name'] == 'p':
                    self.add_tag()
                    self.tag['name'] = tag_name
                    self.tag['content'] = []

                if self.tag['name'] != tag_name:
                    raise SliderError('* Encountered outside of {} {} in {} in line {}'.format(tag_name, self.filename, self.page, self.line))
                self.tag['content'].append(match.group(2))
            return True
        return False


    def is_empty(self, row):
        # empty row ends the ol, ul tags
        # empty row is included in the verbatim tag
        match = re.search(r'\A\s*\Z', row)
        if match:
            if self.tag:
                if self.tag['name'] == 'verbatim':
                    if self.tag['name'] == 'verbatim':
                        self.tag['content'][0] += "\n"
                    return True
                if self.tag['name'] == 'p':
                    self.add_tag()

            self.add_tag()
            return True
        return False


    def is_free_text(self, row):
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
                if file_extension in ['.png', '.jpg', '.svg']:
                    self.tag['name'] = 'image'
                    self.tag['title'] = title
                    self.tag['filename'] = include_file
                elif file_extension in ['.mp4']:
                    self.tag['name'] = 'video'
                    self.tag['title'] = title
                    self.tag['filename'] = include_file
                else:
                    with open(include_path, 'r', encoding="utf-8") as fh:
                        content = fh.read()
                    self.tag['name'] = 'include'
                    self.tag['filename'] = include_file
                    self.tag['content'] = [content]
                    self.tag['title'] = title
                    self.add_tag()
                return True

            self.tag['name'] = 'p'
            self.tag['content'] = ['\n']

        if self.tag['name'] == 'verbatim' or self.tag['name'] == 'p':
            self.tag['content'][0] += row + "\n"
            return True
        return False


    def is_verbatim(self, row):
        match = re.search(r'\A```\Z', row)
        if match:
            if not self.page:
                raise SliderError('``` outside of page {} in line {}'.format(self.filename, self.line))
            if not self.tag:
                self.tag['name'] = 'verbatim'
                self.tag['content'] = ['\n']
                return True
            if self.tag['name'] != 'verbatim':
                raise SliderError('``` cannot be inside another tag {} in line {}'.format(self.filename, self.line))
            self.add_tag()
            return True
        return False


    def check_requirements(self):
        # TODO: error if id already exists anywhere in the slides (chapters, pages)

        if not 'title' in self.chapter:
            raise SliderError('Chapter title is missing in {}'.format(self.filename))

        if not 'id' in self.chapter:
            raise SliderError('Chapter id is missing in {}'.format(self.filename))


    def parse(self, filename):
        self.chapter = {}
        self.chapter['pages'] = []
        self.page = {}
        self.tag = {}
        self.path_to_file = os.path.dirname(filename)
        self.ids = set()
        self.filename = filename

        # TODO: error when md file is missing
        with open(self.filename, encoding="utf-8") as fh:
            self.line = 0
            for row in fh:
                self.line += 1
                row = row.rstrip('\n')

                if 'name' in self.tag and self.tag['name'] and self.tag['name'] == 'verbatim' and row != '```':
                    # inside verbatim quote we should not parse anything
                    self.tag['content'][0] += row + "\n"
                    continue

                if self.is_chapter_title(row):
                    continue

                if self.is_id(row):
                    continue

                if self.is_index(row):
                    continue

                if self.is_page_title(row):
                    continue

                if self.is_list(row):
                    continue

                if self.is_verbatim(row):
                    continue

                if self.is_empty(row):
                    continue

                if self.is_free_text(row):
                    continue

                raise SliderError('Unhandled row "{}" in {} in line {}'.format(row, self.filename, self.line))

            self.add_page()

        self.check_requirements()

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
            if 'id' not in self.page:
                raise SliderError('Page id is missing in {} in line {}'.format(self.filename, self.line))
            self.chapter['pages'].append(self.page)
            self.page = {}
        return

