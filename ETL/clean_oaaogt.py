import os, sys

pathname = os.path.dirname(sys.argv[0])
full_pathname = os.path.abspath(pathname)
split_pathname = full_pathname.split(sep="mvesc")
base_pathname = os.path.join(split_pathname[0], "mvesc")
parentdir = os.path.join(base_pathname, "ETL")
sys.path.insert(0,parentdir)

from mvesc_utility_functions import clean_column,\
    postgres_pgconnection_generator

def clean_oaaogt(raw_schema, clean_schema):
    """
    Python wrapper for sql script 

    :param str clean_schema: name of the clean schema
    :rtype: None
    """
    with postgres_pgconnection_generator() as connection:
        with connection.cursor() as cursor:

            # copy from raw schema
            cursor.execute("""
            drop table if exists {clean_schema}.oaaogt;
            create table {clean_schema}.oaaogt as table
            {raw_schema}."OAAOGT_712016";
            alter table {clean_schema}.oaaogt rename "StudentLookup"
            to student_lookup;
            """.format(clean_schema=clean_schema,raw_schema=raw_schema))


            # get lowercase commands
            cursor.execute("""
            select  'alter table ' || quote_ident(c.table_schema) || '.'
            || quote_ident(c.table_name) || ' rename "' || c.column_name || 
            '" to ' || quote_ident(lower(c.column_name)) || ';' 
            as lower_column_cmds
            from information_schema.columns as c
            where c.table_schema = \'{clean_schema}\'
                and c.table_name = 'oaaogt'
                and c.column_name <> lower(c.column_name) 
            order by c.table_schema, c.table_name, c.column_name;
            """.format(clean_schema=clean_schema))
            lower_column_cmds = cursor.fetchall()
            lower_column_cmds = [c[0] for c in lower_column_cmds]
            
            # make all column names lowercase
            for c in lower_column_cmds:
                cursor.execute(c)

            # date of birth
            cursor.execute("""
            alter table {s}.oaaogt alter column dob type date using
            to_date(dob, 'MM/DD/YYYY');
            """.format(s=clean_schema))
            
            # gender
            cursor.execute("""
            update {s}.oaaogt set gender = upper(left(trim(gender),1));
            """.format(s=clean_schema))

            # ethnicity
            clean_column(cursor,os.path.join(base_pathname,'ETL',
                                        'json/ethnicity.json'),
                         "ethnicity", "oaaogt")
            
        connection.commit()
