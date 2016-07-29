from mvesc_utility_functions import *
import cleaning_grad_grades
import clean_addresses

def main():
    execute_sql_script("cleaning_all_snapshots.sql")
    with postgres_pgconnection_generator() as connection:
        with connection.cursor() as cursor:
            clean_column(cursor, values="student_status.json",
                         old_column_name="status_code",
                         table_name="all_snapshots", replace=1)
            clean_column(cursor, values="student_status.json",
                         old_column_name="status_desc",
                         table_name="all_snapshots", replace=1)
            cursor.execute("""
            alter table clean.all_snapshots add column status text;
            alter table clean.all_snapshots alter column status type
            text using coalesce(status_code, status_desc);
            alter table clean.all_snapshots drop column status_code;
            alter table clean.all_snapshots drop column status_desc;
            """)
    connection.commit()
    cleaning_grad_grades.main()
    execute_sql_script("update_all_snapshots_with_missing_graduates.sql")
    clean_addresses.main()
