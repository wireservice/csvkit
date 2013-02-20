CSV FUZZY JOIN, an extension of csvkit that helps reconcile two datasets using the levenstein algorithm to assign 
similarity scores to items in particular fields, and selecting the best match to join on.

Given two CSVs and the names of the fields to do a "soft" or "fuzzy" join on, it will return each row of the first table, along with the single 
best match from the second table, and an additional "match_score" indicating, on a scale of 0 to 100, how confident the algorithm is in the match.

This is designed for the common problem of reconciling different spellings between two datasets to settle on unique IDs. Open Refine employs similar 
reconiciliation, but is designed for standardizing rows with a singe dataset and cannot reconcile two separate groups between each other.

You can also perform normal left joins (non-fuzzy) on as many columns as you want to limit the pool of possibilities among which the algorithm will choose 
the best match based on the fuzzy field.

To test, take a list of black members of Congress (the main table) and a list of all members of Congress (the lookup table)
with differently-standardized spellings. We know that there will be one best match for each black member in the larger list,
and we want to reconcile them so we can use consistent IDs.

python csvfuzzyjoin.py ../../examples/fuzzy_main.csv ../../examples/fuzzy_lookup.csv -f name=office

But wait! We also have party and state for each lawmaker--those aren't fuzzy--so we will get much better results if, when looking for
a match for Charlie Rangel, we limit our pool of differently-standardized names to only those we know are also New York Democrats.

python csvfuzzyjoin.py ../../examples/fuzzy_main.csv ../../examples/fuzzy_lookup.csv -f name=office -n state,party

The tool requires fuzzywuzzy, a levenstein implementation by seatgeek (added to requirements.txt):

https://github.com/seatgeek/fuzzywuzzy/tree/master/fuzzywuzzy

but that dependency could be eliminated by moving pieces of the code inside the project. It could also easily be expanded to use other 
matching algorithms like the ones employed by Open Refine.


By Luke Rosiak. MIT license.

