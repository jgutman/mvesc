from  mvesc_utility_functions import *

with postgres_pgconnection_generator() as connection:
    with connection.cursor() as cursor:
        #consolidating tables in clean schema
        ### consolidating_tables.py

        #absences
        execute_sql_script("clean_absences.sql")

        #grades
        execute_sql_script("clean_grades.sql")

        #tests
        execute_sql_script("clean_oaaogt_0616.sql")

        #snapshots
        execute_sql_script("cleaning_all_snapshots.sql")
        clean_column(cursor, values="student_status.json", 
                      old_column_name="status_code",
                      table_name="all_snapshots", 
                      new_column_name="status", replace=0) 

        #additional tables for analysis
    connection.commit()

