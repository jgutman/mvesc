""" Generate GPA
Procedures:
1. Read from tracking table to get student_lookups;
2. Generate `model.grades` from `clean.all_grades`
"""
from feature_utilities import *

def generate_gpa(grade_range=range(3,11),replace=False):
    schema, table = "model", "grades"
    with postgres_pgconnection_generator() as connection:
        with connection.cursor() as cursor:
            # creating base table (if not existing)
            create_feature_table(cursor, table, replace=replace)
            
            # grabbing high school grades
            cursor.execute("""
            create temp table grades as select * from 
            clean.all_grades where
            student_lookup in
            (select student_lookup from model.outcome)
            and grade < 11;
            """)
            
            # selecting numeric grades
            cursor.execute("""
             create temp table numeric_grades as
             select * from grades where 
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
            select * from grades where 
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
            end as "mark", grade
            from numeric_grades;
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
            end as "mark", grade
            from letter_grades;
            """)
            
            # unioning standardized grades
            cursor.execute("""
            create temp table standard_grades as 
            select * from numeric_standard_grades 
            union all 
            select * from  letter_standard_grades;
            """)
            
            # computing gpa
            cursor.execute("""
            create temp table gpa as 
            select student_lookup, 
            avg(mark) as "cumulative_gpa"
            from standard_grades group by student_lookup;
            """)
            
            # yearly gpa
            # for grade in grade_range:
            #     cursor.execute("""
            #     create temp table gpa_{grade} as
            #     select student_lookup,
            #     avg(mark) as "gpa_gr_{grade}"
            #     from standard_grades 
            #     where grade = {grade}
            #     group by student_lookup
            #     """.format_map({'grade':grade}))
            
            #     sql_create_index = """
            #     create index temp_lookup_index_{gr} on 
            #     {schema}.{table}(student_lookup)            
            #     """.format(gr=grade,schema=schema, table=table)
            #     cursor.execute(sql_create_index)
           
            # computing gpa and saving feature table
            # update_column_with_join(cursor, table, ['cumulative_gpa_gr_{}'\
            #                         .format(max(grade_range))],
            #                         'gpa',
            #                         source_column_list=['cumulative_gpa']) 
            #for grade in grade_range:
                #update_column_with_join(cursor, table, 
                #                       column_list=['gpa_gr_{}'.format(grade)],
                #                       source_table='gpa_{}'.format(grade))
        connection.commit()

def main():
    generate_gpa()

if __name__=='__main__':
    main()
