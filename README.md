

1) Parse a simplified MarkDown that is used to create my slides.
2) Generate HTML files from the slides
3) Generate PDF from the slides
4) Generate mobi file from the slides


Example:


```
# Chapter Title
id: page-url
{i: subject matter}
{i: another!subject}

## Page Title
id: page-url

* Bullet
* Points


1 Numbered
1 Bullet
1 Points 


   ```
   Verbatim for code
   ``` 

Free Paragraph text.


HTML Links: <a href="https://code-maven.com/slides/">slides</a> that will be used as links anywhere except in verbatim text 

![Title](path/to/file.py)    # include external file
![](path/to/file.py)         # include external file use filename as title

``` 

TODO:
* bold
* command (maybe just bold)
* links []() or a href ?
* tags to be indexed
* Images
* Multiple files in one course
* Extra text that is not included in the slide (or is optional)

* Generate HTML and test it