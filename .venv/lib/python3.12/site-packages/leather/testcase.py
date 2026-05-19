import unittest


class LeatherTestCase(unittest.TestCase):
    """
    Unittest case for quickly asserting logic about charts.
    """
    def render_chart(self, chart):
        """
        Verify the column names in the given table match what is expected.
        """
        svg = chart.to_svg()

        return self.parse_svg(svg)

    def parse_svg(self, text):
        from lxml import etree

        text = text.replace(' xmlns="http://www.w3.org/2000/svg"', '').encode('utf-8')

        return etree.fromstring(text)

    def assertElementCount(self, svg, selector, count):
        series = svg.cssselect(selector)
        self.assertEqual(len(series), count)

    def assertTickLabels(self, svg, orient, compare):
        ticks = [t.text for t in svg.cssselect('.%s .tick text' % orient)]
        self.assertSequenceEqual(ticks, compare)
