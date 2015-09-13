Running Tasks
==========

For now, tasks must be run manually:

From the container's bash prompt (see SETUP.org), launch Django's Python 

```bash
cd app
./manage.py shell

```

To run, for example, the scrape task and scrape all proposals since
August 1, 2015:

```python
from proposal.models import *
from proposal import tasks
from datetime import datetime

tasks.scrape_reports_and_decisions(since=datetime(2015, 8, 1))
```

Automated Tasks
==========

Scraping Reports and Decisions
----------

Function: `scrape_reports_and_decisions`

The [Reports and Decisions](www.somervillema.gov/departments/planning-board/reports-and-decisions/robots) page is where the City of Somerville
Planning Board posts information about past and ongoing zoning changes,
etc. The scraper task parses the HTML on that page and extracts data
from the table. It creates a proposal.models.Proposal object for each
entry in the table and associates a proposal.models.Document object for
each linked document in the entry's fields.

Fetch Document
----------

Function: `fetch_document`

Accepts as its argument a Document object constructed by the
scraper. Downloads the document to a new subdirectory in the server's
media directory (MEDIA_ROOT/doc/<id>/).

Extract Content
----------

Accepts a Document object. Extracts images to MEDIA_ROOT/doc/<id>/images
and text to MEDIA_ROOT/doc/<id>/text.txt. Creates a new
proposal.models.Image objects for each 'interesting' image 

Generate Thumbnail
----------

Accepts a proposal.models.Image object and generates a thumbnail that
fits to the dimensions specified in cornerwise.settings.THUMBNAIL_DIM.
