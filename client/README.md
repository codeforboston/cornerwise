cornerwise/client
==========

This directory contains all of the code for the site's web frontend.
When Cornerwise is run with Docker, it is mounted inside the container
as `/client`.  The Django app serves its contents at `/static/`.  For
example, using the standard dev setup, `css/app.css` would be served at
`http://localhost:3000/static/css/app.css`.
