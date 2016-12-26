=======
csvjson
=======

Description
===========

Converts a CSV file into JSON or GeoJSON (depending on flags)::

    usage: csvjson [-h] [-d DELIMITER] [-t] [-q QUOTECHAR] [-u {0,1,2,3}] [-b]
                   [-p ESCAPECHAR] [-z MAXFIELDSIZE] [-e ENCODING] [-S] [-v] [-l]
                   [--zero] [-i INDENT] [-k KEY] [--lat LAT] [--lon LON]
                   [--crs CRS] [--stream]
                   [FILE]

    Convert a CSV file into JSON (or GeoJSON).

    positional arguments:
      FILE                  The CSV file to operate on. If omitted, will accept
                            input on STDIN.

    optional arguments:
      -h, --help            show this help message and exit
      -i INDENT, --indent INDENT
                            Indent the output JSON this many spaces. Disabled by
                            default.
      -k KEY, --key KEY     Output JSON as an array of objects keyed by a given
                            column, KEY, rather than as a list. All values in the
                            column must be unique. If --lat and --lon are also
                            specified, this column will be used as GeoJSON Feature
                            ID.
      --lat LAT             A column index or name containing a latitude. Output
                            will be GeoJSON instead of JSON. Only valid if --lon
                            is also specified.
      --lon LON             A column index or name containing a longitude. Output
                            will be GeoJSON instead of JSON. Only valid if --lat
                            is also specified.
      --crs CRS             A coordinate reference system string to be included
                            with GeoJSON output. Only valid if --lat and --lon are
                            also specified.
      --stream              Output JSON as a stream of newline-separated objects,
                            rather than an as an array.

See also: :doc:`../common_arguments`.

Examples
========

Convert veteran's education dataset to JSON keyed by state abbreviation::

    csvjson -k "State Abbreviate" -i 4 examples/realdata/FY09_EDU_Recipients_by_State.csv

Results in a JSON document like::

    {
        [...]
        "WA": {
            "State Name": "WASHINGTON", 
            "State Abbreviate": "WA", 
            "Code": 53.0, 
            "Montgomery GI Bill-Active Duty": 7969.0, 
            "Montgomery GI Bill- Selective Reserve": 769.0, 
            "Dependents' Educational Assistance": 2192.0, 
            "Reserve Educational Assistance Program": 549.0, 
            "Post-Vietnam Era Veteran's Educational Assistance Program": 13.0, 
            "TOTAL": 11492.0, 
            "": null
        }, 
        [...]
    }

Converting locations of public art into GeoJSON::

    csvjson --lat latitude --lon longitude --k slug --crs EPSG:4269 -i 4 examples/test_geo.csv

Results in a GeoJSON document like::

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
            [...]
        ], 
        "crs": {
            "type": "name", 
            "properties": {
                "name": "EPSG:4269"
            }
        }
    }

