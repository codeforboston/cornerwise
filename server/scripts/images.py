from collections import namedtuple
import os
import subprocess

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
        raise Exception("Error in command: {error}"\
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

def make_thumbnail(image_path, percent=None, fit=None, dim=None, dest_file=None):
    """Uses the 'convert' command line utility to resize the image at the
    given path. """

    if percent:
        resize = "{}%".format(percent)
    else:
        if fit:
            w, h = dimensions(image_path)
            fit_w, fit_h = fit

            if w > h:
                dim = (fit_w, h/w*fit_w)
            else:
                dim = (w/h*fit_h, fit_h)

        if dim:
            resize = "{dim[0]}x{dim[1]}".format(dim=dim)
        else:
            raise Exception("")

    if not dest_file:
        image_dir = os.path.dirname(image_path)
        image_name = os.path.basename(image_path)
        dest_file = os.path.join(image_dir, "thumb_" + image_name)

    subprocess.call(["convert", "-resize", resize, image_path, dest_file])

    return dest_file
