import argparse
import re
from jinja2 import Environment, FileSystemLoader

class SliderError(Exception):
    pass

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Name of and md file")

    args = parser.parse_args()

    slider = Slider()
    slider.parse(args.file)

class Slider(object):
    def parse(self, filename):
        self.chapter = {}
        self.chapter['pages'] = []
        self.page = {}
        self.tag = {}

        # TODO: error when md file is missing
        with open(filename) as fh:
            for row in fh:
                row = row.rstrip('\n')
                match = re.search(r'\A# (.*)\Z', row)
                if match:
                # TODO: error if duplicate chapter title in the same file
                    if 'title' in self.chapter:
                        raise SliderError('Second chapter found in the same file in {}'.format(filename))
                    self.chapter['title'] = match.group(1)
                    continue

                # TODO: error if something follows a Chapter title that is not an id - probably not needed
                # TODO: error if there are duplicate chapter ids
                match = re.search(r'\Aid: ([a-z0-9-]+)\Z', row)
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
                        raise SliderError('* Encountered outside of page {}'.format(filename))
                    if not self.tag:
                        self.tag['name'] = tag_name
                        self.tag['content'] = []
                    if self.tag:
                        if self.tag['name'] != tag_name:
                            raise SliderError('* Encountered outside of {} {} in {}'.format(tag_name, filename. self.page))
                        self.tag['content'].append(match.group(2))
                    continue

                match = re.search(r'\A```\Z', row)
                if match:
                    if not self.page:
                        raise SliderError('``` outside of page {}'.format(filename))
                    if not self.tag:
                        self.tag['name'] = 'verbatim'
                        self.tag['content'] = ['\n']
                        continue
                    if self.tag['name'] != 'verbatim':
                        raise SliderError('``` cannot be inside another tag {}'.format(filename))
                    self.add_tag()
                    continue


                # empty row ends the ol, ul tags
                # empty row is included in the verbatim tag
                match = re.search(r'\A\s*\Z', row)
                if match:
                    if self.tag:
                        if self.tag['name'] == 'verbatim':
                            self.tag['content'][0] += "\n"
                            continue

                    self.add_tag()
                    continue


                # free text
                if not self.tag:
                    self.tag['name'] = 'p'
                    self.tag['content'] = ['']

                if self.tag['name'] == 'verbatim' or self.tag['name'] == 'p':
                    self.tag['content'][0] += row + "\n"
                    continue

                raise SliderError('Unhandled row "{}" in {}'.format(row, filename))


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
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template('chapter.html')
        html = template.render(
            title = self.chapter['title']
        )
        return [
            {
                'id'   : self.chapter['id'],
                'html' : html,
            }
        ]

if __name__ == '__main__':
    main()