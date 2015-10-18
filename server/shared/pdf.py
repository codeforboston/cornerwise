import datetime, os, re, subprocess

from .files_metadata import published_date

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
