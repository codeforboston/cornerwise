#!/bin/bash

if [ -d /data/shapefiles ]; then
    SHAPEFILE_DIR="/data/shapefiles"
elif [ -d /shapefiles ]; then
    SHAPEFILE_DIR="/shapefiles"
fi

if [ -n "$SHAPEFILE_DIR" ]; then
    shp2pgsql -c -s 97406 -g shape $SHAPEFILE_DIR/M274TaxPar.shp parcel | psql -q -U cornerwise -d cornerwise
else
    echo "No shapefiles found."
    exit 1
fi
