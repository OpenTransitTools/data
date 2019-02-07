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
     PostGIS:  bin/gtfsdb-load --is_geospatial --schema ott --database_url postgresql://postgres@127.0.0.1:5432/postgres http://developer.trimet.org/schedule/gtfs.zip



Future thoughts:
  1. gtfs services ... or transit services ... or services ... or ????
  1. need to have both DAO and service under same roof
  1. swagger ???
  1. this needs to be a lot simplier
  1. have otp TI services ... shouldn't they be alongside these
  1. what about https://github.com/openfaas/faas
  1. what about Docker ?
  1. what about multiple agencies
  1. new gtfsdb and gtfsdb and SUM services:
    IDEAS:
      a. gtfsdb.shape_stops table ... tell me what stops belong to a given shape / pattern
      b. route_direction_stops table ... what stops belong to a given direction (think we have that)
      c. how can we animate where a bus is based on route and schedule time ... what table structure?
      d. other tables?

    MAP:
      a. create a map app to show current routes, stops and RT vehicles
      b. Gatsby ?
      c...

