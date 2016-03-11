from PyPDF2 import PdfFileReader
from PIL import Image
import os
from io import BytesIO


def xobjects(pdf):
    for page in pdf.pages:
        try:
            xobject = page["/Resources"]["/XObject"].getObject()
        except KeyError:
            continue
        for x_id in xobject:
            yield x_id, xobject[x_id]


def default_name(i, ext, xobject):
    return "image-{i:0>3}.{ext}".format(i=i, ext=ext)


def default_guard(xobject):
    w = xobject["/Width"]
    h = xobject["/Height"]

    return w >= 100 and h >= 100


def extract_images(path, guard_fn=default_guard, name_fn=default_name,
                   limit=10, dirname=None):
    image_paths = []
    if not dirname:
        dirname = os.path.dirname(path)
    with open(path, "rb") as infile:
        pdf = PdfFileReader(infile)
        for i, (xid, xobject) in enumerate(xobjects(pdf)):
            if xobject["/Subtype"] != "/Image":
                continue

            if guard_fn and not guard_fn(xobject):
                continue

            filter = xobject["/Filter"]

            if filter == "/FlateDecode":
                data = xobject.getData()
                mode = "RGB" if xobject["/ColorSpace"] == "/DeviceRGB" else "P"
                width = xobject["/Width"]
                height = xobject["/Height"]
                img = Image.frombytes(mode, (width, height), data)
                filename = os.path.join(dirname, name_fn(i, "png", xobject))
                img.save(filename)
                image_paths.append(filename)
            elif filter == "/DCTDecode":
                filename = os.path.join(dirname, name_fn(i, "jpg", xobject))
                data = xobject._data
                img = Image.open(BytesIO(data))
                img.save(filename)
                image_paths.append(filename)
            else:
                continue

            if len(image_paths) == limit:
                break

    return image_paths
