#!/bin/bash

if [ -d /data/shapefiles ]; then
    su postgres -- <<EOF
shp2pgsql -cG -s 97406 -g shape /data/shapefiles/M274TaxPar.shp parcel | psql -q -d citydash
EOF
else
    echo "No shapefiles found."
    exit 1
fi
