#!/bin/bash

apt-get update
apt-get install -y libgdal-dev binutils gdal-bin redis-server

cd /support
export CPLUS_INCLUDE_PATH=/usr/include/gdal
export C_INCLUDE_PATH=/usr/include/gdal
pip install -r requirements.txt

# Postgres setup
service postgresql start
su postgres -- <<EOF
createdb citydash
psql citydash -q -f pg_setup.sql
psql citydash -q -f import_parcels.sql
EOF

# Allow password authentication from local Postgres connections
sed -i '75 a\
local citydash postgres password' /etc/postgresql/9.3/main/pg_hba.conf
