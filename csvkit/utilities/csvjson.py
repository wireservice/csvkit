#!/usr/bin/env python

import codecs

try:
    from collections import OrderedDict
    import json
except ImportError:
    from ordereddict import OrderedDict
    import simplejson as json

import six

from csvkit import CSVKitReader
from csvkit.cli import CSVKitUtility, match_column_identifier
from csvkit.exceptions import NonUniqueKeyColumnException

class CSVJSON(CSVKitUtility):
    description = 'Convert a CSV file into JSON (or GeoJSON).'
    override_flags = ['H']

    def add_arguments(self):
        self.argparser.add_argument('-i', '--indent', dest='indent', type=int, default=None,
            help='Indent the output JSON this many spaces. Disabled by default.')
        self.argparser.add_argument('-k', '--key', dest='key', type=str, default=None,
            help='Output JSON as an array of objects keyed by a given column, KEY, rather than as a list. All values in the column must be unique. If --lat and --lon are also specified, this column will be used as GeoJSON Feature ID.')
        self.argparser.add_argument('--lat', dest='lat', type=str, default=None,
            help='A column index or name containing a latitude. Output will be GeoJSON instead of JSON. Only valid if --lon is also specified.')
        self.argparser.add_argument('--lon', dest='lon', type=str, default=None,
            help='A column index or name containing a longitude. Output will be GeoJSON instead of JSON. Only valid if --lat is also specified.')
        self.argparser.add_argument('--crs', dest='crs', type=str, default=None,
            help='A coordinate reference system string to be included with GeoJSON output. Only valid if --lat and --lon are also specified.')

        self.argparser.add_argument('--stream', dest='streamOutput', action='store_true',
            help='Output JSON as a stream of newline-separated objects, rather than an as an array.')

    def main(self):
        if six.PY2:
            stream = codecs.getwriter('utf-8')(self.output_file)
        else:
            stream = self.output_file 
        
        json_kwargs = {
            'ensure_ascii': False,
            'indent': self.args.indent,
        }

        if six.PY2:
            json_kwargs['encoding'] = 'utf-8'
        
        def dump_json (data,newline=False): 
            json.dump(data, stream, **json_kwargs) 
            if newline: stream.write("\n")
            
        """
        Convert CSV to JSON. 
        """
        if self.args.lat and not self.args.lon:
            self.argparser.error('--lon is required whenever --lat is specified.')

        if self.args.lon and not self.args.lat:
            self.argparser.error('--lat is required whenever --lon is specified.')

        if self.args.crs and not self.args.lat:
            self.argparser.error('--crs is only allowed when --lat and --lon are also specified.')
        
        if self.args.streamOutput and (self.args.lat or self.args.lon or self.args.key):
            self.argparser.error('--stream is only allowed if --lat, --lon and --key are not specified.')

        rows = CSVKitReader(self.input_file, **self.reader_kwargs)
        column_names = next(rows)

        # GeoJSON
        if self.args.lat and self.args.lon:
            features = []
            min_lon = None
            min_lat = None
            max_lon = None
            max_lat = None

            lat_column = match_column_identifier(column_names, self.args.lat, self.args.zero_based)
            lon_column = match_column_identifier(column_names, self.args.lon, self.args.zero_based)

            if self.args.key:
                id_column = match_column_identifier(column_names, self.args.key, self.args.zero_based)
            else:
                id_column = None

            for row in rows:
                feature = OrderedDict()
                feature['type'] = 'Feature'
                properties = OrderedDict()
                geoid = None
                lat = None
                lon = None

                for i, c in enumerate(row):
                    if i == lat_column:
                        try:
                            lat = float(c)
                        except ValueError:
                            lat = None

                        if min_lat is None or lat < min_lat:
                            min_lat = lat

                        if max_lat is None or lat > max_lat:
                            max_lat = lat
                    elif i == lon_column:
                        try:
                            lon = float(c)
                        except ValueError:
                            lon = None

                        if min_lon is None or lon < min_lon:
                            min_lon = lon

                        if max_lon is None or lon > max_lon:
                            max_lon = lon
                    elif id_column is not None and i == id_column:
                        geoid = c
                    else:
                        properties[column_names[i]] = c

                if id_column is not None:
                    feature['id'] = geoid

                feature['geometry'] = OrderedDict([ 
                    ('type', 'Point'),
                    ('coordinates', [lon, lat])
                ])

                feature['properties'] = properties

                features.append(feature)

            output = OrderedDict([
                ('type', 'FeatureCollection'),
                ('bbox', [min_lon, min_lat, max_lon, max_lat]),
                ('features', features)
            ])

            if self.args.crs:
                output['crs'] = OrderedDict([ 
                    ('type', 'name'),
                    ('properties', {
                        'name': self.args.crs
                    })
                ])
            dump_json(output)
        # Keyed JSON
        elif self.args.key:
            output = OrderedDict()
            
            for row in rows:
                data = OrderedDict()

                for i, column in enumerate(column_names):
                    data[column] = row[i]

                k = data[self.args.key]

                if k in output:
                    raise NonUniqueKeyColumnException('Value %s is not unique in the key column.' % six.text_type(k))

                output[k] = data
            dump_json(output)
        # Boring JSON
        else:
            output = []
            for row in rows:
                data = OrderedDict()

                for i, column in enumerate(column_names):
                    try:
                        data[column] = row[i]
                    except IndexError:
                        data[column] = None
                if(self.args.streamOutput):
                    dump_json(data,newline=True)
                else:
                    output.append(data)
            if not self.args.streamOutput:
                dump_json(output)



def launch_new_instance():
    utility = CSVJSON()
    utility.main()
    
if __name__ == "__main__":
    launch_new_instance()

