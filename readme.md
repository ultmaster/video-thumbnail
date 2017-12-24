# Thumbnails

![](example.jpg)

## Installation

Installing dependencies can be a really painful experience, painful enough to scare you away.

You should install the following packages:

+ Python 3 (of course)
+ Pillow (PIL)
+ ffmpeg
+ PyAV

If you have managed to install all above, congratulations! Enjoy~!


## Usage

The only thing that is currently very much needed to configure is the font. You should carefully choose a truetype font,
something like `*.ttf` and put it in the current directory, specify the font name in `thumbnail.py`. Done!

You may notice that files are renamed and some temporary files are created when running the program. This is due to the
ridiculous bug in PyAV which nobody cares. I would really appreciate it if someone could repair this bug.
