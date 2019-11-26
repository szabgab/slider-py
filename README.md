# Slider-Py
[![Build Status](https://travis-ci.org/szabgab/slider-py.png)](https://travis-ci.org/szabgab/slider-py)
[![Coverage Status](https://coveralls.io/repos/github/szabgab/slider-py/badge.svg?branch=master)](https://coveralls.io/github/szabgab/slider-py?branch=master)


1) Parse a simplified MarkDown that is used to create my slides.  (TODO make the format a subset of [Markua](https://leanpub.com/markua/read))
2) Generate HTML files from the slides
3) Generate PDF from the slides
4) Generate mobi file from the slides

See the [slide sources](https://github.com/szabgab/slides) and the generated [slides](https://code-maven.com/slides/)

## Example

Create a director (e.g. 'example') and in there a file called 'main.md' with the following content.

```
# Chapter Title
{id: page-url}
{i: subject matter}
{i: another!subject}

## Page Title
{id: page-url}

* Bullet
* Points


1. Numbered
1. Bullet
1. Points


   ```
   Verbatim for code between triple backticks.
   ```

Free Paragraph text.

**bold between a pair of double-stars**

`inline code example between single backticks`

HTML Links: [slides](https://code-maven.com/slides/) that will be used as links anywhere except in verbatim text

![Title](path/to/file.py)    # include external file
![](path/to/file.py)         # include external file use filename as title

![Title](path/to/file.png)    # include image


{aside}
In the asides, we support [links](http://some-page.com), **bold** and

* unordered
* list
{/aside}
```

Then run

```
python slider.py --md example/main.md --html --dir html/
```

The results shoule be in the 'html' directory.

## TODO

* Navigation key-binding in JavaScript (can be in other templating system)
* make sure the same id does not exists in different pages
* makes sure index is not an id in the multiSlider case
* make sure keywords is not an id
* make sure examples is not an id
* other conflicts?
* Main page for multi-file case should be index.html

## Development suggestions:

Generate html slides in a temporary local directory to look at the result

```
rm -rf html/*; python slider/__init__.py --md cases/all.md --html --dir html
```

Update the expected results for a test case:

```
rm -rf cases/html/all
python slider/__init__.py --md cases/all.md --html --dir cases/html/all/
```

update all the test cases:
./update_test_cases
