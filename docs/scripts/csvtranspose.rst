============
csvtranspose
============

Description
===========

Transpose a CSV file:

    usage: csvtranspose FILE

    Transpose rows into columns and vice versa.


Examples
========

    Reshape some csv:

    csvtranspose realdata/acs2012_5yr_population.csv 

    Get all columns matching "OKLAHOMA":

    csvtranspose examples/realdata/FY09_EDU_Recipients_by_State.csv \
       | grep OKLAHOMA | csvtranspose
