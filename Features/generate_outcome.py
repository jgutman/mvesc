""" Generate Outcome table
QL command is used to replace outcomes table
Can be used for multiple outcome and cohorts definition
"""
import os, sys

pathname = os.path.dirname(sys.argv[0])
full_pathname = os.path.abspath(pathname)
split_pathname = full_pathname.split(sep="mvesc")
base_pathname = os.path.join(split_pathname[0], "mvesc")
parentdir = os.path.join(base_pathname, "ETL")
sys.path.insert(0,parentdir)
from mvesc_utility_functions import *

def main():
    schema, table = "model", "outcome2"
    source_schema, source_table = "clean", "wrk_tracking_students"
    snapshots = "all_snapshots"
    current_year = 2016
    prediction_grade_range = list(range(5,10))

    with postgres_pgconnection_generator() as connection:
        with connection.cursor() as cursor:
            insert_outcome_category_future = """
            update {source_schema}.{source_table}
                set outcome_category = 'future'
                where student_lookup in
                (select student_lookup from {source_schema}.{source_table}
                where "{last_year}" >= {min_grade} and
                "{last_year}" <= {max_grade})
            """.format(source_schema=source_schema, source_table=source_table,
                last_year=current_year-1,
                min_grade = min(prediction_grade_range),
                max_grade = max(prediction_grade_range))

            sql_drop_table = """drop table if exists {schema}.{table};""".format(schema=schema, table=table)
            cursor.execute(sql_drop_table)

            sql_create_table = """
            create table {schema}.{table} as
            select * from
            (   select distinct student_lookup,
                case
                    when outcome_category='on-time' then 0
                    when outcome_category not like 'future' then 1
                end as not_on_time,
                case
                    when outcome_category='dropout' then 1
                    when outcome_category not like 'future' then 0
                end as is_dropout,
                case
                    when outcome_category='on-time' or outcome_category='late' then 0
                    when outcome_category='dropout' then 1
                end as definite
                case
                    when outcome_category = 'future' then 1
                end as current_students
                from {source_schema}.{source_table}
                where outcome_category is not null
            ) as all_outcomes
            left join
            (   select student_lookup, min(school_year) as cohort_10th
                from {source_schema}.{snapshots}
                where grade = 10
                and outcome_category not like 'future'
                group by student_lookup
            ) as cohorts_tenth
            using(student_lookup)
            left join
            (   select student_lookup, min(school_year) as cohort_9th
                from {source_schema}.{snapshots}
                where grade = 9
                and outcome_category not like 'future'
                group by student_lookup
            ) as cohorts_ninth
            using(student_lookup)
            left join
            (   select student_lookup, min(school_year) as cohort_8th
                from {source_schema}.{snapshots}
                where grade = 8
                and outcome_category not like 'future'
                group by student_lookup
            ) as cohorts_eighth
            using(student_lookup)
            left join
            (   select student_lookup, min(school_year) as cohort_7th
                from {source_schema}.{snapshots}
                where grade = 7
                and outcome_category not like 'future'
                group by student_lookup
            ) as cohorts_seventh
            using(student_lookup)
            left join
            (   select student_lookup, min(school_year) as cohort_6th
                from {source_schema}.{snapshots}
                where grade = 6
                and outcome_category not like 'future'
                group by student_lookup
            ) as cohorts_sixth
            using(student_lookup)
            order by cohort_10th;
            """.format(schema=schema, table=table,
            source_schema=source_schema, source_table=source_table,
            snapshots=snapshots)
            cursor.execute(sql_create_table)

            for grade in prediction_grade_range:
                update_2016_cohorts = """
                update {schema}.{table}
                    set cohort_{grade_plus}th = {current_year}
                    where student_lookup in
                    (select student_lookup from {source_schema}.{source_table}
                    where "{last_year}" = {grade})
                """.format(schema=schema, table=table,
                    source_schema=source_schema, source_table=source_table,
                    grade=grade, grade_plus=grade+1,
                    last_year=current_year-1, current_year=current_year)


            connection.commit()
            print("Table {schema}.{table} created! ".format(
            schema=schema, table=table))

            # create index
            sql_create_index = "create index {schema}_{table}_lookup on {schema}.{table}(student_lookup)".format(schema=schema, table=table)
            cursor.execute(sql_create_index); connection.commit()
            print("""- Index created on {schema}.{table}(student_lookup)!""".format(schema=schema, table=table))

if __name__=='__main__':
    main()
