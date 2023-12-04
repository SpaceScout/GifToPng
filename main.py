import os
import sys
import time

import cv2

from PIL import Image
from art import *

png_ready = os.path.normpath(os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') + r"\PNG CONVERTOR")
os.makedirs(png_ready, exist_ok=True)


def convertVideo(path):
    print("Converting Video")
    video = cv2.VideoCapture(path)
    success, frame = video.read()
    frame_count = 0
    savePath = png_ready + rf"\{os.path.basename(path)}"
    print(savePath)
    os.makedirs(savePath, exist_ok=True)
    while success:
        print("saving %s frame %d" % (path, frame_count))
        cv2.imwrite(savePath + rf"\{frame_count}.png", frame)
        success, frame = video.read()
        frame_count += 1
    tprint("DONE!")
    time.sleep(1)
    video.release()


def analyseImage(path):
    """
    Pre-process pass over the image to determine the mode (full or additive).
    Necessary as assessing single frames isn't reliable. Need to know the mode
    before processing all frames.
    """
    im = Image.open(path)
    results = {
        'size': im.size,
        'mode': 'full',
    }
    try:
        while True:
            if im.tile:
                tile = im.tile[0]
                update_region = tile[1]
                update_region_dimensions = update_region[2:]
                if update_region_dimensions != im.size:
                    results['mode'] = 'partial'
                    break
            im.seek(im.tell() + 1)
    except EOFError:
        pass
    return results


def convertGif(path):
    print("Converting Gif")
    """
    Iterate the GIF, extracting each frame.
    """
    mode = analyseImage(path)['mode']

    im = Image.open(path)

    i = 0
    p = im.getpalette()
    last_frame = im.convert('RGBA')

    try:
        while True:
            print("saving %s (%s) frame %d, %s %s" % (path, mode, i, im.size, im.tile))
            '''
            If the GIF uses local colour tables, each frame will have its own palette.
            If not, we need to apply the global palette to the new frame.
            '''
            if not im.getpalette():
                im.quantize(dither=Image.NONE).putpalette(p)
            new_frame = Image.new('RGBA', im.size)
            '''
            Is this file a "partial"-mode GIF where frames update a region of a different size to the entire image?
            If so, we need to construct the new frame by pasting it on top of the preceding frames.
            '''
            if mode == 'partial':
                new_frame.paste(last_frame)

            new_frame.paste(im, (0, 0), im.convert('RGBA'))

            savePath = png_ready + r"\%s" % (''.join(os.path.basename(path).split('.')[:-1]))
            print(savePath)
            os.makedirs(png_ready, exist_ok=True)
            new_frame.save(savePath + r'\%s-%d.png' % (''.join(os.path.basename(path).split('.')[:-1]), i), 'PNG')

            i += 1
            last_frame = new_frame
            im.seek(im.tell() + 1)
    except EOFError:
        pass
    finally:
        tprint("DONE!")
        input()


def main():
    path = sys.argv[1]
    if path.endswith('.gif'):
        convertGif(path)
    elif path.endswith('.mp4'):
        convertVideo(path)
    else:
        tprint("EBLAN?")
        time.sleep(1)


if __name__ == "__main__":
    main()
