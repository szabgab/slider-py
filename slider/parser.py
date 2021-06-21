import re
import os
import json


class SliderError(Exception):
    pass


class MultiSlider(object):
    def process_yml(self, filename):
        root = os.path.dirname(os.path.abspath(filename))
        with open(filename, 'r', encoding="utf-8") as fh:
            conf = json.load(fh)

            self.conf = conf

        conf['pages'] = []

        for md_file in conf['files']:
            slider = Slider()
            pages = slider.parse(os.path.join(root, md_file))
            conf['pages'].append(pages)

        self.check_id_uniqueness()

        return conf

    def check_id_uniqueness(self):
        ids = {}
        for page in self.conf['pages']:
            idx = page['id']
            if idx in ids:
                raise SliderError("Duplicate id {}".format(idx))
            ids[idx] = 1

            for pg in page['pages']:
                idx = pg['id']
                if idx in ids:
                    raise SliderError("Duplicate id {}".format(idx))
                ids[idx] = 1


class Slider(object):
    def is_chapter_title(self, row):
        match = re.search(r'\A# (.*)\Z', row)
        if match:
            if 'title' in self.chapter:
                raise SliderError("Second chapter '{}' found in the same file in '{}'".format(self.chapter['title'], self.filename))
            self.chapter['title'] = match.group(1)
            return True
        return False

    def is_id(self, row):
        match = re.search(r'\A\{id: ([a-z0-9-]+)\}\s*\Z', row)
        if match:
            idx = match.group(1)
            if self.page:
                if 'id' in self.page:
                    raise SliderError("Second page id '{}' found in the same file in '{}' in line '{}'".format(self.page['id'], self.filename, self.line))
                self.page['id'] = idx
            else:
                if 'id' in self.chapter:
                    raise SliderError('Second chapter id found in the same file in {} in line {}'.format(self.filename, self.line))
                self.chapter['id'] = idx
            if idx in self.ids:
                raise SliderError('The id {} found twice in file {} in line {}'.format(idx, self.filename, self.line))
            self.ids.add(idx)
            return True
        return False

    def is_index(self, row):
        # {i: index field}
        # {i: index!field}
        match = re.search(r'\A\{i:\s+(.+)\}\s*\Z', row)
        #match = re.search(r'\A\{i:\s+(.+)', row)
        if match:
            if 'i' not in self.page:
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

    def is_table(self, row):
        if row == '':
            return False
        if row[0] != '|':
            if self.tag and self.tag['name'] == 'table':
                self.add_tag()
                return True
            else:
                return False

        if not self.tag:
            self.tag['name'] = 'table'
            self.tag['content'] = {}
            self.tag['content']['titles'] = []
            self.tag['content']['rows'] = []

        if re.search(r'\A\|(\s*-*\s*\|)+\s*\Z', row):
            self.tag['content']['titles'] = self.tag['content']['rows']
            self.tag['content']['rows'] = []
            return True

        this_row = re.split(r'\s*\|\s*', row)
        self.tag['content']['rows'].append(this_row)
        return True

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
                    if not os.path.exists(include_path):
                        raise SliderError('Included file "{}" does not exist. In {} in line {}.'.format(include_path, self.filename, self.line))
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

    def is_block(self, row):
        blocks = ['aside', 'blockquote', 'blurb', 'exercise', 'quiz']
        blocks_str = '|'.join(blocks)
        closing_regex = r'\A\{/(' + blocks_str + r')}\Z'
        match = re.search(closing_regex, row)
        if match:
            if not self.tag:
                raise SliderError('{} before it was started page {} in line {}'.format(row, self.filename, self.line))
            if self.tag['name'] != match.group(1):
                raise SliderError('Ending {} while we are in {}. page {} in line {}'.format(row, self.tag['name'], self.filename, self.line))
            self.add_tag()
            return True

        opening_regex = r'\A\{(' + blocks_str + r')}\Z'
        match = re.search(opening_regex, row)
        if match:
            if not self.page:
                raise SliderError('Starting {} outside of page {} in line {}'.format(row, self.filename, self.line))
            if self.tag:
                raise SliderError('Starting {} inside another tag: {} of page {} in line {}'.format(row, self.tag['name'], self.filename, self.line))
            self.tag['name'] = match.group(1)
            self.tag['content'] = ['\n']
            return True

        if self.tag and self.tag['name'] in blocks:
            match = re.search(r'\A\* (.*)', row)
            if match:
                if 'internal' not in self.tag:
                    self.tag['internal'] = '</ul>'
                    self.tag['content'].append('<ul>')
                self.tag['content'].append('<li>' + match.group(1) + '</li>')
            else:
                if 'internal' in self.tag:
                    self.tag['content'].append(self.tag.pop('internal'))
                self.tag['content'].append(row)
            match_empty_row = re.search(r'\A\s*\Z', row)
            if match_empty_row:
                self.tag['content'].append('<p>')
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

        if 'title' not in self.chapter:
            raise SliderError('Chapter title is missing in {}'.format(self.filename))

        if 'id' not in self.chapter:
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

                if self.is_block(row):
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

                if self.is_table(row):
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

