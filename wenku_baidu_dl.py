import requests
import json
import os, shutil

import img2pdf
from PIL import Image

filenames = []
TMPDIR = "tmp/"


def convert_to_rgb(path):
    # From https://github.com/zeantsoi/remove-transparency
    image = Image.open(path)
    # If image has an alpha channel
    if image.mode == 'RGBA':
        # Create a blank background image
        bg = Image.new('RGB', image.size, (255, 255, 255))
        # Paste image to background image
        bg.paste(image, (0, 0), image)
        # Save pasted image as image
        bg.save(path, "PNG")


# Each page can be obtained through ai.wenku.baidu.com, from where raw swf data can be extracted
# With each network query, multiple pages can be accessed to speed things up
# A small chunk of header data also serves as progress indication
# So to download a pdf, this program downloads a few swf-s at once with each query
def download_one_block(id, page_number):
    # Reference: https://github.com/Hacksign/BaiduDoc/

    # According to the swf specification, the W and S bytes are constant and always the same
    # The reference indicates that all swf files have a version number 6 and are zlib compressed
    SWF_HEADER = "CWS" + chr(9)

    # Raw swf binary data is stored in a text format
    # After a short json-like header, .swf files are concatenated, page after page
    url = "http://ai.wenku.baidu.com/play/" + id + "?pn=" + str(page_number) + "&rn=5"  # TODO make use of this 'rn' param
    print(url)
    raw_text = requests.get(url).text  # TODO threading to speed up network queries

    # The header of the loaded page looks similar to this: {"totalPage":"6","fromPage":"1","toPage":"5"}
    # While the order of values are consistent, it is better to identify parameters by their names
    metadata = raw_text[raw_text.index('{'):raw_text.index('}') + 1]
    json_obj = json.loads(metadata)
    fromPage = int(json_obj['fromPage'])
    toPage = int(json_obj['toPage'])
    totalPage = int(json_obj['totalPage'])

    # Splitting is used here to separate swf files
    # While the reference library had used a similar method
    #   it would be a better practice to exctract FileLength from the swf headers (TODO)
    splitted = raw_text.split(SWF_HEADER)[1:]  # The first part is discarded as its not a part of any page

    for i in range(len(splitted)):
        # Readding header to the swf files
        data = SWF_HEADER + splitted[i]
        data = data.encode("latin-1")

        base_filename = TMPDIR + str(i + fromPage).zfill(4)
        swf_filename = base_filename + ".swf"
        png_filename = base_filename + ".png"
        with open(swf_filename, "wb") as f:
            f.write(data)
        # Converts the first page of each swf into a png image
        # swfrender takes a path as its main parameter
        os.system("swfrender -r 240 -p 1 " + swf_filename + " -o " + png_filename)  # TODO alternate resolutions (-r 240)
        os.remove(swf_filename)
        # For some reason swfrender outputs pngs with alpha channel sometimes,
        #   and img2pdf refuses to work with images with transparency
        convert_to_rgb(png_filename)

        # Keep track of the generated image files for further unification
        filenames.append(png_filename)

    # Return the last saved page and whether we are done yet or not
    return toPage, totalPage == toPage


def download_pdf(url, output_name):
    try:
        os.mkdir(TMPDIR)
    except OSError:
        pass

    # Documents are identified by and id
    # The reference calls it md5, which suggests that this id might be the generated md5 hash value of the pdfs
    id = url[url.rfind("/")+1:url.rfind(".")]
    fromPage = 1
    while True:
        fromPage, end = download_one_block(id, fromPage)
        fromPage += 1
        if end:
            break

    # Creating final pdf file
    with open(output_name, "wb") as f:
        f.write(img2pdf.convert(filenames))

    shutil.rmtree(TMPDIR)
    pass

if __name__ == "__main__":
    # TODO add command line arguments
    download_pdf("https://wenku.baidu.com/view/db740a9edc3383c4bb4cf7ec4afe04a1b071b016.html?rec_flag=default&sxts=1533997032540", "OUTPUT.pdf")
