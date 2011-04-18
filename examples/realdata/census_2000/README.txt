The file 'usgeo.upl' in this directory is the "Geographic Header File" distributed with the 
"Race and Hispanic or Latino Summary File" dataset from the 2000 Census of Population and 
Housing (US). 

<http://www2.census.gov/census_2000/datasets/Race_Hispanic_Latino_Summary_File/USGEO.UPL.ZIP>

The file 'census2000_geo_schema.csv' is suitable for use with the 'in2csv' tool to convert the 
sample file into CSV.  Note that 'usgeo.upl' is in ISO-8859-1 (latin-1) encoding.

Thus, to convert the fixed-width geographic header file to CSV, use:

% in2csv -e iso-8859-1 -f fixed -s census2000_geo_schema.csv usgeo.pl > usgeo.csv

As is standard with csvkit tools, the output csv is UTF-8 encoded.

The documentation for that dataset notes, "The geographic header record is standard across all 
electronic data products from Census 2000."  Therefore, the same schema can also be used to convert 
the geographic header files for the more in-depth files accompanying the SF1 and other data sets.
