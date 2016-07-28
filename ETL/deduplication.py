import os, sys
from os.path import isfile, join, abspath, basename

pathname = os.path.dirname(sys.argv[0])
full_pathname = os.path.abspath(pathname)
split_pathname = full_pathname.split(sep="mvesc")
base_pathname = os.path.join(split_pathname[0], "mvesc")
parentdir = os.path.join(base_pathname, "ETL")
sys.path.insert(0,parentdir)
from mvesc_utility_functions import *

def add_id(cursor, table, schema='clean'):
    cursor.execute("alter table {}.{} add column id serial"\
                   .format(schema,table))

def remove_residents(cursor):
    cursor.execute("delete from clean.all_snapshots where status = 'resident';")

def remove_duplicates(cursor, cols, table, schema='clean'):
    """
    Replaces the given table with one distinct on the given column list
    Max values taken for all other columns

    :param pg cursor object cursor: cursor for psql database
    :param list cols: list of strings giving column names that should be unique
    :param string table: table name in the database
    :param str schema: schema name in database
    """
    # For identical lookup, district, school, grade, and year there are
    # never more than 2 records sharing these 5 traits in all_snapshots
    # In all examples I looked at all columns where identical or one record had 
    # a value and the other record had null, so MAX should only be taking 
    # the non-null value

    other_cols = get_column_names(cursor, table, schema=schema)
    for c in cols:
        other_cols.remove(c)
    dedupe_query = "create temp table deduped_{} as select ".format(table)
    for c in cols:
        dedupe_query += "{col}, ".format(col=c)
    for c in other_cols:
        dedupe_query += "max({col}) as {col}, ".format(col=c)
    dedupe_query = dedupe_query[:-2] + """
    from {0}.{1} 
    group by 
    """.format(schema,table)
    for c in cols:
        dedupe_query += " {}, ".format(c)
    dedupe_query = dedupe_query[:-2]
    
    cursor.execute(dedupe_query)
    cursor.execute("drop table {}.{};".format(schema,table))
    cursor.execute("""
    create table {schema}.{table} as
    select * from deduped_{table}
    """.format(schema=schema, table=table))
    print('duplicates removed from {}.{}!'.format(schema,table))

def remove_trails(cursor):
    """
    Removes trailing records (more than two consecutive years in the same grade 
    in the same school) from clean.all_snapshots

    :param pg cursor object cursor: cursor for psql database
    """
    grade_count_query = """
    create temp table grade_counts as
    select student_lookup, """

    for g in range(1,13):
        grade_count_query += \
        "sum(case when grade={gr} then 1 else 0 end) as num_{gr}, ".format(gr=g)

    grade_count_query = grade_count_query[:-2] + \
                        " from clean.all_snapshots group by student_lookup;"

    cursor.execute(grade_count_query)

    add_cols_query = """
    alter table grade_counts add column max_num int;
    alter table grade_counts alter column max_num type int using
    greatest(num_1,num_2,num_3,num_4,num_5,num_6,num_7,num_8,num_9,
             num_10,num_11,num_12);
    
    alter table grade_counts add column max_num_grade int;
    alter table grade_counts alter column max_num_grade type int using
    case 
    """
    for g in range(1,13):
        add_cols_query += """
        when num_{gr} = max_num then {gr} """\
            .format(gr=g)
    add_cols_query += " end;"
    cursor.execute(add_cols_query)

    cursor.execute("""
    create temp table to_keep as
    select distinct on (student_lookup, grade, district) 
    t1.*, max_num, max_num_grade
    from clean.all_snapshots as t1
    left join 
    grade_counts as t2
    on t1.student_lookup = t2.student_lookup 
    order by student_lookup,grade, district, school_year
    """)

    cursor.execute(""" 
    create temp table joined_grade_counts as select t1.id,max_num,max_num_grade
    from clean.all_snapshots as t1
    left join 
    grade_counts as t2
    on t1.student_lookup = t2.student_lookup;
    """)

    cursor.execute("""
    delete from clean.all_snapshots as s using joined_grade_counts
    where s.id not in (select id from to_keep)
        and (joined_grade_counts.id = s.id 
            and max_num > 2 
            and grade = max_num_grade)
    """)
    print('trails deleted!')


def main():
    with postgres_pgconnection_generator() as connection:
        with connection.cursor() as cursor:
            cols = ['student_lookup', 'district', 'school_code', 'grade', 
                    'school_year']
            add_id(cursor, 'all_snapshots')
            remove_residents(cursor)
            remove_duplicates(cursor, cols, 'all_snapshots')
            connection.commit()
            remove_trails(cursor)
            connection.commit()
    # as of 7/28 this left 4 students with conflicting grade levels -
    # student lookups 70212 (conflicting electronic school record), 
    # 37529 (two people merged), and 62594 and 2486 (dealt with manually)

if __name__ == "__main__":
    main()
