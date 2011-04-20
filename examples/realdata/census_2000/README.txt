GEOGRAPHIC HEADER FILE
----------------------

The file 'usgeo_excerpt.upl' in this directory is the first 1000 rows of the  "Geographic Header File" 
distributed with the "Race and Hispanic or Latino Summary File" dataset from the 2000 US Census. 

<http://www2.census.gov/census_2000/datasets/Race_Hispanic_Latino_Summary_File/USGEO.UPL.ZIP>

The file 'census2000_geo_schema.csv' is suitable for use with the 'in2csv' tool to convert the 
sample file into CSV.  Note that 'usgeo_excerpt.upl' is in ISO-8859-1 (latin-1) encoding.

Thus, to convert the fixed-width geographic header file to CSV, use:

% in2csv -e iso-8859-1 -f fixed -s census2000_geo_schema.csv usgeo_excerpt.upl > usgeo.csv

As is standard with csvkit tools, the output csv is UTF-8 encoded.  To see that it worked, try:

% csvcut -c 64 usgeo.csv

This will print the NAME column to STDOUT.

The documentation for that dataset notes, "The geographic header record is standard across all 
electronic data products from Census 2000."  Therefore, the same schema can also be used to convert 
the geographic header files for the more in-depth files accompanying the SF1 and other data sets.
<<<<<<< HEAD
=======

VOTING RIGHTS DETERMINATION
---------------------------
By law, the Director of the Census is to determine which political subdivisions are subject to the minority 
language assistance provisions of Section 203 of the Voting Rights Act.

<http://www.census.gov/mp/www/cat/decennial_census_2000/voting_rights_determination_file_on_cd-rom.html>

The file VROUTFSJ.TXt is the result of the report, limited to the subdivisions so identified. 
<http://www2.census.gov/census_2000/datasets/determination/VROUTFSJ.TXt>
(This data is actually also made available as CSV, but there is also a complete fixed-width file which might be 
interesting for analysis outside the specific question of minority language voting assistance which is in the 
same format as the test file here, but which is much too large to use for an example.)

To convert the fixed-width voting rights determination file to CSV, use:

% in2csv -f fixed -s determination_schema.csv VROUTFSJ.TXt > determination.csv

To see that it worked, try:

% csvcut -c 18 determination.csv

For complete documentation of the meaning of the fields described in determination_schema.csv consult:
<http://www2.census.gov/census_2000/datasets/determination/vr_doc_rev7.wpd>
