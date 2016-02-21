Running Tasks Manually
==========

The `CELERYBEAT_SCHEDULE` variable in `settings.py` specifies when certain tasks
run automatically, but you can also run tasks manually.

From the container's bash prompt (see SETUP.org), launch Django's Python 

```bash
cd app
./manage.py shell

```

To run, for example, the scrape task and scrape all proposals since
January 1, 2016:

```python
from proposal import tasks
from datetime import datetime
import pytz

since = pytz.timezone("US/Eastern").localize(datetime(2016, 1, 1))
tasks.fetch_proposals(since=since)
```

(Note that it expects a timezone-aware datetime.)

This will run `fetch_proposals` synchronously.  You will see a list of new
`Proposal` objects only once all the importers have run.

Asynchronous Execution
----------------------

In normal operation, tasks are sent by celery beat to the celery workers and
executed asynchronously. To run a task asynchronously on demand, you first have
to make sure you have a celery worker running (`app/start.sh` does
automatically).

```bash
./manage.py celery worker            # or:
./manage.py celery worker --detach   # daemonize worker
```

Then, at the Python shell:

```
from proposal import tasks
result = tasks.fetch_proposals.delay(since=None)
```

`result` will be a
[celery.result.AsyncResult](http://docs.celeryproject.org/en/latest/reference/celery.result.html)
instance. See the docs for details about how to 

`fetch_proposals` does not run in parallel, so there is no speed-up from running
it this way. Many other tasks, on the other hand, will farm out work across the
available workers --e.g., `process_documents` and similar.

Tasks
==========

Scraping Proposal Sources
----------

Function: `fetch_proposals`

The
[Reports and Decisions](www.somervillema.gov/departments/planning-board/reports-and-decisions/robots)
page is where the City of Somerville Planning Board posts information about past
and ongoing zoning changes, etc. The scraper task parses the HTML on that page
and extracts data from the table. It creates a proposal.models.Proposal object
for each entry in the table and associates a proposal.models.Document object for
each linked document in the entry's fields.

If you have a `SOCRATA_API_KEY` configured in
`server/cornerwise/local_settings.py`, this will also scrape data for the City
of Cambridge.


Fetch Document
----------

Function: `fetch_document`

Accepts as its argument a Document object constructed by the
scraper. Downloads the document to a new subdirectory in the server's
media directory (`MEDIA_ROOT/doc/<id>/`).

Extract Content
----------

Function: `extract_content`

Accepts a Document object. Extracts images to MEDIA_ROOT/doc/<id>/images
and text to MEDIA_ROOT/doc/<id>/text.txt. Creates a new
proposal.models.Image objects for each 'interesting' image 

Generate Thumbnail
----------

Function `generate_thumbnail`

Accepts a proposal.models.Image object and generates a thumbnail that
fits to the dimensions specified in cornerwise.settings.THUMBNAIL_DIM.
