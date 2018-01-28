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
        self.argparser.add_argument('-k', '--key', dest='key', type=str,
                                    help='Output JSON as an array of objects keyed by a given column, KEY, rather than as a list. All values in the column must be unique. If --lat and --lon are also specified, this column will be used as GeoJSON Feature ID.')
        self.argparser.add_argument('--lat', dest='lat', type=str,
                                    help='A column index or name containing a latitude. Output will be GeoJSON instead of JSON. Only valid if --lon is also specified.')
        self.argparser.add_argument('--lon', dest='lon', type=str,
                                    help='A column index or name containing a longitude. Output will be GeoJSON instead of JSON. Only valid if --lat is also specified.')
        self.argparser.add_argument('--crs', dest='crs', type=str,
                                    help='A coordinate reference system string to be included with GeoJSON output. Only valid if --lat and --lon are also specified.')
        self.argparser.add_argument('--stream', dest='streamOutput', action='store_true',
                                    help='Output JSON as a stream of newline-separated objects, rather than an as an array.')
        self.argparser.add_argument('-y', '--snifflimit', dest='sniff_limit', type=int,
                                    help='Limit CSV dialect sniffing to the specified number of bytes. Specify "0" to disable sniffing entirely.')
        self.argparser.add_argument('-I', '--no-inference', dest='no_inference', action='store_true',
                                    help='Disable type inference (and --locale, --date-format, --datetime-format) when parsing CSV input.')

    def main(self):
        if self.additional_input_expected():
            if self.args.streamOutput and self.args.no_inference and not self.args.skip_lines and self.args.sniff_limit == 0:
                sys.stderr.write('No input file or piped data provided. Waiting for standard input:\n')
            else:
                self.argparser.error('You must provide an input file or piped data.')

        # We need to do this dance here, because we aren't writing through agate.
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

        def default(obj):
            if isinstance(obj, (datetime.date, datetime.datetime)):
                return obj.isoformat()
            elif isinstance(obj, decimal.Decimal):
                return str(obj)
            raise TypeError('%s is not JSON serializable' % repr(obj))

        def dump_json(data, newline=False):
            json.dump(data, stream, default=default, **json_kwargs)
            if newline:
                stream.write("\n")

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

        # GeoJSON
        if self.args.lat and self.args.lon:
            table = agate.Table.from_csv(
                self.input_file,
                skip_lines=self.args.skip_lines,
                sniff_limit=self.args.sniff_limit,
                column_types=self.get_column_types(),
                **self.reader_kwargs
            )

            features = []

            global min_lon, min_lat, max_lon, max_lat

            min_lon = None
            min_lat = None
            max_lon = None
            max_lat = None

            def update_boundary_lat(lat):
                global min_lat, max_lat

                if min_lat is None or lat < min_lat:
                    min_lat = lat
                if max_lat is None or lat > max_lat:
                    max_lat = lat

            def update_boundary_lon(lon):
                global min_lon, max_lon

                if min_lon is None or lon < min_lon:
                    min_lon = lon
                if max_lon is None or lon > max_lon:
                    max_lon = lon

            def update_boundary_coords(coords):
                if (isinstance(coords, list) and len(coords) == 2 and
                        isinstance(coords[0], (float, int)) and
                        isinstance(coords[1], (float, int))):
                    update_boundary_lon(coords[0])
                    update_boundary_lat(coords[1])
                else:
                    for coord in coords:
                        update_boundary_coords(coord)

            lat_column = match_column_identifier(table.column_names, self.args.lat, self.args.zero_based)
            lon_column = match_column_identifier(table.column_names, self.args.lon, self.args.zero_based)

            if self.args.key:
                id_column = match_column_identifier(table.column_names, self.args.key, self.args.zero_based)
            else:
                id_column = None

            for row in table.rows:
                feature = OrderedDict()
                feature['type'] = 'Feature'
                properties = OrderedDict()
                geoid = None
                geo_type = 'Point'
                lat = None
                lon = None
                coords = None

                for i, c in enumerate(row):
                    if i == lat_column:
                        if c is None:
                            continue
                        try:
                            lat = float(c)
                        except ValueError:
                            lat = None
                        update_boundary_lat(lat)
                    elif i == lon_column:
                        if c is None:
                            continue
                        try:
                            lon = float(c)
                        except ValueError:
                            lon = None
                        update_boundary_lon(lon)
                    elif i == id_column:
                        geoid = c
                    elif table.column_names[i] == 'type':
                        geo_type = c
                    elif table.column_names[i] == 'geojson':
                        geojson = json.loads(c)
                        coords = geojson['coordinates']
                        update_boundary_coords(coords)
                    elif c is not None:
                        properties[table.column_names[i]] = c

                if id_column is not None:
                    feature['id'] = geoid

                if lon and lat:
                    coords = [lon, lat]

                feature['geometry'] = OrderedDict([
                    ('type', geo_type),
                    ('coordinates', coords)
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
        elif self.args.streamOutput and self.args.no_inference and not self.args.skip_lines and self.args.sniff_limit == 0:
            rows = agate.csv.reader(self.input_file, **self.reader_kwargs)
            column_names = next(rows)

            for row in rows:
                data = OrderedDict()
                for i, column in enumerate(column_names):
                    try:
                        data[column] = row[i]
                    except IndexError:
                        data[column] = None
                dump_json(data, newline=True)
        else:
            table = agate.Table.from_csv(
                self.input_file,
                skip_lines=self.args.skip_lines,
                sniff_limit=self.args.sniff_limit,
                column_types=self.get_column_types(),
                **self.reader_kwargs
            )

            table.to_json(
                self.output_file,
                key=self.args.key,
                newline=self.args.streamOutput,
                indent=self.args.indent,
            )


def launch_new_instance():
    utility = CSVJSON()
    utility.run()


if __name__ == '__main__':
    launch_new_instance()
