import zipfile
import time
import lxml.etree as etree
import xml.etree.ElementTree as ET
import agate
import io


ODS_CONTENT_FILE = 'content.xml'
def get_namespaces_lxml(xml_file):
    """
    Extracts all the namespaces present in XML file
    """
    xml_file.seek(0)
    tree = etree.parse(xml_file)
    return tree.getroot().nsmap
            

def ods2csv(filepath,sheetname=None,**kwargs):
    """
    Convert ODS document to CSV format
    """
    kwargs_keys = list(kwargs.keys())
    if not zipfile.is_zipfile(filepath):
        return 'not an ods file'

    with zipfile.ZipFile(file=filepath) as ods_file:
        INPUT_FILENAME = ods_file.filename.split('.')[0]
        with ods_file.open(ODS_CONTENT_FILE,'r') as content_file:
            tree = ET.parse(content_file)
            root = tree.getroot()
            ns = get_namespaces_lxml(content_file) #xml file namespaces 

            table_tag = '{%s}table' % ns['table']
            table_row_tag = '{%s}table-row' % ns['table']
            cell_tag = '{%s}table-cell' % ns['table']
            p_tag = '{%s}p' % ns['text']

            sheetnames = list()    
            for table in root.iter(table_tag):
                sheetnames.append(table.attrib['{%s}name' % ns['table']])
            
            if (
                'display_sheetnames' in kwargs_keys 
                and kwargs['display_sheetnames'] is not False
            ):
                return sheetnames   #display sheetnames
            
            csv_string = ''
            def create(table,sheetname=None):
                rows = list()
                for table_row in table.iter(table_row_tag):
                    row = list()
                    for data_cell in table_row.iter(cell_tag):
                        text = data_cell.findtext(p_tag) if data_cell.findtext(p_tag) is not None else ''
                        row.append(text)
                    
                    if row[-1] == '':
                        row.pop(-1)     #remove row padding
                    if len(row) == 0:
                        continue        #remove empty row
                    rows.append(row)
                columns = rows[0]   #creating a column row for agate
                rows.pop(0)         #removing extra column row from data
                table = agate.Table(rows=rows,column_names=columns)
                output = io.StringIO()

                if 'write_sheets' in kwargs_keys and kwargs['write_sheets'] is not None:
                    if kwargs['write_sheets'] in sheetnames or kwargs['write_sheets'] == '-':
                        output_filename = (
                            '%s.csv' % INPUT_FILENAME if (sheetname is None and kwargs['write_sheets'] != '-') 
                            else '%s_%s.csv' % (INPUT_FILENAME,sheetname)
                            )
                        table.to_csv(
                            output_filename
                        )
                        print('%s successfully created.' % output_filename)
                else:
                    print('-----%s-----' % sheetname)
                    table.print_csv()
                    csv_string = output.getvalue()

            
            for table in root.iter(table_tag):
                if 'write_sheets' in kwargs_keys and kwargs['write_sheets'] is not None:
                    sheetname = kwargs['write_sheets']
                if (
                    sheetname is not None 
                    and sheetname in sheetnames
                    and table.attrib['{%s}name' % ns['table']] == sheetname
                ):
                    # print(table.attrib['{%s}name' % ns['table']])
                    create(table,sheetname=sheetname)    #output single ods sheet csv
                elif sheetname is None or sheetname == '-':
                    create(table,table.attrib['{%s}name' % ns['table']] if len(sheetnames) > 1 else None)    #output csv for all the sheets present in ods file
            
            return csv_string
        content_file.close()
    ods_file.close()        
