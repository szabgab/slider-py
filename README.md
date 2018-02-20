# Slider-Py
[![Build Status](https://travis-ci.org/szabgab/silder-py.png)](https://travis-ci.org/szabgab/slider-py)
[![Coverage Status](https://coveralls.io/repos/github/szabgab/slider-py/badge.svg?branch=master)](https://coveralls.io/github/szabgab/slider-py?branch=master)


1) Parse a simplified MarkDown that is used to create my slides.
2) Generate HTML files from the slides
3) Generate PDF from the slides
4) Generate mobi file from the slides


Example:


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

TODO:

* Images
* Multiple files in one course
* Extra text that is not included in the slide (or is optional)

* Generate HTML and test it
* Copy external file without including it in the pages
