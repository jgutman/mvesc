from  mvesc_utility_functions import *
import consolidating_tables
from clean_absences import clean_absences, \
    all_absences_generate_mm_day_wkd, \
    all_absences_add_grade_column
from clean_grades import clean_grades
from clean_oaaogt import clean_oaaogt
from clean_snapshots import clean_snapshots
from build_graduates import build_graduates
import build_student_tracking
import build_cohort_tree_counts
import deduplication
import create_index
import build_clean_intervention_table
import generate_consec_absence_intermediate_tables



def main():
    raw_schema = 'public'
    clean_schema = 'new_clean'

    #consolidating tables in clean schema
    consolidating_tables.main([raw_schema, clean_schema])
    print('consolidated tables')
    
    #absences
    clean_absences(clean_schema)
    all_absences_generate_mm_day_wkd(clean_schema)
    print('all_absences cleaned')
    
    #grades
    clean_grades(clean_schema)
    print('all_grades cleaned')
    
    #tests
    clean_oaaogt(raw_schema, clean_schema)
    print('oaaogt cleaned')
    
    #snapshots
    clean_snapshots(clean_schema)
    deduplication.main([clean_schema])
    all_absences_add_grade_column(clean_schema)
    print('all_snapshots cleaned')

    #intervention
    build_clean_intervention_table.main([raw_schema,clean_schema])
    print('intervention built and cleaned')
    
    #additional tables for analysis
    build_graduates(raw_schema, clean_schema)
    build_student_tracking.main([raw_schema, clean_schema])
    
    # additional script for adding labels to tracking table
    build_cohort_tree_counts.main([clean_schema])
    print('tracking table plus outcome buckets built')
    
    # additional script for building intermediate tables for consecutive absences
    generate_consec_absence_intermediate_tables.main([clean_schema])
    print('consecutive absence tables built')
    
    # create index for all tables in clean schema for faster joining and searching
    create_index.main(['-s', clean_schema])
    print('indices created or checked for tables in schema `clean`')

if __name__ == "__main__":
    main()
