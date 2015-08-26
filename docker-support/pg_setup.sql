DO
$body$
BEGIN
   IF NOT EXISTS (
      SELECT *
      FROM   pg_catalog.pg_user
      WHERE  usename = 'cornerwise') THEN

      CREATE USER cornerwise WITH LOGIN;
   END IF;
END
$body$;

GRANT ALL PRIVILEGES ON DATABASE cornerwise TO cornerwise;

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
INSERT INTO spatial_ref_sys (srid, auth_name, auth_srid, proj4text, srtext) values ( 97406, 'sr-org', 7406, '+proj=lcc +lat_1=41.71666666666667 +lat_2=42.68333333333333 +lat_0=41 +lon_0=-71.5 +x_0=200000 +y_0=750000 +datum=NAD83 +units=m +no_defs ', 'PROJCS["NAD_1983_StatePlane_Massachusetts_Mainland_FIPS_2001",GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Lambert_Conformal_Conic"],PARAMETER["False_Easting",200000.0],PARAMETER["False_Northing",750000.0],PARAMETER["Central_Meridian",-71.5],PARAMETER["Standard_Parallel_1",41.71666666666667],PARAMETER["Standard_Parallel_2",42.68333333333333],PARAMETER["Latitude_Of_Origin",41.0],UNIT["Meter",1.0]]');
