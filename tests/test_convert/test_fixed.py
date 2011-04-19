import unittest

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
        