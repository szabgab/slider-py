# Slider-Py
[![Build Status](https://travis-ci.org/szabgab/slider-py.png)](https://travis-ci.org/szabgab/slider-py)
[![Coverage Status](https://coveralls.io/repos/github/szabgab/slider-py/badge.svg?branch=master)](https://coveralls.io/github/szabgab/slider-py?branch=master)


1) Parse a simplified MarkDown that is used to create my slides.
2) Generate HTML files from the slides
3) Generate PDF from the slides
4) Generate mobi file from the slides


## Example


```
# Chapter Title
{id: page-url}
{i: subject matter}
{i: another!subject}

## Page Title
{id: page-url}

* Bullet
* Points


1 Numbered
1 Bullet
1 Points 


   ```
   Verbatim for code
   ``` 

Free Paragraph text.


HTML Links: [slides](https://code-maven.com/slides/) that will be used as links anywhere except in verbatim text 

![Title](path/to/file.py)    # include external file
![](path/to/file.py)         # include external file use filename as title

**bold**

![Title](path/to/file.png)    # include image

``` 

## TODO

* Navigation link on the HTML pages
* Navigation key-binding in JavaScript
* Web pages should be without extension

* Multiple files in one course
* Main page for multi-file case should be index.html

* Extra text that is not included in the slide (or is optional)

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

