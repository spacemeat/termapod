from datetime import date
from os import makedirs
from pathlib import Path
import re
import requests
import shutil

from PIL import Image

cache_dir = Path.home() / '.config/apod-cache'

def get_image_cache_path():
    today = date.today()
    image_cache_path = cache_dir / ('image-' + today.strftime('%Y-%m-%d') + '.jpg')
    return image_cache_path

def is_cached():
    return get_image_cache_path().exists()

def get_image_and_caption():
    if is_cached():
        im = Image.open(get_image_cache_path())
        with open(cache_dir / 'caption.txt', 'rt') as f:
            caption = f.read()
        return (im, caption)

    [f.unlink() for f in cache_dir.glob('*') if f.is_file()]

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

    if not cache_dir.exists():
        makedirs(cache_dir)
    im = Image.open(requests.get(img_url, stream=True).raw)
    with open(cache_dir / 'caption.txt', 'wt') as f:
        f.write(caption)

    im.save(get_image_cache_path(), 'JPEG')

    return (im, caption.strip())

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
    txy = shutil.get_terminal_size()
    im, caption = get_image_and_caption()
    print (caption)
    if im:
        resize_image(txy, im)
        s = convert_to_ansi(txy, im, caption)
        print (s)

if __name__ == "__main__":
    main()
