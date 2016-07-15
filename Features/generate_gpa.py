""" Generate GPA
Procedures:
1. Read from outcome table to get student_lookups;
2. Generate `model.demographics` from `clean.all_snapshots`
"""
import os, sys
from os.path import isfile, join, abspath, basename

pathname = os.path.dirname(sys.argv[0])
full_pathname = os.path.abspath(pathname)
split_pathname = full_pathname.split(sep="mvesc")
base_pathname = os.path.join(split_pathname[0], "mvesc")
parentdir = os.path.join(base_pathname, "ETL")
sys.path.insert(0,parentdir)
from mvesc_utility_functions import *

def main():
    # schema, table = "model", "grades"
    # source_schema, source_table = "clean", "all_grades"
    # with postgres_pgconnection_generator() as connection:
    #     with connection.cursor() as cursor:
    #         # drop and create table
    #         sql_drop = "drop table if exists {schema}.{table};"\
    #             .format(schema=schema, table=table)
    #         sql_create = """
    #         create table {schema}.{table} as 
    #         ( select distinct student_lookup
    #           from clean.wrk_tracking_students
    #           where outcome_category is not null
    #         );""".format(schema=schema, table=table)           
    #         cursor.execute(sql_drop);
    #         cursor.execute(sql_create); 
    #         sql_create_index = """
    #         create index lookup_index on {schema}.{table}(student_lookup)
    #         """.format(schema=schema, table=table)
    #         cursor.execute(sql_create_index)
    #         connection.commit()
    #         print(""" - Table "{schema}"."{table}" created!"""\
    #               .format(schema=schema, table=table))
    
    ##### GPA #####
    with postgres_pgconnection_generator() as connection:
        with connection.cursor() as cursor:

            # grabbing high school grades
            cursor.execute("""
            create temp table high_school as select * from 
            clean.all_grades where grade >= 9;
            """)
            # selecting numeric grades
            cursor.execute("""
             create temp table numeric_grades as
             select * from high_school where 
                 mark like '0%' or mark like '1%' or mark like '2%' or 
                 mark like '3%' or mark like '4%' or mark like '5%' or
                 mark like '6%' or mark like '7%' or mark like '8%' or 
                 mark like '9%';
             alter table numeric_grades alter column mark 
                 type float using mark::float;
             alter table numeric_grades alter column mark type float using
             case when  mark != 1 and mark != 0 and mark != 200 then mark end;
            """)
            # selecting letter grades
            cursor.execute("""
            create temp table letter_grades as
            select * from high_school where 
                lower(mark) like 'a%' or  lower(mark) like 'b%' or  
                lower(mark) like 'c%' or  lower(mark) like 'd%' or  
                lower(mark) like 'f%';
            alter table letter_grades alter column mark 
                type text using lower(mark);
            delete from letter_grades where 
                mark like 'ap' or mark like 'fw' or mark like 'dw' or 
                mark like 'fa' or mark like 'blk';
            """)
            # standardizing numeric grades
            cursor.execute("""
            create temp table numeric_standard_grades as
            select student_lookup, case
                when mark < 60 then 0
                when mark < 63 then 0.7
                when mark < 67 then 1
                when mark < 70 then 1.3
                when mark < 73 then 1.7
                when mark < 77 then 2
                when mark < 80 then 2.3
                when mark < 83 then 2.7
                when mark < 87 then 3
                when mark < 90 then 3.3
                when mark < 94 then 3.7
                when mark < 100 then 4
            end as "mark" from numeric_grades;
            """)
            # standardizing letter grades
            cursor.execute("""
            create temp table letter_standard_grades as
            select student_lookup, case
                when mark like 'a' or mark like 'a+' then 4
                when mark like 'a-' then 3.7
                when mark like 'b+' then 3.3
                when mark like 'b' then 3
                when mark like 'b-' then 2.7
                when mark like 'c+' then 2.3
                when mark like 'c' then 2
                when mark like 'c-' then 1.7
                when mark like 'd+' then 1.3
                when mark like 'd' then 1
                when mark like 'd-' then 0.7
                when mark like 'f' then 0
            end as "mark" from letter_grades;
            """)
            # unioning standardized grades
            cursor.execute("""
            create temp table standard_grades as 
            select * from numeric_standard_grades 
            union all 
            select * from  letter_standard_grades;
            """)
            # computing gpa and saving feature table
            cursor.execute("""
            drop table if exists model.grades;
            create table model.grades as 
            select student_lookup, 
            avg(mark) as "high_school_gpa"
            from standard_grades group by student_lookup;
            """)
        connection.commit()

if __name__=='__main__':
    main()
