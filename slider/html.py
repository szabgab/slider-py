import datetime
import jinja2
import os
import re
import shutil
import yaml
import json
from pygments import highlight
from pygments.lexers import get_lexer_for_filename
from pygments.formatters import HtmlFormatter


def _replace_links(html):
    html = re.sub(r'\[([^]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)
    html = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', html)
    html = re.sub(r'`([^`]+)`', r'<span class="code">\1</span>', html)
    return html


def _html_escape(html):
    html = re.sub(r'<', '&lt;', html)
    html = re.sub(r'>', '&gt;', html)
    return html


def _syntax(code, filename):
    file_name, file_extension = os.path.splitext(filename)
    skip = ['.out', '.log', '.in', '.csv', '.err', '.PL', '.mypy', '.dump', '.ok', '.nok', '.SKIP', '.psgi', '.glade', '.conf']  # becasue Pygments does not know them.
    skip.extend(['.pl'])  # skip Perl files becaus they look horrible in the current syntaxt highlighting
    skip.extend(['.t', '.tap'])  # not supported in older version of Pygment we have on the server
    if not file_extension or file_extension in skip:
        return _html_escape(code)
    try:
        lexer = get_lexer_for_filename(filename)
        return highlight(code, lexer, HtmlFormatter())
    except Exception:
        print("Could not find lexer for {}".format(filename))
        exit(1)
        #It is ok if we can't find a lexer
        #pass


class HTML():
    # TODO: clean up the parameter list so we fail early if required parameters are not provided
    def __init__(self, ext=None, chapter=None, includes=None, templates=None, static=None):
        self.root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.timestamp = datetime.datetime.now()

        self.chapter = chapter
        self.includes = includes

        if ext is not None and ext != '':
            if ext[0] == '.':
                self.ext = ext
            else:
                self.ext = '.' + ext
        else:
            self.ext = ''

        if templates is not None:
            self.templates = templates
        else:
            self.templates = os.path.join(self.root, 'templates')

        if static is not None:
            self.static = static
        else:
            self.static = os.path.join(self.root, 'static')

    def create_keywords_page(self):
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(self.templates))
        keywords_template = env.get_template('keywords.html')
        html = keywords_template.render(
            keywords  = self.keywords,
            timestamp = self.timestamp,
            extension = self.ext,
            title     = 'Keywords',
        )
        html = _replace_links(html)
        self.pages.append(
            {
                'id'   : 'keywords',
                'html' : html,
            }
        )

        return

    def generate_html(self, prev_page = None, next_page = None, next_chapter = None):
        self.keywords = {}
        self.pages = []
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(self.templates))
        env.filters['linker'] = _replace_links
        env.filters['syntax'] = _syntax

        self.create_chapter_head(env, next_page, prev_page)
        self.create_pages(env, next_chapter)
        self.create_keywords_page()

        return

    def create_pages(self, env, next_chapter):
        page_template = env.get_template('page.html')
        for ix in range(len(self.chapter['pages'])):
            page = self.chapter['pages'][ix]
            if ix > 0:
                page['prev'] = self.chapter['pages'][ix - 1]
            else:
                page['prev'] = {
                    'id': self.chapter['id'],
                    'title': self.chapter['title'],
                }
            if ix < len(self.chapter['pages']) - 1:
                page['next'] = self.chapter['pages'][ix + 1]
            else:
                page['next'] = next_chapter

            if 'i' in page:
                page['keywords'] = page['i']
                for pair in page['i']:
                    main_key = pair[0]
                    sub_key = ''
                    if len(pair) > 1:
                        sub_key = pair[1]
                    if main_key not in self.keywords:
                        self.keywords[main_key] = {}
                    if sub_key not in self.keywords[main_key]:
                        self.keywords[main_key][sub_key] = []
                    self.keywords[main_key][sub_key].append({
                        'id': page['id'],
                        'title': page['title'],
                    })

            html = page_template.render(
                title     = page['title'],
                page      = page,
                prev      = page.get('prev'),
                next      = page.get('next'),
                timestamp = self.timestamp,
                extension =self.ext,
                chapter   = self.chapter,
                srcdir    = os.path.basename(self.includes),
            )
            #html = _replace_links(html)
            self.pages.append(
                {
                    'id': page['id'],
                    'html': html,
                }
            )

    def create_chapter_head(self, env, next_page, prev_page):
        chapter_template = env.get_template('chapter.html')
        html = chapter_template.render(
            title      = self.chapter['title'],
            pages      = self.chapter['pages'],
            timestamp  = self.timestamp,
            extension  = self.ext,
            prev       = prev_page,
            next       = next_page,
        )
        html = _replace_links(html)
        self.pages.append(
            {
                'id': self.chapter['id'],
                'html': html,
            }
        )


class OnePage(HTML):
    def generate_html_files(self, in_dir, prev_page = None, next_page = None, next_chapter = None):
        work_dir = os.getcwd()
        html_path = os.path.join(work_dir, in_dir)
        if not os.path.exists(html_path):
            os.makedirs(html_path)
        self.generate_html(prev_page=prev_page, next_page=next_page, next_chapter=next_chapter)
        for page in self.pages:
            html_filename = os.path.join(in_dir, page['id'] + self.ext)
            with open(html_filename, 'w', encoding="utf-8") as fh:
                fh.write(page['html'])

        self.copy_image_files(in_dir)
        self.copy_static_files(in_dir)
        self.save_info_yml(in_dir)

    def save_info_yml(self, in_dir):
        info = {
            "title": self.chapter['title'],
            "cnt": len(self.pages),
        }
        info_filename = os.path.join(in_dir, 'info.yaml')
        with open(info_filename, 'w', encoding="utf-8") as fh:
            fh.write(yaml.dump(info, default_flow_style=False))
        info_filename = os.path.join(in_dir, 'info.json')
        with open(info_filename, 'w', encoding="utf-8") as fh:
            json.dump(info, fh, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)

    def copy_static_files(self, in_dir):
        if os.path.exists(self.static):
            for entry in os.listdir(self.static):
                shutil.copy(os.path.join(self.static, entry), in_dir)

    def copy_image_files(self, in_dir):
        for page in self.chapter['pages']:
            if 'content' not in page:  # TODO: shall we make sure there is alway a content?
                continue

            for c in page['content']:
                if c['name'] == 'image' or c['name'] == 'video':
                    img_dir = os.path.join(in_dir, os.path.dirname(c['filename']))
                    if not os.path.exists(img_dir):
                        os.makedirs(img_dir)
                    include_path = os.path.join(self.includes, c['filename'])
                    # print(include_path)
                    shutil.copy(include_path, img_dir)


class Book(HTML):
    def __init__(self, book, **kw):
        self.book = book
        self.pages = []
        super(Book, self).__init__(**kw)
        self.keywords = {}

    def generate_book(self, in_dir):
        #print(self.book['pages'][1])
        for i in range(len(self.book['pages'])):
            page = self.book['pages'][i]
            html = OnePage(
                templates = self.templates,
                static    = self.static,
                chapter   = page,
                includes  = self.includes,
                ext       = self.ext,
            )

            prev_page = {
                'id' : 'toc',
                'title' : 'TOC',
            }
            if i > 0:
                prev_page = self.book['pages'][i-1]  # chapter
                if len(self.book['pages'][i-1]['pages']) > 0:
                    prev_page = self.book['pages'][i-1]['pages'][-1]
            next_page = None
            if 0 < len(self.book['pages'][i]['pages']):
                next_page = self.book['pages'][i]['pages'][0]  # first page in this chapter
            elif i < len(self.book['pages']) - 1:
                next_page = self.book['pages'][i+1]  # next chapter
            next_chapter = None
            if i < len(self.book['pages']) - 1:
                next_chapter = self.book['pages'][i+1]
            html.generate_html_files(in_dir, prev_page=prev_page, next_page=next_page, next_chapter=next_chapter)

            self.merge_keywords(html)

        self.page_count = 0
        for chapter in self.book['pages']:
            self.page_count += 1
            for page in chapter['pages']:
                self.page_count += 1

        self.create_book_index_page(in_dir)
        self.create_book_toc_page(in_dir)
        self.create_keywords_page()
        self.save_info_yml(in_dir)
        html_filename = os.path.join(in_dir, 'keywords' + self.ext)
        with open(html_filename, 'w', encoding="utf-8") as fh:
            fh.write(self.pages[0]['html'])

    def save_info_yml(self, in_dir):
        info = {
            "title": self.book['title'],
            "cnt": self.page_count,
        }
        info_filename = os.path.join(in_dir, 'info.yaml')
        with open(info_filename, 'w', encoding="utf-8") as fh:
            fh.write(yaml.dump(info, default_flow_style=False))
        info_filename = os.path.join(in_dir, 'info.json')
        with open(info_filename, 'w', encoding="utf-8") as fh:
            json.dump(info, fh, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)

    def merge_keywords(self, html):
        for kw in html.keywords:
            if kw in self.keywords:
                for kw2 in self.keywords[kw]:
                    if kw2 in self.keywords[kw]:
                        self.keywords[kw][kw2] += html.keywords[kw][kw2]
                    else:
                        self.keywords[kw][kw2] = html.keywords[kw][kw2]
            else:
                self.keywords[kw] = html.keywords[kw]

    def create_book_index_page(self, in_dir):
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(self.templates))
        index_template = env.get_template('index.html')
        #print(self.book['pages'][0])
        first = self.book['pages'][0]
        html = index_template.render(
            title      = self.book['title'],
            book       = self.book,
            prev       = None,
            next       = { "id" : "toc", "title": "Start" },
            first      = first,
            this_year  = datetime.datetime.now().year,
            extension  = self.ext,
        )
        html_filename = os.path.join(in_dir, 'index' + self.ext)
        with open(html_filename, 'w', encoding="utf-8") as fh:
            fh.write(html)

    def create_book_toc_page(self, in_dir):
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(self.templates))
        toc_template = env.get_template('toc.html')
        html = toc_template.render(
            title      = "TOC: " + self.book['title'],
            book       = self.book,
            this_year  = datetime.datetime.now().year,
            prev       = { "id" : "index", "title": "Index" },
            next       = { "id" : self.book['pages'][0]['id'], "title": self.book['pages'][0]['title'] },
            extension  = self.ext,
        )
        html_filename = os.path.join(in_dir, 'toc' + self.ext)
        with open(html_filename, 'w', encoding="utf-8") as fh:
            fh.write(html)


