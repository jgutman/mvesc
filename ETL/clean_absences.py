import os, sys

pathname = os.path.dirname(sys.argv[0])
full_pathname = os.path.abspath(pathname)
split_pathname = full_pathname.split(sep="mvesc")
base_pathname = os.path.join(split_pathname[0], "mvesc")
parentdir = os.path.join(base_pathname, "ETL")
sys.path.insert(0,parentdir)

from mvesc_utility_functions import clean_column,\
    postgres_pgconnection_generator

def clean_absences(clean_schema):
    """
    Python wrapper for sql script 

    :param str clean_schema: name of the clean schema
    :rtype: None
    """
    with postgres_pgconnection_generator() as connection:
        with connection.cursor() as cursor:

            # absence length column very non-standardized b/w districts

            # Each row in this table corresponds to a single day absent.
            # Length of absence usually indicates 1 for a full day absent,
            # .5 for a partial day absent, and 0 if the student was not present
            # but it didn't "count against" the student.
            # However, for Zanesville records numbers >1 appear, which 
            # are an aggregate of all absences that "counted against" that
            # student, so it is the same value for all records for a given
            # student. Because of these discrepencies, using this column is 
            # not recommended. 

            # absence codes also non-standardized and seem to be 
            # overlapping, using absence_desc only to differentiate types
        
            # absence_desc column
            clean_column(cursor, os.path.join(base_pathname,'ETL',
                                              "json/absence_desc.json"),
                                              "absence_desc", "all_absences")

            # date column
            cursor.execute("""
            alter table {clean_schema}.all_absences
            alter column date type date using to_date(date, 'YYYY-MM-DD');
            update {clean_schema}.all_absences
            set date = case
                when extract(year from "date") < 100
                then ("date" + interval '2000 years')::date
                else "date"
            end;""".format(clean_schema=clean_schema))
        connection.commit()

def all_absences_generate_mm_day_wkd(clean_schema):
    """
    Python wrapper for sql script 

    :param str clean_schema: name of the clean schema
    :rtype: None
    """
    
    with postgres_pgconnection_generator() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
            alter table {s}.all_absences add column month int default null;
            update only {s}.all_absences set month=extract(month from date);

            alter table {s}.all_absences add column week int default null;
            update only {s}.all_absences set week = extract(week from date);
            
            alter table {s}.all_absences add column weekday int default null;
            update only {s}.all_absences set weekday = extract(dow from date);
            """.format(s=clean_schema))
        connection.commit()

def all_absences_add_grade_column(clean_schema):
    """
    Python wrapper for sql script 

    :param str clean_schema: name of the clean schema
    :rtype: None
    """
    
    with postgres_pgconnection_generator() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
            alter table {clean_schema}.all_absences 
            add column grade int default null;
            update only {clean_schema}.all_absences t1
            set grade =
            (select grade from {clean_schema}.all_snapshots t2
             where grade is not null and t1.student_lookup=t2.student_lookup 
             and (
                  (extract(year from t1.date)=t2.school_year and month>7)
                  or 
                  (extract(year from t1.date)=t2.school_year+1 and month<8)
                 )
                order by grade limit 1
            );""".format(clean_schema=clean_schema))
        connection.commit()
            
