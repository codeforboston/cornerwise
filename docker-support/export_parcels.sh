#!/bin/bash

if [ -d /data/shapefiles ]; then
    SHAPEFILE_DIR="/data/shapefiles"
elif [ -d /shapefiles ]; then
    
fi

if [ -n "$SHAPEFILE_DIR" ]; then
   
else
    echo "No shapefiles found."
    exit 1
fi
