#!/usr/bin/env python
# -*- coding: utf-8 -*-

import six
import re
import os
import tempfile

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from csvkit.utilities.csvgoog import CSVGoog

class TestCSVGoog(unittest.TestCase):
    def test_upload(self):
        args = ['examples/dummy.csv']
        output_file = six.StringIO()
        utility = CSVGoog(args, output_file)
        utility.CREDENTIALS_LOCATION = 'tests/credentials'

        utility.main()

        input_file = six.StringIO(output_file.getvalue())

        url = next(input_file)
        print(url)
        match = re.match(r'https://docs.google.com/spreadsheets/d/(.+?)/edit', url)
        self.assertIsNotNone(match)

        # authenticate
        gauth = GoogleAuth()
        gauth.LoadCredentialsFile(utility.CREDENTIALS_LOCATION)
        if gauth.access_token_expired:
            gauth.Refresh()
        else:
            gauth.Authorize()
        drive = GoogleDrive(gauth)

        # attempt to locate data
        matching_file = None
        file_list = drive.ListFile().GetList()
        for f in file_list:
            if f['id'] == match.group(1):
                matching_file = f
                break

        self.assertIsNotNone(matching_file)

        # @TODO: download file, compare contents to expected

        # attempt to delete file
        try:
            matching_file.auth.service.files().delete(fileId=matching_file['id']).execute()
        except errors.HttpError, error:
            print 'An error occurred: %s' % error
