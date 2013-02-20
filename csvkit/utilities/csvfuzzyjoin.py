#!/usr/bin/env python

from fuzzywuzzy import process

from csvkit import table, CSVKitWriter
from csvkit.cli import CSVKitUtility, CSVFileType, match_column_identifier


"""To test, take a list of black members of Congress (the main table) and a list of all members of Congress (the lookup table)
with differently-standardized spellings. We know that there will be one best match for each black member in the larger list,
and we want to reconcile them so we can use consistent IDs.

python csvfuzzyjoin.py ../../examples/fuzzy_main.csv ../../examples/fuzzy_lookup.csv -f name=office

But wait! We also have party and state for each lawmaker--those aren't fuzzy--so we will get much better results if, when looking for
a match for Charlie Rangel, we limit our pool of differently-standardized names to only those we know are also New York Democrats.

python csvfuzzyjoin.py ../../examples/fuzzy_main.csv ../../examples/fuzzy_lookup.csv -f name=office -n state,party
"""

class CSVFuzzyJoin(CSVKitUtility):
    description = """Fuzzy join: For each row of table 1, find the best match in table 2, the "lookup table," and append all those columns. 
    Optionally limit the field of potential fuzzy matches by other fields, on which a normal join in done. In all cases each row of table 1
    will be printed exactly once, with the single best match from table 2 appearing next to it unless there are no suitable matches, in which
    case there will be blank fields next to it."""
    override_flags = 'f'

    def add_arguments(self):
        self.argparser.add_argument('files', metavar='FILES', nargs=2, type=CSVFileType(), help='Two filenames: a main table and another \
            lookup table, where the utility will concatenate the best match from lookup to each row from main.')
        self.argparser.add_argument('-f', '--fuzzy', dest='columns',
            help='The fields to do a fuzzy match on. Either a single column name (to join on a same-named field) or something like leftname=rightname, \
                using a column from the main table then the lookup table.')
        self.argparser.add_argument('-n', '--hard', dest='hard',
            help='Fields to do essentially a left join on. Either a single column name (to join on a same-named field) or something like \
            leftname1=rightname1,leftname2=rightname2... using a column from the main table then the lookup table. You can join on multiple fields, \
            separated by commas')


    def main(self):
        
        tab = table.Table.from_csv(self.args.files[0], **self.reader_kwargs)
        lookup = table.Table.from_csv(self.args.files[1], **self.reader_kwargs)

        #store indices of columns to do the fuzzy match on
        fuzzy_columns = self.args.columns
        if not fuzzy_columns:
            self.argparser.error("Fuzzy match column -f must be specified.")
        if '=' in fuzzy_columns:
            (tab_fuzzy_field, lookup_fuzzy_field) = fuzzy_columns.split('=')
        else:
            (tab_fuzzy_field, lookup_fuzzy_field) = (fuzzy_columns,fuzzy_columns)
        tab_fuzzy_index = match_column_identifier(tab.headers(), tab_fuzzy_field)
        lookup_fuzzy_index = match_column_identifier(lookup.headers(), lookup_fuzzy_field)

            
        #store indices of columns to do a normal left join on.
        #limiting fuzzy matches to a set of hard matches on other columns is optional.
        hard_joins = []
        if self.args.hard:
            for pair in self.args.hard.split(','):
                if '=' in pair:
                    (tabfield, lookupfield) = pair.split('=')
                else:
                    (tabfield, lookupfield) = (pair,pair)
                hard_joins.append( (match_column_identifier(tab.headers(), tabfield),
                        match_column_identifier(lookup.headers(), lookupfield)) )



        if len(hard_joins)==0:
            #we're not doing any hard joins, so our pool of possible matches is everything
            join_dict = lookup.to_rows()
        else:
            #create a hash using the hard-join keys so we don't recreate a list of possible matches for the fuzzy join each time.
            #in other words, if we're doing a fuzzy join on a lawmaker's name, but limiting via hard join to records that match 
            #on state and party, we just have to do the fuzzy join on join_dict[('democrat','ny')]
            join_dict = {}

            for row in lookup.to_rows():
                hashkey = tuple([row[x[1]] for x in hard_joins])
                if hashkey not in join_dict.keys():
                    join_dict[hashkey] = []
                join_dict[hashkey].append(row)
                
                    

        output = CSVKitWriter(self.output_file, **self.writer_kwargs)
        newheaders = tab.headers() + ['match_score',] + lookup.headers()
        output.writerow( newheaders )


        def getfirstmatch(lookup_rows, lookup_fuzzy_index, fuzzy_match):
            #it's assumed that most lookup tables will have the intended match appear only once, but if there are
            #multiple rows containing the same value of the fuzzy match column, where that value was selected as 
            #the best match for the main table, we just take the first time it appears in the lookup table
            for row in lookup_rows:
                if row[lookup_fuzzy_index]==fuzzy_match:
                    return row


        for row in tab.to_rows():

            possible_matches = []
            if type(join_dict)==list: #we're not using any hard-join columns, so search the whole table
                possible_matches = join_dict
            else:
                #use the previously assembled hash to rapidly look for sets of rows that match on all hard-join fields
                hashkey = tuple([row[x[0]] for x in hard_joins]) #find values in the columns specified in the table_col side of hard_joins
                if hashkey in join_dict.keys():                
                    possible_matches = join_dict[hashkey]                
                

            if not len(possible_matches):
                output.writerow( list(row) + ['',] + ['' for x in lookup.headers()] )
            else:
                #use fuzzywuzzy's levenstein implementation to select the best match in our universe of options.
                lookup_vals = [x[lookup_fuzzy_index] for x in possible_matches]
                #the meat is all in this one line.
                #score is a number from 0 to 100 representing how good the fuzzy match is, and it becomes
                #a field in our output table so users can react accordingly.
                (fuzzy_match,fuzzy_score) = process.extractOne(row[tab_fuzzy_index],lookup_vals)
                #we could say a really bad score counts as no match, and set nomatch=True, but we won't
                lookup_row = getfirstmatch(possible_matches, lookup_fuzzy_index, fuzzy_match)
                output.writerow( list(row) + [fuzzy_score,] + list(lookup_row) )

                    
    

def launch_new_instance():
    utility = CSVFuzzyJoin()
    utility.main()
    
if __name__ == "__main__":
    launch_new_instance()
    
