#!/usr/bin/env python

import codecs
import datetime
import decimal
import sys

try:
    from collections import OrderedDict
    import json
except ImportError:
    from ordereddict import OrderedDict
    import simplejson as json

import agate
import six

from csvkit.cli import CSVKitUtility, match_column_identifier


class CSVJSON(CSVKitUtility):
    description = 'Convert a CSV file into JSON (or GeoJSON).'

    def add_arguments(self):
        self.argparser.add_argument('-i', '--indent', dest='indent', type=int,
                                    help='Indent the output JSON this many spaces. Disabled by default.')
        self.argparser.add_argument('-k', '--key', dest='key',
                                    help='Output JSON as an array of objects keyed by a given column, KEY, rather than as a list. All values in the column must be unique. If --lat and --lon are also specified, this column will be used as GeoJSON Feature ID.')
        self.argparser.add_argument('--lat', dest='lat',
                                    help='A column index or name containing a latitude. Output will be GeoJSON instead of JSON. Only valid if --lon is also specified.')
        self.argparser.add_argument('--lon', dest='lon',
                                    help='A column index or name containing a longitude. Output will be GeoJSON instead of JSON. Only valid if --lat is also specified.')
        self.argparser.add_argument('--type', dest='type',
                                    help='A column index or name containing a GeoJSON type. Output will be GeoJSON instead of JSON. Only valid if --lat and --lon are also specified.')
        self.argparser.add_argument('--geometry', dest='geometry',
                                    help='A column index or name containing a GeoJSON geometry. Output will be GeoJSON instead of JSON. Only valid if --lat and --lon are also specified.')
        self.argparser.add_argument('--crs', dest='crs',
                                    help='A coordinate reference system string to be included with GeoJSON output. Only valid if --lat and --lon are also specified.')
        self.argparser.add_argument('--no-bbox', dest='no_bbox', action='store_true',
                                    help='Disable the calculation of a bounding box.')
        self.argparser.add_argument('--stream', dest='streamOutput', action='store_true',
                                    help='Output JSON as a stream of newline-separated objects, rather than an as an array.')
        self.argparser.add_argument('-y', '--snifflimit', dest='sniff_limit', type=int,
                                    help='Limit CSV dialect sniffing to the specified number of bytes. Specify "0" to disable sniffing entirely.')
        self.argparser.add_argument('-I', '--no-inference', dest='no_inference', action='store_true',
                                    help='Disable type inference (and --locale, --date-format, --datetime-format) when parsing CSV input.')

    def __init__(self, args=None, output_file=None):
        super(CSVJSON, self).__init__(args, output_file)

        self.json_kwargs = {
            'ensure_ascii': False,
            'indent': self.args.indent,
        }

        # We need to do this stream dance here, because we aren't writing through agate.
        if six.PY2:
            self.stream = codecs.getwriter('utf-8')(self.output_file)
            self.json_kwargs['encoding'] = 'utf-8'
        else:
            self.stream = self.output_file

    def main(self):
        """
        Convert CSV to JSON.
        """

        self.validate_args()

        if self.additional_input_expected():
            if self.can_stream_output():
                sys.stderr.write('No input file or piped data provided. Waiting for standard input:\n')
            else:
                self.argparser.error('You must provide an input file or piped data.')

        if self.args.lat and self.args.lon:
            self.output_geojson()
        elif self.can_stream_output():
            self.output_ndjson_stream()
        else:
            self.output_json()

    def dump_json(self, data, newline=False):
        def default(obj):
            if isinstance(obj, (datetime.date, datetime.datetime)):
                return obj.isoformat()
            elif isinstance(obj, decimal.Decimal):
                return str(obj)
            raise TypeError('%s is not JSON serializable' % repr(obj))

        json.dump(data, self.stream, default=default, **self.json_kwargs)
        if newline:
            self.stream.write("\n")

    def can_stream_output(self):
        return (self.args.streamOutput
                and self.args.no_inference
                and not self.args.skip_lines
                and self.args.sniff_limit == 0)

    def validate_args(self):
        if self.args.lat and not self.args.lon:
            self.argparser.error('--lon is required whenever --lat is specified.')
        if self.args.lon and not self.args.lat:
            self.argparser.error('--lat is required whenever --lon is specified.')

        if self.args.crs and not self.args.lat:
            self.argparser.error('--crs is only allowed when --lat and --lon are also specified.')
        if self.args.type and not self.args.lat:
            self.argparser.error('--type is only allowed when --lat and --lon are also specified.')
        if self.args.geometry and not self.args.lat:
            self.argparser.error('--geometry is only allowed when --lat and --lon are also specified.')

        if self.args.streamOutput and (self.args.lat or self.args.lon or self.args.key):
            self.argparser.error('--stream is only allowed if --lat, --lon and --key are not specified.')

    def read_csv_to_table(self):
        return agate.Table.from_csv(
            self.input_file,
            skip_lines=self.args.skip_lines,
            sniff_limit=self.args.sniff_limit,
            column_types=self.get_column_types(),
            **self.reader_kwargs
        )

    def output_json(self):
        self.read_csv_to_table().to_json(
            self.output_file,
            key=self.args.key,
            newline=self.args.streamOutput,
            indent=self.args.indent,
        )

    def output_ndjson_stream(self):
        rows = agate.csv.reader(self.input_file, **self.reader_kwargs)
        column_names = next(rows)

        for row in rows:
            data = OrderedDict()
            for i, column in enumerate(column_names):
                try:
                    data[column] = row[i]
                except IndexError:
                    data[column] = None
            self.dump_json(data, newline=True)

    def output_geojson(self):
        table = self.read_csv_to_table()

        features = []

        self.min_lon = None
        self.min_lat = None
        self.max_lon = None
        self.max_lat = None

        def update_boundary_lat(lat):
            if self.min_lat is None or lat < self.min_lat:
                self.min_lat = lat
            if self.max_lat is None or lat > self.max_lat:
                self.max_lat = lat

        def update_boundary_lon(lon):
            if self.min_lon is None or lon < self.min_lon:
                self.min_lon = lon
            if self.max_lon is None or lon > self.max_lon:
                self.max_lon = lon

        def update_boundary_coordinates(coordinates):
            if len(coordinates) <= 3 and isinstance(coordinates[0], (float, int)):
                update_boundary_lon(coordinates[0])
                update_boundary_lat(coordinates[1])
            else:
                for coordinate in coordinates:
                    update_boundary_coordinates(coordinate)

        lat_column = match_column_identifier(table.column_names, self.args.lat, self.args.zero_based)
        lon_column = match_column_identifier(table.column_names, self.args.lon, self.args.zero_based)
        if self.args.type:
            type_column = match_column_identifier(table.column_names, self.args.type, self.args.zero_based)
        else:
            type_column = None
        if self.args.geometry:
            geometry_column = match_column_identifier(table.column_names, self.args.geometry, self.args.zero_based)
        else:
            geometry_column = None

        if self.args.key:
            id_column = match_column_identifier(table.column_names, self.args.key, self.args.zero_based)
        else:
            id_column = None

        for row in table.rows:
            feature = OrderedDict()
            feature['type'] = 'Feature'
            properties = OrderedDict()
            feature_id = None
            lat = None
            lon = None
            geometry = None

            for i, c in enumerate(row):
                if c is None:
                    continue
                if i == lat_column:
                    try:
                        lat = float(c)
                    except ValueError:
                        lat = None
                    if not self.args.no_bbox:
                        update_boundary_lat(lat)
                elif i == lon_column:
                    try:
                        lon = float(c)
                    except ValueError:
                        lon = None
                    if not self.args.no_bbox:
                        update_boundary_lon(lon)
                elif i == id_column:
                    feature_id = c
                elif i == type_column:
                    pass  # Prevent "type" from being added to "properties".
                elif i == geometry_column:
                    geometry = json.loads(c)
                    if not self.args.no_bbox and 'coordinates' in geometry:
                        update_boundary_coordinates(geometry['coordinates'])
                elif c:
                    properties[table.column_names[i]] = c

            if id_column is not None:
                feature['id'] = feature_id

            feature['properties'] = properties
            if geometry or lat is None and lon is None:
                feature['geometry'] = geometry
            elif lon and lat:
                feature['geometry'] = OrderedDict([
                    ('type', 'Point'),
                    ('coordinates', [lon, lat])
                ])
            features.append(feature)

        items = [
            ('type', 'FeatureCollection'),
            ('features', features),
        ]

        if not self.args.no_bbox:
            items.insert(1, ('bbox', [self.min_lon, self.min_lat, self.max_lon, self.max_lat]))

        output = OrderedDict(items)

        if self.args.crs:
            output['crs'] = OrderedDict([
                ('type', 'name'),
                ('properties', {
                    'name': self.args.crs
                })
            ])

        self.dump_json(output)


def launch_new_instance():
    utility = CSVJSON()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()
