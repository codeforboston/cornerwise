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

    return w >= 100 and h >= 100


def get_images(path, guard_fn=default_guard):
    with open(path, "rb") as infile:
        pdf = PdfFileReader(infile)
        for (xid, xobject) in xobjects(pdf):
            if xobject["/Subtype"] != "/Image":
                continue

            if guard_fn and not guard_fn(xobject):
                continue

            filter = xobject["/Filter"]

            if filter == "/FlateDecode":
                data = xobject.getData()
                mode = "RGB" if xobject["/ColorSpace"] == "/DeviceRGB" else "P"
                yield (Image.frombytes(mode, (xobject["/Width"], xobject["/Height"]), data), "png")
            elif filter == "/DCTDecode":
                data = xobject._data
                yield (Image.open(BytesIO(data)), "jpeg")
            else:
                continue


def extract_images(path, filter_fn=default_guard, limit=10):
    limit -= 1
    for i, (image, ext) in enumerate(get_images(path, filter_fn)):
        image_out = BytesIO()
        image.save(image_out, ext)
        yield (image_out, ext)

        if i == limit:
            break

