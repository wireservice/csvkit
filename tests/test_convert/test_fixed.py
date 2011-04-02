import unittest

from csvkit.convert import fixed

class TestFixed(unittest.TestCase):
    def test_fixed(self):
        with open('examples/testfixed', 'r') as f:
            with open('examples/testfixed_schema.csv', 'r') as schema:
                output = fixed.fixed2csv(f, schema)
        
        with open('examples/testfixed_converted.csv', 'r') as f:
            self.assertEquals(f.read(), output)
