import datetime, os, re, subprocess

from .files import published_date, encoding, extract_text

@published_date.add("pdf")
def published_date(path):
    proc = subprocess.Popen(["pdfinfo", path],
                            stderr=subprocess.PIPE,
                            stdout=subprocess.PIPE)
    out, err = proc.communicate()
    m = re.search(r"CreationDate:\s+(.*?)\n", out.decode("UTF-8"))

    if m:
        datestr = m.group(1)
        return datetime.strptime(datestr, "%c")

    return datetime.fromtimestamp(os.path.getmtime(path))


@encoding.add("pdf")
def encoding(_):
    return "ISO-8859-9"


@extract_text.add("pdf")
def extract_text(path, output_path):
    status = subprocess.call(["pdftotext", "-enc", encoding(path), path,
                              output_path])
    return not status
