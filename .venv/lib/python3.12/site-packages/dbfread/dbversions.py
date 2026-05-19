"""
Based on the list found here:

http://www.dbf2002.com/dbf-file-format.html
"""
DBVERSION_STRINGS = {
    0x02 : 'FoxBASE',
    0x03 : 'FoxBASE+/Dbase III plus, no memory',
    0x30 : 'Visual FoxPro',
    0x31 : 'Visual FoxPro, autoincrement enabled',
    0x32 : 'Visual FoxPro with field type Varchar or Varbinary',
    0x43 : 'dBASE IV SQL table files, no memo',
    0x63 : 'dBASE IV SQL system files, no memo',
    0x83 : 'FoxBASE+/dBASE III PLUS, with memo',
    0x8B : 'dBASE IV with memo',
    0xCB : 'dBASE IV SQL table files, with memo',
    0xF5 : 'FoxPro 2.x (or earlier) with memo',
    0xE5 : 'HiPer-Six format with SMT memo file',
    0xFB : 'FoxBASE',
}

def get_dbversion_string(dbversion):
    try:
        return DBVERSION_STRINGS[dbversion]
    except KeyError:
        return 'Unknown (0x{:02x})'.format(dbversion)
