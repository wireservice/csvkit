=======
csvjson
=======

Description
===========

Converts a CSV file into JSON or GeoJSON (depending on flags):

.. code-block:: none

   usage: csvjson [-h] [-d DELIMITER] [-t] [-q QUOTECHAR] [-u {0,1,2,3}] [-b]
                  [-p ESCAPECHAR] [-z FIELD_SIZE_LIMIT] [-e ENCODING] [-L LOCALE]
                  [-S] [--blanks] [--null-value NULL_VALUES [NULL_VALUES ...]]
                  [--date-format DATE_FORMAT] [--datetime-format DATETIME_FORMAT]
                  [-H] [-K SKIP_LINES] [-v] [-l] [--zero] [-V] [-i INDENT]
                  [-k KEY] [--lat LAT] [--lon LON] [--type TYPE]
                  [--geometry GEOMETRY] [--crs CRS] [--no-bbox] [--stream]
                  [-y SNIFF_LIMIT] [-I]
                  [FILE]

   Convert a CSV file into JSON (or GeoJSON).

   positional arguments:
     FILE                  The CSV file to operate on. If omitted, will accept
                           input as piped data via STDIN.

   optional arguments:
     -h, --help            show this help message and exit
     -i INDENT, --indent INDENT
                           Indent the output JSON this many spaces. Disabled by
                           default.
     -k KEY, --key KEY     Output JSON as an object keyed by a given column, KEY,
                           rather than as an array. All column values must be
                           unique. If --lat and --lon are specified, this column
                           is used as the GeoJSON Feature ID.
     --lat LAT             A column index or name containing a latitude. Output
                           will be GeoJSON instead of JSON. Requires --lon.
     --lon LON             A column index or name containing a longitude. Output
                           will be GeoJSON instead of JSON. Requires --lat.
     --type TYPE           A column index or name containing a GeoJSON type.
                           Output will be GeoJSON instead of JSON. Requires --lat
                           and --lon.
     --geometry GEOMETRY   A column index or name containing a GeoJSON geometry.
                           Output will be GeoJSON instead of JSON. Requires --lat
                           and --lon.
     --crs CRS             A coordinate reference system string to be included
                           with GeoJSON output. Requires --lat and --lon.
     --no-bbox             Disable the calculation of a bounding box.
     --stream              Output JSON as a stream of newline-separated objects,
                           rather than an as an array.
     -y SNIFF_LIMIT, --snifflimit SNIFF_LIMIT
                           Limit CSV dialect sniffing to the specified number of
                           bytes. Specify "0" to disable sniffing entirely, or
                           "-1" to sniff the entire file.
     -I, --no-inference    Disable type inference (and --locale, --date-format,
                           --datetime-format, --no-leading-zeroes) when parsing
                           the input.

See also: :doc:`../common_arguments`.

Examples
========

Convert veteran's education dataset to JSON keyed by state abbreviation:

.. code-block:: console

   $ csvjson -k "State Abbreviate" -i 4 examples/realdata/FY09_EDU_Recipients_by_State.csv
   {
       "AL": {
           "State Name": "ALABAMA",
           "State Abbreviate": "AL",
           "Code": 1.0,
           "Montgomery GI Bill-Active Duty": 6718.0,
           "Montgomery GI Bill- Selective Reserve": 1728.0,
           "Dependents' Educational Assistance": 2703.0,
           "Reserve Educational Assistance Program": 1269.0,
           "Post-Vietnam Era Veteran's Educational Assistance Program": 8.0,
           "TOTAL": 12426.0,
           "j": null
       },
       "...": {
           "...": "..."
       }
   }

Convert locations of public art into GeoJSON:

.. code-block:: console

   $ csvjson --lat latitude --lon longitude --k slug --crs EPSG:4269 -i 4 examples/test_geo.csv
   {
       "type": "FeatureCollection", 
       "bbox": [
           -95.334619, 
           32.299076986939205, 
           -95.250699, 
           32.351434
       ], 
       "crs": {
           "type": "name", 
           "properties": {
               "name": "EPSG:4269"
           }
       }, 
       "features": [
           {
               "type": "Feature", 
               "id": "dcl", 
               "geometry": {
                   "type": "Point", 
                   "coordinates": [
                       -95.30181, 
                       32.35066
                   ]
               }, 
               "properties": {
                   "title": "Downtown Coffee Lounge", 
                   "artist": null, 
                   "description": "In addition to being the only coffee shop in downtown Tyler, DCL also features regular exhibitions of work by local artists.", 
                   "install_date": null, 
                   "address": "200 West Erwin Street", 
                   "type": "Gallery", 
                   "photo_url": null, 
                   "photo_credit": null, 
                   "last_seen_date": "2012-03-30"
               }
           }, 
           {
               "...": "..."
           }
       ], 
       "crs": {
           "type": "name", 
           "properties": {
               "name": "EPSG:4269"
           }
       }
   }
