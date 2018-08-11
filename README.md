# wenku.baidu.com downloader

Download documents from wenku.baidu.com without registration

# Requirements

* img2pdf: https://github.com/josch/img2pdf
* swfrender from swftools: http://www.swftools.org/

# Usage

Paste the desired url into the method call in the main block as its first parameter, then run the script

# Credits

* https://github.com/bazzinotti/dl-baidu-pdf
* https://github.com/Hacksign/BaiduDoc/
* https://github.com/zyp001a/swf2pdf

# Notes

While similar software did exist (https://github.com/bazzinotti/dl-baidu-pdf), I found it cumbersome to set it up, especially when I had to fix numerous issues just to make it work. On one had, modularity is a good thing, but on the other hand, these modules were not working well together, updates broke compatibility, so I rewrote the easy stuff (everything except the conversion libraries) in Python.

With that in mind, this pythonic version can/will have a few advantages:

* Better support for non-Unix operating systems like Windows. At the moment I think the only critical method is the swfrender call.
* Easier optimization using threading
* This version can be used without root permissions (if you have img2pdf already)

The same limitations still apply. Each file, be it .pdf, .doc or .ppt, will be converted as a sequence of images and will be saved as pdf, which means the original text can't be recovered unless you run the whole pdf through some kind of OCR software. If you are interested in solving this problem, this might be a good place to start: http://nongnu.13855.n7.nabble.com/swf2pdf-td119700.html
