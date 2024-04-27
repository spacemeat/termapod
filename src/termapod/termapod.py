''' Splats the Astronomy Picture of the Day to the terminal. Because what is life 
without fun?'''

from datetime import date
from os import makedirs
from pathlib import Path
import re
import shutil
import sys

from PIL import Image
import requests

from . import __version__

cache_dir = Path.home() / '.config/termapod'

def get_image_cache_path():
    ''' Gets the cached image's local path.'''
    today = date.today()
    image_cache_path = cache_dir / ('image-' + today.strftime('%Y-%m-%d') + '.jpg')
    return image_cache_path

def is_cached():
    ''' Returns if today's image has been cached.'''
    return get_image_cache_path().exists()

def get_image_and_caption():
    ''' Returns the APOD image either from cache or the web.'''
    if is_cached() and '--no-cache' not in sys.argv:
        im = Image.open(get_image_cache_path())
        with open(cache_dir / 'caption.txt', 'rt', encoding='utf-8') as f:
            caption = f.read()
        return (im, caption)

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
        caption = m[1].strip()

    im = Image.open(requests.get(img_url, stream=True).raw)

    if '--no-save-cache' not in sys.argv:
        # delete previous APODs
        for f in (f for f in cache_dir.glob('*.jpg') if f.is_file()):
            f.unlink()

        if not cache_dir.exists():
            makedirs(cache_dir)
        with open(cache_dir / 'caption.txt', 'wt', encoding='utf-8') as f:
            f.write(caption)

        im.save(get_image_cache_path(), 'JPEG')

    return (im, caption)

def resize_image(txy, im):
    ''' Resize the image to the available terminal elements, keeping aspect ratio.'''
    cols, rows = txy
    size = cols, rows * 2 - 3
    im.thumbnail(size, Image.Resampling.LANCZOS)

def convert_to_ansi(txy, im, caption):
    ''' Returns an ANSI-colored ASCII block made from the image and caption.'''
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
            bot_addr = top_addr + w
            s += f'{fg(data[top_addr])}{bg(data[bot_addr])}{ch}'
    s += '\033[0m\n'
    offs = int((txy[0] - len(caption)) / 2)
    return f'{s}{" " * offs}{caption}'

def main():
    ''' Meign.'''
    if len(sys.argv) > 1 and sys.argv[1] in ['-v', '--version']:
        print (f'termapod version {__version__}')
        return

    txy = shutil.get_terminal_size()
    im, caption = get_image_and_caption()
    if im:
        resize_image(txy, im)
        s = convert_to_ansi(txy, im, caption)
        print (s)

if __name__ == "__main__":
    main()
