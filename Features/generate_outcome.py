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

def main(argv): 
    """
    arguments: model_schema, clean_schema, current_year
    """
    schema, table = argv[1], "outcome"
    source_schema, source_table = argv[0], "wrk_tracking_students"
    snapshots = "all_snapshots"
    current_year = argv[2]
    prediction_grade_range = list(range(5,10))
    prediction_outcome_name = 'future'

    with postgres_pgconnection_generator() as connection:
        with connection.cursor() as cursor:
            # create model schema
            cursor.execute("""
            create schema if not exists {};
            """.format(schema))
            connection.commit()
            
            # add 'future' outcome category for current students
            insert_outcome_category_predictions = """
            update {source_schema}.{source_table}
                set outcome_category = '{predictions}'
                where student_lookup in
                (select student_lookup from {source_schema}.{source_table}
                where "{last_year}" >= {min_grade} and
                "{last_year}" <= {max_grade} and outcome_category is null)
            """.format(source_schema=source_schema, source_table=source_table,
                       last_year=current_year-1, 
                       predictions = prediction_outcome_name,
                       min_grade = min(prediction_grade_range),
                       max_grade = max(prediction_grade_range))
            cursor.execute(insert_outcome_category_predictions)

            sql_drop_table = """drop table if exists {schema}.{table};
            """.format(schema=schema, table=table)
            cursor.execute(sql_drop_table)

            # build outcome table
            sql_create_table = """
            create table {schema}.{table} as
            select * from
            (   select distinct student_lookup,
                case
                    when outcome_category='on-time' then 0
                    when outcome_category not like '{predictions}' then 1
                end as not_on_time,
                case
                    when outcome_category='dropout' then 1
                    when outcome_category not like '{predictions}' then 0
                end as is_dropout,
                case
                    when outcome_category='on-time'
                      or outcome_category='late' then 0
                    when outcome_category='dropout' then 1
                end as definite,
                case
                    when outcome_category = '{predictions}' then 1
                end as current_students,
                outcome_bucket,
                outcome_category
                from {source_schema}.{source_table}
                where outcome_category is not null
            ) as all_outcomes
            left join
            (   select student_lookup, min(school_year) as cohort_10th
                from {source_schema}.{snapshots}
                where grade = 10
                group by student_lookup
            ) as cohorts_tenth
            using(student_lookup)
            left join
            (   select student_lookup, min(school_year) as cohort_9th
                from {source_schema}.{snapshots}
                where grade = 9
                group by student_lookup
            ) as cohorts_ninth
            using(student_lookup)
            left join
            (   select student_lookup, min(school_year) as cohort_8th
                from {source_schema}.{snapshots}
                where grade = 8
                group by student_lookup
            ) as cohorts_eighth
            using(student_lookup)
            left join
            (   select student_lookup, min(school_year) as cohort_7th
                from {source_schema}.{snapshots}
                where grade = 7
                group by student_lookup
            ) as cohorts_seventh
            using(student_lookup)
            left join
            (   select student_lookup, min(school_year) as cohort_6th
                from {source_schema}.{snapshots}
                where grade = 6
                group by student_lookup
            ) as cohorts_sixth
            using(student_lookup);
            """.format(schema=schema, table=table,
                source_schema=source_schema, source_table=source_table,
                snapshots=snapshots, predictions=prediction_outcome_name)
            cursor.execute(sql_create_table)

            for grade in prediction_grade_range:
                update_current_cohorts = """
                update {schema}.{table}
                    set cohort_{grade_plus}th = {current_year}
                    where student_lookup in
                    (select student_lookup from {source_schema}.{source_table}
                    where "{last_year}" = {grade})
                """.format(schema=schema, table=table,
                    source_schema=source_schema, source_table=source_table,
                    grade=grade, grade_plus=grade+1,
                    last_year=current_year-1, current_year=current_year)
                cursor.execute(update_current_cohorts)

            connection.commit()
            print("Table {schema}.{table} created! ".format(
            schema=schema, table=table))

            # create index
            sql_create_index = "create index {schema}_{table}_lookup on {schema}.{table}(student_lookup)".format(schema=schema, table=table)
            cursor.execute(sql_create_index); connection.commit()
            print("- Index created on {schema}.{table}(student_lookup)!".format(
                schema=schema, table=table))

if __name__=='__main__':
    main()
