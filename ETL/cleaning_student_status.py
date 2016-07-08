from  mvesc_utility_functions import *

with postgres_pgconnection_generator() as connection:
    with connection.cursor() as cursor:
        clean_column(cursor, "student_status.json", "status_code",\
                     "all_snapshots", "status", 0) 
    connection.commit()

