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


def default_name(i, ext, img):
    return "image-{i:0>3}.{ext}".format(i=i, ext=ext)


def default_guard(xobject):
    w = xobject["/Width"]
    h = xobject["/Height"]

    return w >= 150 and h >= 150


def get_images(path, guard_fn=default_guard):
    with open(path, "rb") as infile:
        pdf = PdfFileReader(infile)
        for (xid, xobject) in xobjects(pdf):
            if xobject["/Subtype"] != "/Image":
                continue

            if guard_fn and not guard_fn(xobject):
                continue

            filter = xobject["/Filter"]
            width = xobject["/Width"]
            height = xobject["/Height"]

            if filter == "/FlateDecode":
                data = xobject.getData()
                mode = "RGB" if xobject["/ColorSpace"] == "/DeviceRGB" else "P"
                yield (Image.frombytes(mode, (width, height), data), "png", width, height)
            elif filter == "/DCTDecode":
                data = xobject._data
                width = x
                yield (Image.open(BytesIO(data)), "jpeg", width, height)
            else:
                continue


def extract_images(path, filter_fn=default_guard, limit=10):
    limit -= 1
    for i, (image, ext, w, h) in enumerate(get_images(path, filter_fn)):
        image_out = BytesIO()
        image.save(image_out, ext)
        yield (image_out, ext, w, h)

        if i == limit:
            break

