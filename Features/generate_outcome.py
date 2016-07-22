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
    schema, table = "model", "outcome"
    source_schema, source_table = "clean", "wrk_tracking_students"
    snapshots = "all_snapshots"

    with postgres_pgconnection_generator() as connection:
        with connection.cursor() as cursor:
            sql_drop_table = """drop table if exists {schema}.{table};""".format(schema=schema, table=table)
            cursor.execute(sql_drop_table)
            sql_drop_temp_table = """drop table if exists temp_{table};""".format(table=table)
            cursor.execute(sql_drop_temp_table)

            sql_create_table = """
            create temp table temp_{table} as
            select * from
            (   select distinct student_lookup,
                case
                    when outcome_category='on-time' then 0
                    else 1
                end as not_on_time,
                case
                    when outcome_category='dropout' then 1
                    else 0
                end as is_dropout
                from {source_schema}.{source_table}
                where outcome_category is not null
            ) as all_outcomes""".format(table=table,
            source_schema=source_schema, source_table=source_table)
            cursor.execute(sql_create_table)

            # create index
            sql_create_index = "create index temp_{table}_lookup on temp_{table}(student_lookup)".format(table=table)
            cursor.execute(sql_create_index)


            sql_join_cohort="""
            create table {schema}.{table} as
            select * from temp_{table}
            left join
            (   select student_lookup, min(school_year) as cohort_9th
                from {source_schema}.{snapshots}
                where grade = 9
                group by student_lookup
            ) as cohorts_ninth
            using(student_lookup)
            left join
            (   select student_lookup, min(school_year) as cohort_6th
                from {source_schema}.{snapshots}
                where grade = 6
                group by student_lookup
            ) as cohorts_sixth
            using(student_lookup)
            order by cohort_9th;
            """.format(schema=schema, table=table,
            source_schema=source_schema, source_table=source_table,
            snapshots=snapshots)
            cursor.execute(sql_join_cohort)
            connection.commit()
            print("""- Table "{schema}"."{table}" created! """.format(
            schema=schema, table=table))

            # create index
            sql_create_index = "create index {schema}_{table}_lookup on {schema}.{table}(student_lookup)".format(schema=schema, table=table)
            cursor.execute(sql_create_index); connection.commit()
            print("""- Index created on {schema}.{table}(student_lookup)!""".format(schema=schema, table=table))

if __name__=='__main__':
    main()
