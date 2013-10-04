#!/usr/bin/env python

import os
import sys
import logging
import elasticsearch
import json

from csvkit import CSVKitDictReader
from csvkit.cli import CSVKitUtility

class CSVES(CSVKitUtility):
    description = 'Export a CSV file to Elasticsearch.'

    def add_arguments(self):
        self.argparser.add_argument('--index', dest='index_name', required=True,
            help='Specify a name for the Elasticsearch index to be created.')
        self.argparser.add_argument('--type', dest='doc_type', required=True,
            help='Specify an Elasticsearch document type.')
        self.argparser.add_argument('--mapping', dest='mapping',
            help='Specify Elasticsearch mappings file in JSON format.')
        self.argparser.add_argument('--host', dest='host', default="localhost",
            help='Specify Elasticsearch host.')
        self.argparser.add_argument('--port', dest='port', default="9200",
            help='Specify Elasticsearch port.')

    def main(self):
        es = elasticsearch.Elasticsearch([{'host':self.args.host, 'port':self.args.port}])

        if not es.indices.exists(self.args.index_name):
            es.indices.create(index=self.args.index_name)

        if self.args.mapping:
            with open(self.args.mapping,'r') as mapping_file:
                mapping_json = json.load(mapping_file)
                es.indices.put_mapping(index=self.args.index_name, doc_type=self.args.doc_type, body=mapping_json)

        rows = CSVKitDictReader(self.args.file, **self.reader_kwargs)
        for row in rows:
            action={ "index" : { "_index" : self.args.index_name, "_type" : self.args.doc_type } }
            es.bulk([action,row])
        

def launch_new_instance():
    logging.basicConfig()
    utility = CSVES()
    utility.main()
    
if __name__ == "__main__":
    launch_new_instance()

