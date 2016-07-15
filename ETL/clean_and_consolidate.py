from  mvesc_utility_functions import *
import consolidating_tables
import build_student_tracking 
import build_cohort_tree_counts
import cleaning_all_snapshots

#consolidating tables in clean schema
consolidating_tables.main()
print('consolidated tables')

#absences
execute_sql_script("clean_absences.sql")
execute_sql_script("all_absences_generate_mm_day_wkd.sql")
print('all_absences cleaned')

#grades
execute_sql_script("clean_grades.sql")
print('all_grades cleaned')

#tests
execute_sql_script("clean_oaaogt.sql")
# add other test cleaning scripts here
print('oaaogt cleaned')

#snapshots
cleaning_all_snapshots.main()
print('all_snapshots cleaned')

#additional tables for analysis
execute_sql_script("build_graduates_table_from_snapshots.sql"
build_student_tracking.main()
# additional script for adding labels to tracking table
build_cohort_tree_counts.main()
print('additional tables built')
