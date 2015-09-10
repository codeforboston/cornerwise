from collections import namedtuple
import subprocess

ImageInfo = namedtuple("ImageInfo", "name type width height depth space size")

def image_info(image_path):
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

    return w > 100 and h > 100
