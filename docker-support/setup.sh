#!/bin/bash

apt-get update
apt-get install -y libgdal-dev binutils gdal-bin
apt-get install -y xpdf-utils

export CPLUS_INCLUDE_PATH=/usr/include/gdal
export C_INCLUDE_PATH=/usr/include/gdal
pip3 install -r /support/requirements.txt

sh /support/export_parcels.sh
rm -r /shapefiles
