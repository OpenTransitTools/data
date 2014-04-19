OTTDB
=====

database loader 4 transit (in python)

load gtfs
  0. install python 2.7, along with zc.buildout and easy_install, git
  1. git clone https://github.com/OpenTransitTools/ottdb.git
  2. cd ottdb
  3. buildout
  4. git update-index --assume-unchanged .pydevproject
  5. SQL LITE: bin/gtfsdb-load --database_url sqlite://gtfs.db http://developer.trimet.org/schedule/gtfs.zip
     - or -
     PostGIS:  bin/gtfsdb-load --is_geospatial --schema ott --database_url sqlite://gtfs.db http://developer.trimet.org/schedule/gtfs.zip
