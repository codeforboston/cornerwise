Cornerwise
==========

Cornerwise is a Code for Boston project that aims to make it easier to
explore and visualize past, present, and pending changes to the built
environment.  For now, we're exploring better ways to show the contents
of Somerville, MA's Reports and Decisions page.

[Show me!](https://www.cornerwise.org)

In its current state, the project breaks more or less neatly into three
pieces:

- Somerville-specific code that ingests semi-structured data from the city's [Reports and Decisions](http://www.somervillema.gov/departments/planning-board/reports-and-decisions) page and transforms it into searchable structured data.
  
- A server that responds to queries over the imported proposal data
  
- A client-side viewer


Contributing
----------

We welcome contributions from people of all skillsets.  The best way to
get involved is by coming to a Tuesday
[Hack Night](http://www.meetup.com/Code-for-Boston/) and asking about the
project.  You can also take a look at our [issues](Issues) page to find
unclaimed issues marked *bite-sized* or *self-contained*.  These labels
refer to issues that are, respectively, small or that require minimal
familiarity with the existing codebase.


Getting Started
-----------

See the [Setup](SETUP.org) file for full instructions on getting
Cornerwise running locally.


Technologies used: 
----------

- [Docker](https://www.docker.com)
- [Python 3.5](https://www.python.org) and [Django](https://www.djangoproject.com)
- [Celery](http://www.celeryproject.org/)
- [PostGIS](http://postgis.net)
- HTML/CSS
- [Backbone.js](http://backbonejs.org), [jQuery](http://jquery.com/)
- [Leaflet](http://leafletjs.com/)
