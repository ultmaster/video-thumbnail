import os
import random
import re
import string
import subprocess
import traceback

import av
from PIL import Image, ImageFont, ImageDraw

# Tune these settings...
IMAGE_PER_ROW = 5
IMAGE_ROWS = 7
PADDING = 5
FONT_SIZE = 16
IMAGE_WIDTH = 1536
FONT_NAME = "HelveticaNeue.ttc"
BACKGROUND_COLOR = "#fff"
TEXT_COLOR = "#000"
TIMESTAMP_COLOR = "#fff"


def get_time_display(time):
    return "%02d:%02d:%02d" % (time // 3600, time % 3600 // 60, time % 60)


def get_random_filename(ext):
    return ''.join([random.choice(string.ascii_lowercase) for _ in range(20)]) + ext


def create_thumbnail(filename):
    print('Processing:', filename)

    jpg_name = '%s.jpg' % filename
    if os.path.exists(jpg_name):
        print('Thumbnail assumed exists!')
        return

    _, ext = os.path.splitext(filename)
    random_filename = get_random_filename(ext)
    random_filename_2 = get_random_filename(ext)
    print('Rename as %s to avoid decode error...' % random_filename)
    try:
        os.rename(filename, random_filename)
        try:
            container = av.open(random_filename)
        except UnicodeDecodeError:
            print('Metadata decode error. Try removing all the metadata...')
            subprocess.run(["ffmpeg", "-i", random_filename, "-map_metadata", "-1", "-c:v", "copy", "-c:a", "copy",
                            random_filename_2], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            container = av.open(random_filename_2)

        metadata = [
            "File name: %s" % filename,
            "Size: %d bytes (%.2f MB)" % (container.size, container.size / 1048576),
            "Duration: %s" % get_time_display(container.duration // 1000000),
        ]

        start = min(container.duration // (IMAGE_PER_ROW * IMAGE_ROWS), 5 * 1000000)
        end = container.duration - start
        time_marks = []
        for i in range(IMAGE_ROWS * IMAGE_PER_ROW):
            time_marks.append(start + (end - start) // (IMAGE_ROWS * IMAGE_PER_ROW - 1) * i)

        images = []
        for idx, mark in enumerate(time_marks):
            container.seek(mark)
            for frame in container.decode(video=0):
                images.append((frame.to_image(), mark // 1000000))
                break

        width, height = images[0][0].width, images[0][0].height
        metadata.append('Video: (%dpx, %dpx), %dkbps' % (width, height, container.bit_rate // 1024))

        img = Image.new("RGB", (IMAGE_WIDTH, IMAGE_WIDTH), BACKGROUND_COLOR)
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(FONT_NAME, FONT_SIZE)
        _, min_text_height = draw.textsize("\n".join(metadata), font=font)
        image_width_per_img = int(round((IMAGE_WIDTH - PADDING) / IMAGE_PER_ROW)) - PADDING
        image_height_per_img = int(round(image_width_per_img / width * height))
        image_start_y = PADDING * 2 + min_text_height

        img = Image.new("RGB", (IMAGE_WIDTH, image_start_y + (PADDING + image_height_per_img) * IMAGE_ROWS),
                        BACKGROUND_COLOR)
        draw = ImageDraw.Draw(img)
        draw.text((PADDING, PADDING), "\n".join(metadata), TEXT_COLOR, font=font)
        for idx, snippet in enumerate(images):
            y = idx // IMAGE_PER_ROW
            x = idx % IMAGE_PER_ROW
            new_img, timestamp = snippet
            new_img = new_img.resize((image_width_per_img, image_height_per_img), resample=Image.BILINEAR)
            x = PADDING + (PADDING + image_width_per_img) * x
            y = image_start_y + (PADDING + image_height_per_img) * y
            img.paste(new_img, box=(x, y))
            draw.text((x + PADDING, y + PADDING), get_time_display(timestamp), TIMESTAMP_COLOR, font=font)

        img.save(jpg_name)
        print('OK!')
    except Exception as e:
        traceback.print_exc()
    finally:
        os.rename(random_filename, filename)
        if os.path.exists(random_filename_2):
            os.remove(random_filename_2)


if __name__ == "__main__":
    p = input("Input the path you want to process: ")
    p = os.path.abspath(p)

    for root, dirs, files in os.walk(p):
        print('Switch to root %s...' % root)
        os.chdir(root)
        for file in files:
            ext_regex = r"\.(mov|mp4|mpg|mov|mpeg|flv|wmv|avi|mkv)$"
            if re.search(ext_regex, file, re.IGNORECASE):
                create_thumbnail(file)
