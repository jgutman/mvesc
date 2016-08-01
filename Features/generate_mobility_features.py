from feature_utilities import *

pathname = os.path.dirname(sys.argv[0])
full_pathname = os.path.abspath(pathname)
split_pathname = full_pathname.split(sep="mvesc")
base_pathname = os.path.join(split_pathname[0], "mvesc")
parentdir = os.path.join(base_pathname, "ETL")
sys.path.insert(0,parentdir)

from mvesc_utility_functions import *

def create_temp_mobility(cursor, grade_range, table = 'mobility_counts'):
    """

    """
    query_join_mobility_features = """create temporary table {t} as
    select * from
        (select distinct(student_lookup)
        from clean.all_snapshots) student_list
    """.format(t=table)

    for max_grade in grade_range:
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

    cursor.execute(query_join_mobility_features)
    cursor.execute("select * from {t}".format(t=table))
    col_names = [i[0] for i in cursor.description]
    return(col_names[1:])

def join_mobility_transitions(cursor, grade_range,
    table = 'mobility_transitions_wide', source_table = 'transition_counts'):
    """

    """
    query_join_mobility_features = """create temporary table {t} as
    select * from
        (select distinct(student_lookup)
        from {source_table}) student_list
    """.format(t=table, source_table=source_table)

    for grade in grade_range:
        mobility_count_changes = """left join
        (select student_lookup, num_different_street street_transition_in_gr_{gr},
            num_different_district district_transition_in_gr_{gr},
            num_different_city city_transition_in_gr_{gr}
        from {source_table} where grade = {gr}) mobility_transition_gr_{gr}
        using(student_lookup)
        """.format(gr=grade, source_table=source_table)
        query_join_mobility_features += mobility_count_changes

    cursor.execute(query_join_mobility_features)
    cursor.execute("select * from {t}".format(t=table))
    col_names = [i[0] for i in cursor.description]
    return(col_names[1:])

def generate_mobility(replace = False,
        sql_script = 'mobility_changes_inprogress.sql',
        schema = 'model', table = 'mobility'):
    """
    Creates a table in the model schema with relevant mobility related features.
    features: [n_addresses_to*, n_districts_to*, n_cities_to*, n_records_to*,
        avg_address_change_to*, avg_district_change_to*, avg_city_change_to*,
        street_transition_in*, district_transition_in*, city_transition_in*]

    :param boolean replace: whether to overwrite any existing {schema}.{table}
    :param string sql_script: the filename of the sql script for building the
        intermediate tables, must be located in base_pathname/Features
    :param string schema: name of the schema for storing all generated features
    :param string table: name of the table to build and output these features
    :returns None, creates/replaces {schema}.{table} with mobility features,
        (all grade-based features, see list above)
    :rtype None
    """
    print("building {}.{}".format(schema, table))
    with postgres_pgconnection_generator() as connection:
        with connection.cursor() as cursor:
            # drop existing table and create a table with student_lookup index
            if replace:
                cursor.execute("drop table if exists {}.{}".format(
                    schema, table))
                create_feature_table(cursor, table)

            # call fn to build temporary table with counts/avgs of all addresses,
            # districts, and cities lived in up until grade x, for all grades
            # in the specified grade range and return a list of column names
            column_list = create_temp_mobility(cursor, grade_range=range(3,13))
            # take all columns from temporary mobility_counts table and join
            # into feature table with student_lookup index
            update_column_with_join(cursor, table, column_list,
                'mobility_counts')

        # model.mobility now contains first set of mobility Features
        # i.e. [n_addresses_to*, n_districts_to*, n_cities_to*, n_records_to*,
        # avg_address_change_to*, avg_district_change_to*, avg_city_change_to*]
        connection.commit()
        print('{}.{} updated with mobility_counts'.format(schema, table))

    # generate intermediate tables mobility_changes and mobility_transitions
    # to use in generating transition based mobility features
    execute_sql_script(os.path.join(base_pathname, 'Features', sql_script))
    print('intermediate tables built from sql script')

    with postgres_pgconnection_generator() as connection:
        with connection.cursor() as cursor:
            # using boolean transition based features from intermediate tables
            # count the number of true num_different_x by student, by grade
            # only one per school_year, but may be multiple school_years
            # per grade if retained -- maybe this should just be 0/1 always
            query_count_transitions = """
            create temporary table transition_counts as
            select student_lookup, grade,
            count(case when different_street then 1 end) num_different_street,
            count(case when different_district then 1 end) num_different_district,
            count(case when different_city then 1 end) num_different_city
            from mobility_transitions
            group by student_lookup, grade;
            """
            cursor.execute(query_count_transitions)

            # call fn to build temporary table with counts of transitions
            # between or during grades, ie. is address, district, city all the
            # same as last years, grade by grade for all grades
            # in the specified grade range and return a list of column names
            column_list = join_mobility_transitions(cursor,
                grade_range=range(3,13))
            # take all columns from temporary mobility_transitions_wide table
            # and join into feature table with student_lookup index
            update_column_with_join(cursor, table, column_list,
                'mobility_transitions_wide')

        # model.mobility now contains second set of mobility features
        # i.e. [street_transition_in*, district_transition_in*, city_transition_in*]
        connection.commit()
        print('{}.{} updated with mobility_transitions_wide'.format(schema, table))

def main():
    generate_mobility(replace=True)

if __name__ == '__main__':
    main()
