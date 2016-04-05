#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import agate
import six

from sed import CSVModifier, cranges, modifier_as_function

def run(source, modifiers, header=True):
    src = six.StringIO(source)
    dst = six.StringIO()
    reader = agate.csv.reader(src)
    reader = CSVModifier(reader, modifiers, header=header)
    writer = agate.csv.writer(dst)
    for row in reader:
        writer.writerow(row)
    return dst.getvalue()

class TestSed(unittest.TestCase):

    baseCSV = """\
header 1,header 2,header 3,header 4,header 5
field 1.1,field 1.2,field 1.3,field 1.4,field 1.5
field 2.1,field 2.2,field 2.3,field 2.4,field 2.5
field 3.1,field 3.2,field 3.3,field 3.4,field 3.5
"""

    baseCSVUnicode = """\
latin_lower,latin_upper,latin_full,greek_lower,greek_upper,greek_full
a,A,alpha,α,Α,άλφα
b,B,beta,β,Β,βήτα
g,G,gamma,γ,Γ,γάμμα
"""

    def test_charRanges(self):
        self.assertEqual(cranges(u'a-f'), u'abcdef')
        self.assertEqual(cranges(u'a\-f'), u'a-f')
        self.assertEqual(cranges(u'abc-'), u'abc-')
        self.assertEqual(cranges(u'-abc'), u'-abc')
        self.assertEqual(cranges(u'a\\\\-_z'), u'a\]^_z')
        self.assertEqual(cranges(u'a-c-e-g'), u'abcdefg')

    def test_modifier_y_directcall(self):
        self.assertEqual(modifier_as_function(u'y/abc/def/')(u'b,a,c'), u'e,d,f')
        self.assertEqual(modifier_as_function(u'y/abc/def/')(u'b,A,C'), u'e,A,C')
        self.assertEqual(modifier_as_function(u'y/abc/def/i')(u'b,A,C'), u'e,d,f')
        self.assertEqual(modifier_as_function(u'y/a-z/A-Z/')(u'Back-Up'), u'BACK-UP')
        self.assertEqual(modifier_as_function(u'y/a\-z/A~Z/')(u'Back-Up'), u'BAck~Up')

    def test_modifier_y_directcall_unicode(self):
        self.assertEqual(modifier_as_function(u'y/abc/def/')(u'b,a,c'), u'e,d,f')
        self.assertEqual(modifier_as_function(u'y/abc/def/')(u'b,a,c'), u'e,d,f')
        self.assertEqual(modifier_as_function(u'y/αβγ/abg/')(u'β,α,γ'), u'b,a,g')
        self.assertEqual(modifier_as_function(u'y/abg/αβγ/')(u'b,a,g'), u'β,α,γ')
        self.assertEqual(modifier_as_function(u'y/αβγ/γαβ/')(u'β,α,γ'), u'α,γ,β')

    def test_modifier_y_toupper(self):
        chk = """\
header 1,header 2,header 3,header 4,header 5
field 1.1,field 1.2,FIELD 1.3,field 1.4,field 1.5
field 2.1,field 2.2,FIELD 2.3,field 2.4,field 2.5
field 3.1,field 3.2,FIELD 3.3,field 3.4,field 3.5
"""
        self.assertEqual(run(self.baseCSV, {2: u'y/a-z/A-Z/'}), chk)

    def test_modifier_s_directcall(self):
        self.assertEqual(modifier_as_function(u's/a/b/')(u'abcabc'), u'bbcabc')
        self.assertEqual(modifier_as_function(u's/a/b/g')(u'abcabc'), u'bbcbbc')
        self.assertEqual(modifier_as_function(u's/a/b/g')(u'abcABC'), u'bbcABC')
        self.assertEqual(modifier_as_function(u's/a/b/gi')(u'abcABC'), u'bbcbBC')

    def test_modifier_s_directcall_unicode(self):
        self.assertEqual(modifier_as_function(u's/π/p/')(u'κάππα'), u'κάpπα')
        self.assertEqual(modifier_as_function(u's/π/p/g')(u'κάππα'), u'κάppα')
        self.assertEqual(modifier_as_function(u's/π/Π/')(u'κάππα'), u'κάΠπα')
        self.assertEqual(modifier_as_function(u's/π/Π/g')(u'κάππα'), u'κάΠΠα')

    def test_modifier_s_noflags(self):
        chk = """\
header 1,header 2,header 3,header 4,header 5
xield 1.1,field 1.2,field 1.3,field 1.4,field 1.5
xield 2.1,field 2.2,field 2.3,field 2.4,field 2.5
xield 3.1,field 3.2,field 3.3,field 3.4,field 3.5
"""
        self.assertMultiLineEqual(run(self.baseCSV, {0: u's/./x/'}), chk)

    def test_modifier_s_noflags_unicode(self):
        chk = """\
latin_lower,latin_upper,latin_full,greek_lower,greek_upper,greek_full
a,A,alpha,α,Α,*λφα
b,B,beta,β,Β,*ήτα
g,G,gamma,γ,Γ,*άμμα
"""
        self.assertMultiLineEqual(run(self.baseCSVUnicode, {5: u's/./*/'}), chk)

    def test_modifier_s_gflag(self):
        chk = """\
header 1,header 2,header 3,header 4,header 5
xxxxxxxxx,field 1.2,field 1.3,field 1.4,field 1.5
xxxxxxxxx,field 2.2,field 2.3,field 2.4,field 2.5
xxxxxxxxx,field 3.2,field 3.3,field 3.4,field 3.5
"""
        self.assertMultiLineEqual(run(self.baseCSV, {0: u's/./x/g'}), chk)

    def test_modifier_s_gflag_unicode(self):
        chk = """\
latin_lower,latin_upper,latin_full,greek_lower,greek_upper,greek_full
a,A,alpha,α,Α,****
b,B,beta,β,Β,****
g,G,gamma,γ,Γ,*****
"""
        self.assertMultiLineEqual(run(self.baseCSVUnicode, {5: u's/./*/g'}), chk)

    def test_modifier_s_multicol(self):
        chk = """\
header 1,header 2,header 3,header 4,header 5
xxxxxxxxx,field 1.2,yyyyyyyyy,field 1.4,field 1.5
xxxxxxxxx,field 2.2,yyyyyyyyy,field 2.4,field 2.5
xxxxxxxxx,field 3.2,yyyyyyyyy,field 3.4,field 3.5
"""
        self.assertMultiLineEqual(run(self.baseCSV, {0: u's/./x/g', 2: u's/./y/g'}), chk)

    def test_modifier_s_multicol_unicode(self):
        chk = """\
latin_lower,latin_upper,latin_full,greek_lower,greek_upper,greek_full
a,A,alpha,_,Α,****
b,B,beta,_,Β,****
g,G,gamma,_,Γ,*****
"""
        self.assertMultiLineEqual(run(self.baseCSVUnicode, {3: u's/./_/g', 5: u's/./*/g'}), chk)

    def test_modifier_s_colbyname(self):
        chk = """\
header 1,header 2,header 3,header 4,header 5
xxxxxxxxx,field 1.2,yyyyyyyyy,field 1.4,field 1.5
xxxxxxxxx,field 2.2,yyyyyyyyy,field 2.4,field 2.5
xxxxxxxxx,field 3.2,yyyyyyyyy,field 3.4,field 3.5
"""
        self.assertMultiLineEqual(
            run(self.baseCSV, {'header 1': u's/./x/g', 'header 3': u's/./y/g'}), chk)

    def test_modifier_s_colbyname_unicode(self):
        chk = """\
latin_lower,latin_upper,latin_full,greek_lower,greek_upper,greek_full
a,A,alpha,_,Α,****
b,B,beta,_,Β,****
g,G,gamma,_,Γ,*****
"""
        self.assertMultiLineEqual(run(self.baseCSVUnicode, {'greek_lower': u's/./_/g', 'greek_full': u's/./*/g'}), chk)

    def test_modifier_s_nomatch(self):
        chk = self.baseCSV
        self.assertMultiLineEqual(run(self.baseCSV, {0: u's/[IE]/../'}), chk)

    def test_modifier_s_nomatch_unicode(self):
        chk = self.baseCSVUnicode
        self.assertMultiLineEqual(run(self.baseCSVUnicode, {5: u's/[a-zA-Z0-9€]/../'}), chk)

    def test_modifier_s_iflag(self):
        chk = """\
header 1,header 2,header 3,header 4,header 5
f..eld 1.1,field 1.2,field 1.3,field 1.4,field 1.5
f..eld 2.1,field 2.2,field 2.3,field 2.4,field 2.5
f..eld 3.1,field 3.2,field 3.3,field 3.4,field 3.5
"""
        self.assertMultiLineEqual(run(self.baseCSV, {0: u's/[IE]/../i'}), chk)

    def test_modifier_s_multiflag(self):
        chk = """\
header 1,header 2,header 3,header 4,header 5
f....ld 1.1,field 1.2,field 1.3,field 1.4,field 1.5
f....ld 2.1,field 2.2,field 2.3,field 2.4,field 2.5
f....ld 3.1,field 3.2,field 3.3,field 3.4,field 3.5
"""
        self.assertMultiLineEqual(run(self.baseCSV, {0: u's/[IE]/../ig'}), chk)

    def test_modifier_s_remove(self):
        src = 'cell 1,"123,456,789.0"\n'
        chk = 'cell 1,123456789.0\n'
        self.assertMultiLineEqual(run(src, {1: u's/,//g'}, header=False), chk)

    def test_modifier_s_remove_unicode(self):
        src = 'cell 1,"άλφα,βήτα,γάμμα"\n'
        chk = 'cell 1,άααάα\n'
        self.assertMultiLineEqual(run(src, {1: u's/(,|[^άα])//g'}, header=False), chk)

    def test_modifier_e_directcall(self):
        self.assertEqual(modifier_as_function(u'e/./tr ab xy/')(u'b,a,c'), u'y,x,c')
        self.assertEqual(modifier_as_function(u'e/./xargs -I {} echo "{}^2" | bc/')(u'4'), u'16')

    def test_modifier_e_directcall_filter(self):
        self.assertEqual(modifier_as_function(u'e/^[0-9]+$/xargs -I {} echo "{}^2" | bc/')(u'4'), u'16')
        self.assertEqual(modifier_as_function(u'e/^[0-9]+$/xargs -I {} echo "{}^2" | bc/')(u'4a'), u'4a')

    def test_modifier_e_directcall_unicode(self):
        self.assertEqual(modifier_as_function(u'e/./sed "y~฿₯﷼￡￥~￥￡﷼₯฿~"/')(u'￥￡﷼₯฿'), u'฿₯﷼￡￥')

    def test_modifier_e_directcall_backref(self):
        self.assertEqual(modifier_as_function(u'e/^([0-9]+)(€?)$/echo "\\2"; echo "\\1^2" | bc/')(u'4'), u'16')
        self.assertEqual(modifier_as_function(u'e/^([0-9]+)(€?)$/echo "\\2"; echo "\\1^2" | bc/')(u'4€'), u'€16')
        self.assertEqual(modifier_as_function(u'e/^([0-9]+)(€?)$/echo "\\2"; echo "\\1^2" | bc/')(u'€4'), u'€4')

    def test_modifier_e_multipipe(self):
        chk = """\
header 1,header 2,header 3,header 4,header 5
field 1.1,field 1.2,field 1.3,1.96,field 1.5
field 2.1,field 2.2,field 2.3,5.76,field 2.5
field 3.1,field 3.2,field 3.3,11.56,field 3.5
"""
        self.assertMultiLineEqual(
            run(self.baseCSV, {3: u'e/./cut -f2 -d" " | xargs -I {} echo "scale=3;{}^2" | bc/'}), chk)

    def test_modifier_e_unicode(self):
        chk = """\
latin_lower,latin_upper,latin_full,greek_lower,greek_upper,greek_full
a,A,alpha,α,Α,άλφαάλφαάλφα
b,B,beta,β,Β,βήταβήταβήτα
g,G,gamma,γ,Γ,γάμμαγάμμαγάμμα
"""
        self.assertMultiLineEqual(
            run(self.baseCSVUnicode, {5: u'e/./xargs -I {} echo "{}{}{}"/'}), chk)

    def test_modifier_e_comma_in_output(self):
        chk = """\
latin_lower,latin_upper,latin_full,greek_lower,greek_upper,greek_full
a,A,alpha,α,Α,"άλφα,άλφα,άλφα"
b,B,beta,β,Β,"βήτα,βήτα,βήτα"
g,G,gamma,γ,Γ,"γάμμα,γάμμα,γάμμα"
"""
        self.assertMultiLineEqual(
            run(self.baseCSVUnicode, {5: u'e/./xargs -I {} echo "{},{},{}"/'}), chk)

    def test_modifier_e_quotes_in_output(self):
        chk = """\
latin_lower,latin_upper,latin_full,greek_lower,greek_upper,greek_full
a,A,alpha,α,Α,"άλφα,""άλφα"",άλφα"
b,B,beta,β,Β,"βήτα,""βήτα"",βήτα"
g,G,gamma,γ,Γ,"γάμμα,""γάμμα"",γάμμα"
"""
        self.assertMultiLineEqual(
            run(self.baseCSVUnicode, {5: u'e/./xargs -I {} echo "{},\\"{}\\",{}"/'}), chk)

    def test_modifier_e_backreference(self):
        chk = """\
latin_lower,latin_upper,latin_full,greek_lower,greek_upper,greek_full
a,A,"{first : a, last : a}",α,Α,"{first : ά, last : α}"
b,B,"{first : b, last : a}",β,Β,"{first : β, last : α}"
g,G,"{first : g, last : a}",γ,Γ,"{first : γ, last : α}"
"""
        self.assertMultiLineEqual(
            run(self.baseCSVUnicode, {i: u'e/^(.).*(.)$/echo "{first : \\1, last : \\2}"/' for i in range(6)}), chk)