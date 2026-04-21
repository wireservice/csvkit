The file 'ilgeo2010_excerpt.pl' in this directory is the first 1000 lines of the "Geographic Header File" 
distributed with the Census 2010 Redistricting Data Files for Illinois. 

<http://www2.census.gov/census_2010/01-Redistricting_File--PL_94-171/Illinois/il2010.pl.zip>

The file 'census2010_geo_schema.csv' is suitable for use with the 'in2csv' tool to convert the 
sample file into CSV.  

Thus, to convert the fixed-width geographic header file to CSV, use:

% in2csv -e iso-8859-1 -f fixed -s census2010_geo_schema.csv ilgeo2010_excerpt.pl > ilgeo2010_excerpt.csv

As is standard with csvkit tools, the output csv is UTF-8 encoded.  To see that it worked, try:

% csvcut -c 66 ilgeo2010_excerpt.csv

This will print the NAME column to STDOUT.

The documentation for that dataset notes, "The geographic header record layout is identical across all 
electronic data products from Census 2010."  Therefore, the same schema can also be used to convert 
the geographic header files for the more in-depth files accompanying the SF1 and other data sets.
