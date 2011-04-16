=======
csvjoin
=======

Description
===========

Merges two or more CSV tables together using a method analogous to SQL JOIN operation. By default it performs an inner join, but full outer, left outer, and right outer are all available via flags. Key columns are specified with the -c flag (either a single column which exists in all tables, or a comma-seperated list of columns with one corresponding to each). If the columns flag is not provided then the tables will be merged "sequentially", that is they will be attached side-by-side with no concern for ordering or matching.
