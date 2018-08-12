# wenku.baidu.com downloader

Download documents from wenku.baidu.com without registration

## Requirements

* img2pdf: https://github.com/josch/img2pdf
* swfrender from swftools: http://www.swftools.org/

## Usage

Run the main script with the url as its first parameter. Some examples:

```
python3 wenku_baidu_dl.py https://wenku.baidu.com/view/db740a9edc3383c4bb4cf7ec4afe04a1b071b016.html
```
This call will save the resulting file to OUTPUT.pdf with an image resolution of 240 dpi and it will download 5 pages at a time.

```
python3 wenku_baidu_dl.py "https://wenku.baidu.com/view/db740a9edc3383c4bb4cf7ec4afe04a1b071b016.html?rec_flag=default&sxts=1533997032540" -o result.pdf -r 360 -p 10
```
The resulting file in this case will be named as result.pdf, with a resolution of 360 dpi, and 10 pages will be acquired with each query.

Also note that you should enclose the url in quotes, if you decide not to truncate the parameter list coming after .html. The & sign is the critical part here, which would detach the process, and would mess with the upcoming optional arguments.


## Credits

* https://github.com/bazzinotti/dl-baidu-pdf
* https://github.com/Hacksign/BaiduDoc/
* https://github.com/zyp001a/swf2pdf

## Notes

While similar software did exist (https://github.com/bazzinotti/dl-baidu-pdf), I found it cumbersome to set it up, especially when I had to fix numerous issues just to make it work. On one had, modularity is a good thing, but on the other hand, these modules were not working well together, updates broke compatibility, so I rewrote the easy stuff (everything except the conversion libraries) in Python.

With that in mind, this pythonic version can/will have a few advantages:

* Better support for non-Unix operating systems like Windows. At the moment I think the only critical/nontrivial method is the swfrender call.
* Easier optimization using threading
* This version can be used without root permissions (if you have img2pdf already)

The same limitations still apply. Each file, be it .pdf, .doc or .ppt, will be converted as a sequence of images and will be saved as pdf, which means the original text can't be recovered unless you run the whole pdf through some kind of OCR software. If you are interested in solving this problem, this might be a good place to start: http://nongnu.13855.n7.nabble.com/swf2pdf-td119700.html

If you are downloading a .pdf with links, you should except warnings like "Error: ID 68 unknown" popping up in the console, but they are normal.
