import re
import requests
import shutil

from PIL import Image

def get_image_url_and_caption():
    base_url = 'https://apod.nasa.gov/apod/'
    url = base_url + 'astropix.html'
    resp = requests.get(url)
    text = resp.text
    m = re.search(r'<IMG SRC=(.*)>', text)
    pat = '<IMG SRC=\"(.*?)\".*>'
    m = re.search(pat, text, re.S)
    img_url = ''
    if m is not None:
        img_url = base_url + m[1]
    pat = r'<b>(.*?)</b>'
    m = re.search(pat, text, re.S)
    caption = ''
    if m is not None:
        caption = m[1]
    return (img_url, caption.strip())

def get_image(url):
    im = Image.open(requests.get(url, stream=True).raw)
    return im

def resize_image(txy, im):
    cols, rows = txy
    size = cols, rows * 2 - 3
    print (f'{cols, rows * 2 - 3}')
    im.thumbnail(size, Image.Resampling.LANCZOS)

def convert_to_ansi(txy, im, caption):
    s = ''
    def fg(rgb):
        return f'\033[38;2;{rgb[0]};{rgb[1]};{rgb[2]}m'
    def bg(rgb):
        return f'\033[48;2;{rgb[0]};{rgb[1]};{rgb[2]}m'
    data = list(im.getdata())
    ch = '▀'
    w = im.width
    offs = int((txy[0] - w) / 2)
    for y in range(0, im.height - 1, 2):
        s += f'\033[0m\n{" " * offs}'
        for x in range(0, im.width):
            top_addr = y * w + x
            bot_addr = (y + 1) * w + x
            s += f'{fg(data[top_addr])}{bg(data[bot_addr])}{ch}'
    s += '\033[0m\n'
    offs = int((txy[0] - len(caption)) / 2)
    return f'{s}{" " * offs}{caption}'

def main():
    url, caption = get_image_url_and_caption()
    print (url)
    print (caption)
    if url:
        txy = shutil.get_terminal_size()
        im = get_image(url)
        resize_image(txy, im)
        s = convert_to_ansi(txy, im, caption)
        print (s)

if __name__ == "__main__":
    main()
