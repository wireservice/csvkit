#!/usr/bin/env python

import itertools
import os
import sys
import stat
import webbrowser
import datetime
import dateutil.parser
import tempfile

import pprint

import six

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from csvkit import CSVKitReader, CSVKitWriter
from csvkit.cli import CSVKitUtility
from csvkit.headers import make_default_headers


class CSVGoog(CSVKitUtility):
    description = 'Upload a CSV file to Google Sheets.'

    CREDENTIALS_LOCATION = '%s/.csvkit/credentials' % os.path.expanduser('~')

    def add_arguments(self):
        self.argparser.add_argument('-c', '--configure', dest='configure', action='store_true',
            help='Configure credentials for csvgoog command.')
        self.argparser.add_argument('-o', '--open', dest='browser', action='store_true',
            help='Attempt to open spreadsheet in browser.')
        self.argparser.add_argument('-n', '--name', dest='name', action='store',
            help='Specify name for spreadsheet. If it already exists, produces an error unless -o/--overwrite is specified.')
        self.argparser.add_argument('-w', '--overwrite', dest='overwrite', action='store_true',
            help='Force overwrite of existing spreadsheet. Requires -n/--name.')

    def main(self, credentials_location=None):

        gauth = GoogleAuth()

        if self.args.configure:
            if not os.path.exists(os.path.dirname(self.CREDENTIALS_LOCATION)):
                os.mkdir(os.path.dirname(self.CREDENTIALS_LOCATION))
            if os.path.exists(self.CREDENTIALS_LOCATION):
                os.unlink(self.CREDENTIALS_LOCATION)

            gauth.LocalWebserverAuth()
            gauth.SaveCredentialsFile(self.CREDENTIALS_LOCATION)
            os.chmod(self.CREDENTIALS_LOCATION, stat.S_IWUSR | stat.S_IRUSR)
            sys.stderr.write('Success. Credentials saved to %s\n' % self.CREDENTIALS_LOCATION)
            return

        # try to load saved client credentials
        gauth.LoadCredentialsFile(self.CREDENTIALS_LOCATION)
        if gauth.credentials is None:
            self.argparser.error('Google Drive credentials not found. Have you run `csvgoog --configure`?\n')
        elif gauth.access_token_expired:
            gauth.Refresh()
        else:
            gauth.Authorize()

        gauth.SaveCredentialsFile(self.CREDENTIALS_LOCATION)

        drive = GoogleDrive(gauth)

        if self.args.overwrite and not self.args.name:
            self.argparser.error('Cannot overwrite spreadsheet without a specified title. Use -t/--title.')

        title = 'csvkit upload %s' % datetime.datetime.now().isoformat()
        if self.args.name:
            title = self.args.name

        # write contents to temp file
        rows = CSVKitReader(self.input_file, **self.reader_kwargs)
        (fd, temp_path) = tempfile.mkstemp()
        temp_handle = os.fdopen(fd, 'w')
        writer = CSVKitWriter(temp_handle, **self.writer_kwargs)
        for row in rows:
            writer.writerow(row)
        temp_handle.close()

        # upload file
        upload_file = None
        if self.args.overwrite:
            file_list = list(drive.ListFile({'q': "title='%s'" % self.args.name}).GetList())
            file_list.sort(key=lambda x: dateutil.parser.parse(x['createdDate']))
            upload_file = file_list[0]
        else:
            upload_file = drive.CreateFile({'title': title, 'mimeType': 'text/csv'})
        upload_file.SetContentFile(temp_path)
        upload_file.Upload(param={'convert': True})

        # delete temporary file
        os.unlink(temp_path)

        # emit URL
        url = 'https://docs.google.com/spreadsheets/d/%s/edit' % upload_file['id']
        if self.args.browser:
            webbrowser.open(url)
        else:
            self.output_file.write("%s\n" % url)


def launch_new_instance():
    utility = CSVGoog()
    utility.main()

if __name__ == "__main__":
    launch_new_instance()

