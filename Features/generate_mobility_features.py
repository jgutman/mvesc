from feature_utilities import *

pathname = os.path.dirname(sys.argv[0])
full_pathname = os.path.abspath(pathname)
split_pathname = full_pathname.split(sep="mvesc")
base_pathname = os.path.join(split_pathname[0], "mvesc")
parentdir = os.path.join(base_pathname, "ETL")
sys.path.insert(0,parentdir)

from mvesc_utility_functions import *

def create_temp_mobility(cursor, grade_range, table = 'mobility_counts'):
    query_join_mobility_features = """create temporary table {t} as
    select * from
        (select distinct(student_lookup)
        from clean.all_snapshots) student_list
    """.format(t=table)

    for max_grade in grade_range:
        print(max_grade)
        mobility_count_changes = """left join
        (select student_lookup, count(distinct street_clean) n_addresses_to_gr_{gr},
            count(distinct district) n_districts_to_gr_{gr},
            count(distinct city) n_cities_to_gr_{gr},
            count(school_year) n_records_to_gr_{gr},
            (count(distinct street_clean)-1)/
                greatest(1, count(street_clean))::float
                avg_address_change_to_gr_{gr},
            (count(distinct district)-1)/
                greatest(1, count(district))::float
                avg_district_change_to_gr_{gr},
            (count(distinct city)-1)/
                greatest(1, count(city))::float
                avg_city_change_to_gr_{gr}
        from clean.all_snapshots where grade <= {gr}
        group by student_lookup) mobility_gr_{gr}
        using(student_lookup)
        """.format(gr=max_grade)
        query_join_mobility_features += mobility_count_changes

    print(query_join_mobility_features)
    cursor.execute(query_join_mobility_features)
    cursor.execute("select * from {t}".format(t=table))
    col_names = [i[0] for i in cursor.description]
    return(col_names[1:])

def generate_mobility(replace = False,
        sql_script = 'mobility_changes_inprogress.sql',
        schema = 'model', table = 'mobility'):

    print("building {}.{}".format(schema, table))
    with postgres_pgconnection_generator() as connection:
        with connection.cursor() as cursor:
            if replace:
                cursor.execute("drop table if exists {}.{}".format(
                    schema, table))
                create_feature_table(cursor, table)

            # some code to generate the feature
            # in column new_col_1, new_col_2, etc in table new_table
            # following step will be more efficient
            # if new_table has an index

            column_list = create_temp_mobility(cursor, grade_range=range(3,13))
            update_column_with_join(cursor, table, column_list,
                'mobility_counts')

            # optional parameters:
            #    source_schema - if the source is not a temporary table
            # note: there is no longer an optional parameter for new column
            # names - they will be the same in the feature table as
            # they are in the table you feed in
        connection.commit()

        execute_sql_script(sql_script)

        with postgres_pgconnection_generator() as connection:
            with connection.cursor() as cursor:
                # do something

def main():
    generate_mobility(replace=True)

if __name__ == '__main__':
    main()
