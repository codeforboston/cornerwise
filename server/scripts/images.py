from collections import namedtuple
from io import BytesIO
import os
import subprocess

from PIL import Image

ImageInfo = namedtuple("ImageInfo", "name type width height depth space size")


def image_info(image_path):
    """Get information about the image at the given path. Requires the
'identify' command line utility.

    """
    p = subprocess.Popen(["identify", image_path],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)

    status = p.wait()

    if status:
        raise Exception("Error in command: {error}"
                        .format(error=p.stderr.read()))

    output = p.stdout.read().decode("utf-8")
    name, imgtype, dim, _, bit_depth, cspace, size, _ = output.split(" ", 7)

    w, h = dim.split("x")

    return ImageInfo(name, imgtype, int(w), int(h), bit_depth,
                     cspace, size)


def dimensions(image_path):
    info = image_info(image_path)
    return info.width, info.height


def is_interesting(image_path):
    """Heuristics to determine if the image at the given path is
'interesting'.

    """
    # Right now, the only measure of interestingness is the dimensions
    # of the image.
    w, h = dimensions(image_path)

    return w > 200 and h > 200


def pad(image, width, height, fill="black"):
    """Pads an image to `width` x `height` by adding space on all sides. Fills the
    additional pixels by the `fill` argument, which must be appropriate to the
    image mode.

    """
    w, h = image.size
    new_image = Image.new(image.mode, (width, height), fill)
    new_image.paste(image, ((w-width)/2, (h-height)/2))
    return new_image


def thumbnail_name(image_path):
    return "thumb_" + os.path.basename(image_path)


def make_thumbnail(image, percent=None, fit=None, dim=None, dest_file=None,
                   pad=False, pad_fill="black"):
    """Resizes an image to fit within given bounds, or scales it down to a percent
    of its original size. Returns a PIL Image.

    """

    if not isinstance(image, Image.Image):
        image = Image.open(image, "r")
    w, h = image.size

    if not percent:
        if fit:
            fit_w, fit_h = fit
            percent = min(fit_w/w, fit_h/h)

    if percent >= 1:
        # The original is smaller than the desired dimensions.
        resized = image
    else:
        resized = image.resize(
            (int(w*percent), int(h*percent)),
            Image.LANCZOS)
    return pad(image, fit_w, fit_h, pad_fill or "black") if pad else image


def image_data(image, ext="jpeg"):
    image_out = BytesIO()
    image.save(image_out, ext)
    image_out.seek(0)
    return image_out
