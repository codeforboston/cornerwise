#!/bin/bash

apt-get update
apt-get install -y postgis-doc postgis
apt-get install -y libgdal-dev binutils gdal-bin redis-server

export CPLUS_INCLUDE_PATH=/usr/include/gdal
export C_INCLUDE_PATH=/usr/include/gdal
pip3 install -r /support/requirements.txt

# Postgres setup
service postgresql start
createuser -l citydash
createdb -O citydash citydash
psql -U postgres -q -f /support/pg_setup.sql citydash

sh /support/export_parcels.sh
rm -r /shapefiles

# Allow connections
sed -i '75 a\
local citydash all trust' /etc/postgresql/9.3/main/pg_hba.conf
