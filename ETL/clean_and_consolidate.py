from  mvesc_utility_functions import *
import consolidating_tables
import build_student_tracking

with postgres_pgconnection_generator() as connection:
    with connection.cursor() as cursor:
        #consolidating tables in clean schema
        consolidating_tables.main()

        #absences
        execute_sql_script("clean_absences.sql")
        execute_sql_script("all_absences_generate_mm_day_wkd.sql")

        #grades
#        execute_sql_script("clean_grades.sql") 
#        this script doesn't seem to be on github anywhere?

        #tests
        execute_sql_script("clean_oaaogt_0616.sql")

        #snapshots
        execute_sql_script("cleaning_all_snapshots.sql")
        clean_column(cursor, values="student_status.json", 
                      old_column_name="status_code",
                      table_name="all_snapshots", 
                      new_column_name="status", replace=0) 
#        script to add missing graduates?

        #additional tables for analysis
        build_student_tracking.main()
#        need script for all_graduates table?
#        additional script for adding labels to tracking table?

    connection.commit()

