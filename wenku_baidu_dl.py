import requests
import json
import os, shutil
import argparse

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
def download_one_block(id, page_number, resolution, pages_per_query):
    # Reference: https://github.com/Hacksign/BaiduDoc/

    # According to the swf specification, the W and S bytes are constant and always the same
    # The reference indicates that all swf files have a version number 9 and are zlib compressed
    SWF_HEADER = "CWS" + chr(9)

    # Raw swf binary data is stored in a text format
    # After a short json-like header, .swf files are concatenated, page after page
    url = "http://ai.wenku.baidu.com/play/" + id + "?pn=" + str(page_number) + "&rn=" + str(pages_per_query)
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
    #   it would be a better practice to extract FileLength from the swf headers (TODO)
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
        os.system("swfrender -r " + str(resolution) + " -p 1 " + swf_filename + " -o " + png_filename)
        os.remove(swf_filename)
        # For some reason swfrender outputs pngs with alpha channel sometimes,
        #   and img2pdf refuses to work with images with transparency
        convert_to_rgb(png_filename)

        # Keep track of the generated image files for further unification
        filenames.append(png_filename)

    # Return the last saved page and whether we are done yet or not
    return toPage, totalPage == toPage


def download_pdf(url, output_name, resolution, pages_per_query):
    try:
        os.mkdir(TMPDIR)
    except OSError:
        pass

    # Documents are identified by and id
    # The reference calls it md5, which suggests that this id might be the generated md5 hash value of the pdfs
    id = url[url.rfind("/")+1:url.rfind(".")]
    fromPage = 1
    while True:
        lastFromPage = fromPage - 1  # To preserve the number of retrieved pages for error displaying
        fromPage, end = download_one_block(id, fromPage, resolution, pages_per_query)

        # If no data was returned, all of the three (totalPage, fromPage, toPage) values will be zero
        # Which is impossible in normal circumstances and indicates an error
        if fromPage == 0:
            print("ERROR while downloading, the document might be behind a paywall. "
                  "Only the first " + str(lastFromPage) + " pages were downloaded")

        fromPage += 1
        if end:
            break

    # Creating final pdf file
    with open(output_name, "wb") as f:
        f.write(img2pdf.convert(filenames))

    shutil.rmtree(TMPDIR)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download documents from wenku.baidu.com")
    parser.add_argument("url", help="The url to download from")
    parser.add_argument("-o", "--output", help="The name of the desired .pdf file", default="OUTPUT.pdf")
    parser.add_argument("-r", "--resolution", type=int, help="The resolution of the generated image files in dpi", default=240)
    parser.add_argument("-p", "--pages_per_query", type=int, help="How many pages should be requested with each network query", default=5)
    args = parser.parse_args()
    download_pdf(args.url, args.output, args.resolution, args.pages_per_query)
