import unittest
from cStringIO import StringIO
import csv

from csvkit.convert import fixed


class TestFixed(unittest.TestCase):
    def test_fixed(self):
        with open('examples/testfixed', 'r') as f:
            with open('examples/testfixed_schema.csv', 'r') as schema:
                output = fixed.fixed2csv(f, schema)
        
        with open('examples/testfixed_converted.csv', 'r') as f:
            self.assertEqual(f.read(), output)

    def test_row_decoder_init(self):
        rd = fixed.SchemaRowDecoder(start=1,length=2,column=3)
        self.assertEqual(1,rd.start)
        self.assertEqual(2,rd.length)
        self.assertEqual(3,rd.column)
        
        rd = fixed.SchemaRowDecoder(row=['column','start','length'])
        self.assertEqual(1,rd.start)
        self.assertEqual(2,rd.length)
        self.assertEqual(0,rd.column)
        
        
    def test_row_decoder_in_action(self):
        rd = fixed.SchemaRowDecoder(start=1,length=2,column=3)

        (column, start, length) = rd(['This is a comment','0','1','column_name'])
        self.assertEqual(False,rd.one_based)
        self.assertEqual('column_name',column)
        self.assertEqual(0, start)
        self.assertEqual(1, length)
        
        (column, start, length) = rd(['This is another comment','1','5','column_name2'])
        self.assertEqual(False,rd.one_based)
        self.assertEqual('column_name2',column)
        self.assertEqual(1, start)
        self.assertEqual(5, length)
        
        (column, start, length) = rd(['yet another comment','9','14','column_name3'])
        self.assertEqual(False,rd.one_based)
        self.assertEqual('column_name3',column)
        self.assertEqual(9, start)
        self.assertEqual(14, length)
        

    def test_one_based_row_decoder(self):
        rd = fixed.SchemaRowDecoder(row=['column','start','length'])

        (column, start, length) = rd(['LABEL', '1', '5' ])
        self.assertEqual(True,rd.one_based)
        self.assertEqual('LABEL',column)
        self.assertEqual(0, start)
        self.assertEqual(5, length)

        (column, start, length) = rd(['LABEL2', '6', '15' ])
        self.assertEqual('LABEL2',column)
        self.assertEqual(5, start)
        self.assertEqual(15, length)

    def test_schematic_line_parser(self):
        schema = """column,start,length
foo,1,5
bar,6,2
baz,8,5"""
        f = StringIO(schema)
        parser = fixed.SchematicLineParser(f)
        self.assertEqual('foo',parser.headers[0])
        self.assertEqual('bar',parser.headers[1])
        self.assertEqual('baz',parser.headers[2])
        
        parsed = parser.parse("111112233333")
        self.assertEqual('11111',parsed[0])
        self.assertEqual('22',parsed[1])
        self.assertEqual('33333',parsed[2])
        
        parsed = parser.parse("    1 2    3")
        self.assertEqual('1',parsed[0])
        self.assertEqual('2',parsed[1])
        self.assertEqual('3',parsed[2])

        parsed = parser.parse("1  1  233  3")
        self.assertEqual('1  1',parsed[0])
        self.assertEqual('2',parsed[1])
        self.assertEqual('33  3',parsed[2])
        
    def test_stream_convert(self):
        schema = StringIO("""column,start,length
foo,1,5
bar,6,2
baz,8,5""")

        data = StringIO("""111112233333
    1 2    3
1  1  233  3""")

        result = StringIO()

        fixed.stream_convert(data, result, schema)

        expected = """foo,bar,baz
11111,22,33333
1,2,3
1  1,2,33  3"""
        result.reset()
        result_reader = csv.reader(result)
        self.assertEqual(['foo','bar','baz'], result_reader.next())
        self.assertEqual(['11111','22','33333'], result_reader.next())
        self.assertEqual(['1','2','3'], result_reader.next())
        self.assertEqual(['1  1','2','33  3'], result_reader.next())

        