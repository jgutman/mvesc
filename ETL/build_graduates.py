import os, sys

pathname = os.path.dirname(sys.argv[0])
full_pathname = os.path.abspath(pathname)
split_pathname = full_pathname.split(sep="mvesc")
base_pathname = os.path.join(split_pathname[0], "mvesc")
parentdir = os.path.join(base_pathname, "ETL")
sys.path.insert(0,parentdir)

from mvesc_utility_functions import clean_column,\
    postgres_pgconnection_generator

def build_graduates(raw_schema,clean_schema):
    """
    Python wrapper for sql script 

    :param str clean_schema: name of the clean schema
    :rtype: None
    """
    with postgres_pgconnection_generator() as connection:
        with connection.cursor() as cursor:
            
            # get all students with a non-null graduation date                             
            # if multiple conflicting non-null graduation dates, select date
            # from most recent school year snapshot record   
            cursor.execute("""
            drop table if exists {s}.all_graduates;
            create table {s}.all_graduates as (
              select student_lookup, graduation_date from (
                select student_lookup, max(school_year) as school_year
                  from {s}.all_snapshots where student_lookup in (
                    select distinct student_lookup from {s}.all_snapshots
                    where graduation_date is not null)
                  and graduation_date is not null
                  group by student_lookup)
                as latest_grade_with_graduation
                left join (
                select student_lookup, school_year, graduation_date 
                from {s}.all_snapshots where graduation_date is not null)
                as graduation_dates_valid
            using (student_lookup, school_year));
            """.format(s=clean_schema))
            
            # some students are not included here                                          
            # they don't have a graduation date in the snapshots table                     
            # but they do have one in the public."AllGradsTotal" table  
            cursor.execute("""
            insert into {s}.all_graduates(student_lookup, graduation_date)
            select "StudentLookup" student_lookup,
            to_date("HIGH_SCHOOL_GRAD_DATE", 'YYYYMMDD') graduation_date
            from {r}."AllGradsTotal" where "StudentLookup" not in
            (select student_lookup from {s}.all_graduates);
            """.format(r=raw_schema,s=clean_schema))

            # some students do not have graduation dates                                   
            # but their grade level in the snapshots is 12 or 23                           
            # and their withdrawal reason is 'graduate'                                    
            # and their district_withdraw_date is basically a graduation date  
            cursor.execute("""
            insert into {s}.all_graduates(student_lookup, graduation_date)
            select student_lookup,district_withdraw_date graduation_date
            from {s}.all_snapshots where 
              student_lookup not in (select student_lookup from {s}.all_graduates)
              and withdraw_reason = 'graduate'
              and (grade=12 or grade=23);""".format(s=clean_schema))
                           
        connection.commit()
