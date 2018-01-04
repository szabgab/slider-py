

1) Parse a simplified MarkDown that is used to create my slides.
2) Generate HTML files from the slides
3) Generate PDF from the slides
4) Generate mobi file from the slides


Example:


```
# Chapter Title
id: page-url

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

Include external files:

include: path/to/file.py

``` 
