# apod
An ASCII-style rendering of the [Astronomy Picture of the Day](https://apod.nasa.gov/apod/astropix.html) at nasa.gov. This retrieves the picture of the day, downsamples it to the size of your terminal window, and displays it in ASCII-style Unicode blocks with ANSI 24-bit color codes. I like it as a splash screen for a new terminal window.

Enjoy it. It's fun. Tested in POP!_OS 22.04. Written in python 3.10.

## Installation

It's a python package:

```
$ python3 -m pip install termapod
```

Or, install from a local clone of the repo:

```
$ git clone https://github.com/spacemeat/termapod
$ cd termapod
$ python3 -m pip install .
```

## Running it

It should install as a runnable program.

```
$ termapod
```

Unless `--no-save-cache` is passed as an argument, the image is downloaded to `~/.config/termapod/image-<date>.jpg`, with caption saved to `~/.config/termapod/caption.txt`. This cache image is used unless `--no-cache` is given as an argument. Whenever a new image is cached, the previous image and caption are deleted, so as not to fill up your precious storage.
