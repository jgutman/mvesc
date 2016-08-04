from feature_utilities import *

pathname = os.path.dirname(sys.argv[0])
full_pathname = os.path.abspath(pathname)
split_pathname = full_pathname.split(sep="mvesc")
base_pathname = os.path.join(split_pathname[0], "mvesc")
parentdir = os.path.join(base_pathname, "ETL")
sys.path.insert(0,parentdir)

from mvesc_utility_functions import *

def create_temp_mobility(cursor, grade_range, table = 'mobility_counts',
    source_schema = 'clean', source_table = 'all_snapshots'):
    """
    Creates a temporary table containing the first set of mobility features,
    count-based cumulative counts and averages for number of distinct addresses,
    districts, and cities (ignoring alternations) up to and including grade x,
    for all grades in specified grade range.
    Draws features from {source_schema}.{source_table} and stores them in {table}.

    features: [n_addresses_to*, n_districts_to*, n_cities_to*, n_records_to*,
        avg_address_change_to*, avg_district_change_to*, avg_city_change_to*]

    :param psycopg2.cursor: cursor to execute queries on the database
    :param list/range(int) grade_range: which grades to generate features for
        (each will be appended to the feature name in standard feature_x_gr_k format)
    :param string table: name of temporary table where these features are stored
    :param string source_schema: name of schema where address, district, city
        features should be drawn from
    :param string source_table: name of table where features to be drawn from
    :returns list of column names as string in newly created temp table
    :rtype list[string]
    """
    # create table with all student_lookups to store features for
    query_join_mobility_features = """create temporary table {t} as
    select * from
        (select distinct(student_lookup)
        from {source_schema}.{source_table}) student_list
    """.format(t=table, source_schema=source_schema, source_table=source_table)

    # for each student, get the number of distinct addresses, cities, districts
    # lived in up to the specified max_grade, also store the total number of
    # non-null records going into that count (how long they've been in data)
    # then compute average as (number_addresses - 1) / number_records
    for max_grade in grade_range:
        mobility_count_changes = """left join
        (select student_lookup,
            count(distinct street_clean) n_addresses_to_gr_{gr},
            count(distinct district) n_districts_to_gr_{gr},
            count(distinct city) n_cities_to_gr_{gr},
            count(school_year) n_records_to_gr_{gr},
            (count(distinct street_clean)-1)/
                greatest(1, count(distinct grade))::float
                avg_address_change_to_gr_{gr},
            (count(distinct district)-1)/
                greatest(1, count(distinct grade))::float
                avg_district_change_to_gr_{gr},
            (count(distinct city)-1)/
                greatest(1, count(distinct grade))::float
                avg_city_change_to_gr_{gr}
        from {source_schema}.{source_table} where grade <= {gr}
        group by student_lookup) mobility_gr_{gr}
        using(student_lookup)
        """.format(gr=max_grade,
            source_schema=source_schema, source_table=source_table)
        query_join_mobility_features += mobility_count_changes

    cursor.execute(query_join_mobility_features)
    # get column names in temporary table just created and return all in a list
    # remove student_lookup from list of column names returned
    cursor.execute("select * from {t}".format(t=table))
    col_names = [i[0] for i in cursor.description]
    return(col_names[1:])

def join_mobility_transitions(cursor, grade_range,
    table = 'mobility_transitions_wide', source_table = 'transition_counts'):
    """
    Creates a temporary table containing the second set of mobility features,
    transition-based grade to grade counts of changes from previous school year
    for all grades in specified grade range.
    Draws features from {source_table} and stores them in {table}.

    features: [street_transition_in*, district_transition_in*, city_transition_in*]

    :param psycopg2.cursor: cursor to execute queries on the database
    :param list/range(int) grade_range: which grades to generate features for
        (each will be appended to the feature name in standard feature_x_gr_k format)
    :param string table: name of temporary table where these features are stored
    :param string source_table: name of temporary table where features to be drawn from
    :returns list of column names as string in newly created temp table
    :rtype list[string]
    """
    # create table with all student_lookups to store features for
    query_join_mobility_features = """create temporary table {t} as
    select * from
        (select distinct(student_lookup)
        from {source_table}) student_list
    """.format(t=table, source_table=source_table)

    # for each student, return true or false for whether or not their address
    # has changed at least once since their address from the previous grade
    for grade in grade_range:
        mobility_count_changes = """left join
        (select student_lookup,
            (num_different_street >=1) street_transition_in_gr_{gr},
            (num_different_district >=1) district_transition_in_gr_{gr},
            (num_different_city >=1) city_transition_in_gr_{gr}
        from {source_table} where grade = {gr}) mobility_transition_gr_{gr}
        using(student_lookup)
        """.format(gr=grade, source_table=source_table)
        query_join_mobility_features += mobility_count_changes

    cursor.execute(query_join_mobility_features)
    # get column names in temporary table just created and return all in a list
    # remove student_lookup from list of column names returned
    cursor.execute("select * from {t}".format(t=table))
    col_names = [i[0] for i in cursor.description]
    return(col_names[1:])

def find_midyear_withdrawals(cursor, grade_range, table,
        source_schema='clean', source_table='all_snapshots'):
    """

    """
    query_multiple_records_per_year = """
    create temporary table withdrawals_by_month as
    select student_lookup, school_year, grade, status, street_clean, district,
        city, district_withdraw_date, district_admit_date,
        extract(month from district_withdraw_date) withdraw_month
    from {source_schema}.{source_table}
    where (student_lookup, school_year) in
    (select student_lookup, school_year from {source_schema}.{source_table}
    group by student_lookup, school_year
    having count(*) > 1)
    order by student_lookup, school_year, district_withdraw_date;
    """.format(source_schema=source_schema, source_table=source_table)

    query_temp_midyear_withdrawals_long_format = """
    create temporary table midyear_withdrawals_long as
    select student_lookup, grade,
    count(case when withdraw_month < {summer_start} or
        withdraw_month > {summer_end} then 1 end) as mid_year_withdraw
    from withdrawals_by_month
    group by student_lookup, grade
    """.format(summer_start = 5, summer_end = 9)

    cursor.execute(query_multiple_records_per_year)
    cursor.execute(query_temp_midyear_withdrawals_long_format)

    # create table with all student_lookups to store features for
    query_join_mobility_features = """create temporary table {t} as
    select * from
        (select distinct(student_lookup)
        from {source_schema}.{source_table}) student_list
    """.format(t=table, source_schema=source_schema, source_table=source_table)

    for grade in grade_range:
        mobility_changes_midyear = """left join
        (select student_lookup,
            (mid_year_withdraw > 0) as mid_year_withdraw_gr_{gr}
        from midyear_withdrawals_long where grade = {gr})
        mid_year_withdraw_gr_{gr}
        using(student_lookup)
        """.format(gr=grade)
        query_join_mobility_features += mobility_changes_midyear

    cursor.execute(query_join_mobility_features)
    # get column names in temporary table just created and return all in a list
    # remove student_lookup from list of column names returned
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
        print("{}.{} updated with mobility_counts".format(schema, table))

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
            print("{}.{} updated with mobility_transitions_wide".format(
                schema, table))

            # model.mobility now contains second set of mobility features
            # i.e. [street_transition_in*, district_transition_in*,
            # city_transition_in*]

            column_list = find_midyear_withdrawals(cursor,
                grade_range=range(3,13), table='midyear_withdrawals_wide')
            # take all columns from temporary midyear_withdrawals_wide table
            # and join into feature table with student_lookup index
            update_column_with_join(cursor, table, column_list,
                'midyear_withdrawals_wide')
            print("{}.{} updated with midyear_withdrawals_wide".format(
                schema, table))

        connection.commit()

def set_table_negative_null(table='mobility', schema='model'):
    """
    Set negative data points to NULL in a table
   
    :param str table: table name
    :param str schema: schema name
    :return None:
    """

    with postgres_pgconnection_generator() as connection:
        connection.autocommit = True
        with connection.cursor() as cursor:
            table_df = pd.read_sql_query("select * from {schema}.{table} limit 1000;".format(
                    schema=schema, table=table), connection)
            table_df = table_df.select_dtypes(include=[np.number])
            numeric_columns = table_df.columns
            for column in numeric_columns:
                sql_set_null_0 = """
                update only {schema}.{table}
                set {column}=NULL
                where {column}<0.0;
                """.format(schema=schema, table=table, column=column)
                cursor.execute(sql_set_null_0)
            connection.commit()
    return None



def main():
    generate_mobility(replace=True)
    set_table_negative_null(table='mobility', schema='model');

if __name__ == '__main__':
    main()
