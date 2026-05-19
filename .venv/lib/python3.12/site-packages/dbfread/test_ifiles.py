from .ifiles import *
from .ifiles import ipat

assert ipat('mixed') == '[Mm][Ii][Xx][Ee][Dd]'
assert ifnmatch('test', 'test') == True
assert ifnmatch('miXEdCaSe', 'mixedcase') == True
assert ifnmatch('CAMELCASE/CamelCase', 'CamelCase/UPPERCASE') == False

# Pattern with 
# assert ipat('[A]') == '[[Aa]]'

