#!/bin/bash

apt-get update
apt-get install -y python3.4 python3-pip
apt-get install -y postgresql-9.3-postgis-2.1 postgis-doc postgis
apt-get install -y libgdal-dev binutils gdal-bin redis-server

export CPLUS_INCLUDE_PATH=/usr/include/gdal
export C_INCLUDE_PATH=/usr/include/gdal
pip3 install -r /support/requirements.txt

# Postgres setup
service postgresql start
su postgres -- <<EOF
createdb citydash
psql citydash -q -f pg_setup.sql
EOF

sh /support/export_parcels.sh

# Allow password authentication from local Postgres connections
sed -i '75 a\
local citydash postgres password' /etc/postgresql/9.3/main/pg_hba.conf
