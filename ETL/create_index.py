""" Create index of a certain schema to make joining much faster
Input: "shema", "column"
- create index for all tables in a "schema" using "column"
- if exists index, nothing is completed

usage example:
- $`python create_index.py`
    * create index for defaults: "clean", "student_lookup"
- $`python create_index.py -s public -c StudentLookup` 
    * create index for all tables in "public" using column name "student_lookup"
""" 


import sys, os
pathname = os.path.dirname(sys.argv[0])
full_pathname = os.path.abspath(pathname)
split_pathname = full_pathname.split(sep="mvesc")
base_pathname = os.path.join(split_pathname[0], "mvesc")
parentdir = os.path.join(base_pathname, "ETL")
sys.path.insert(0,parentdir)

from optparse import OptionParser
from mvesc_utility_functions import *

def call_main(schema='clean', column='student_lookup'):
    with postgres_pgconnection_generator() as connection:
        with connection.cursor() as cursor:
            sqlcmd_table_names = "SELECT table_name FROM information_schema.tables WHERE table_schema='{}'".format(schema)
            all_table_names = list(pd.read_sql(sqlcmd_table_names, connection).table_name)
            for tab in all_table_names:
                print("""--- Trying to index {schema}.{table}... """.format(schema=schema, table=tab))
                sql_create_index = """create index {schema}_{table}_lookup_index 
                on {schema}.{table} ({column})""".format(schema=schema, table=tab, column=column)
                try:
                    cursor.execute(sql_create_index); connection.commit()
                    print(""" - Index in {schema}.{table} created!""".format(schema=schema, table=tab) )
                except:
                    print(""" - Index in {schema}.{table} exists!""".format(schema=schema, table=tab) )
                    pass

if __name__=='__main__':
    parser = OptionParser()
    parser.add_option('-s','--schema', dest='schema',
                      help="schema to create index; default 'clean' ")
    parser.add_option('-c','--column', dest='column',
                      help="column name to create index; default 'student_lookup' ")
    (options, args) = parser.parse_args()

    ### Parameters to entered from the options or use default####
    schema = 'clean'
    if options.schema:
        schema = options.schema

    column = 'student_lookup'
    if options.column:
        column = options.column

    call_main(schema=schema, column=column)

