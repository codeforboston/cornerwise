#!/bin/bash

if [ -d /data/shapefiles ]; then
    SHAPEFILE_DIR="/data/shapefiles"
elif [ -d /shapefiles ]; then
    SHAPEFILE_DIR="/shapefiles"
fi

if [ -n "$SHAPEFILE_DIR" ]; then
    shp2pgsql -c -g shape $SHAPEFILE_DIR/M274TaxPar.shp parcel | psql -q -U citydash -d citydash
else
    echo "No shapefiles found."
    exit 1
fi
