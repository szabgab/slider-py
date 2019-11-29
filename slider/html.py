import datetime
import jinja2
import os
import re
import shutil
import yaml

class HTML(object):
    def __init__(self, **kw):
        self.root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.timestamp = datetime.datetime.now()

        # TODO: clean up this code so we fail early if required parameters are not provided
        # TODO: shall we separate the Multi chapter generator to its own classs?
        if 'book' in kw and kw['book']:
            self.book = kw['book']

        if 'chapter' in kw and kw['chapter']:
            self.chapter = kw['chapter']

        if 'includes' in kw and kw['includes'] is not None:
            self.includes = kw['includes']

        if 'ext' in kw and kw['ext'] is not None and kw['ext'] != '':
            if kw['ext'][0] == '.':
                self.ext = kw['ext']
            else:
                self.ext = '.' + kw['ext']
        else:
            self.ext = ''

        if 'templates' in kw and kw['templates']:
            self.templates = kw['templates']
        else:
            self.templates = os.path.join(self.root, 'templates')

        if 'static' in kw and kw['static']:
            self.static = kw['static']
        else:
            self.static = os.path.join(self.root, 'static')

    def generate_html(self, prev = None):
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(self.templates))
        pages = []

        def _replace_links(html):
            html = re.sub(r'\[([^]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)
            html = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', html)
            html = re.sub(r'`([^`]+)`', r'<span class="code">\1</span>', html)
            return html

        keywords = {}

        chapter_template = env.get_template('chapter.html')
        html = chapter_template.render(
            title = self.chapter['title'],
            pages = self.chapter['pages'],
            timestamp = self.timestamp,
            extension  = self.ext,
            prev       = prev,
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

            if 'i' in page:
                page['keywords'] = page['i']
                for pair in page['i']:
                    main_key = pair[0]
                    sub_key = ''
                    if len(pair) > 1:
                        sub_key = pair[1]
                    if main_key not in keywords:
                        keywords[main_key] = {}
                    if sub_key not in keywords[main_key]:
                        keywords[main_key][sub_key] = []
                    keywords[main_key][sub_key].append({
                        'id': page['id'],
                        'title': page['title'],
                    })

            html = page_template.render(
                page = page,
                timestamp = self.timestamp,
                extension = self.ext,
            )
            html = _replace_links(html)
            pages.append(
                {
                    'id'   : page['id'],
                    'html' : html,
                }
            )

        try:
            keywords_template = env.get_template('keywords.html')
            html = keywords_template.render(
                keywords  = keywords,
                timestamp = self.timestamp,
                extension = self.ext,
                title     = 'Keywords',
            )
            html = _replace_links(html)
            pages.append(
                {
                    'id'   : 'keywords',
                    'html' : html,
                }
            )
        except jinja2.exceptions.TemplateNotFound:
            print("Template keywords.html not found")

        return pages

    def generate_book(self, in_dir):
        #print(self.book['pages'][1])
        prev = {
            'id' : 'index'
        }
        for page in self.book['pages']:
            html = HTML(
                templates = self.templates,
                static    = self.static,
                chapter   = page,
                includes  = self.includes,
                ext       = self.ext,
            )
            html.generate_html_files(in_dir, prev=prev)
            prev = self.book['pages'][-1]

        # create index page
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(self.templates))
        index_template = env.get_template('index.html')
        #print(self.book['pages'][0])
        first = self.book['pages'][0]
        html = index_template.render(
            title      = self.book['title'],
            book       = self.book,
            first      = first,
            this_year  = datetime.datetime.now().year,
            extension  = self.ext,
        )
        html_filename = os.path.join(in_dir, 'index' + self.ext)
        with open(html_filename, 'w', encoding="utf-8") as fh:
            fh.write(html)

        # create toc page
        toc_template = env.get_template('toc.html')
        html = toc_template.render(
            title      = self.book['title'],
            book       = self.book,
            this_year  = datetime.datetime.now().year,
            extension  = self.ext,
        )
        html_filename = os.path.join(in_dir, 'toc' + self.ext)
        with open(html_filename, 'w', encoding="utf-8") as fh:
            fh.write(html)

    def generate_html_files(self, in_dir, prev = None):
        work_dir = os.getcwd()
        html_path = os.path.join(work_dir, in_dir)
        if not os.path.exists(html_path):
                os.makedirs(html_path)
        pages = self.generate_html(prev=prev)
        for page in pages:
            html_filename = os.path.join(in_dir, page['id'] + self.ext)
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
                    include_path = os.path.join(self.includes, c['filename'])
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


