import os, sys

pathname = os.path.dirname(sys.argv[0])
full_pathname = os.path.abspath(pathname)
split_pathname = full_pathname.split(sep="mvesc")
base_pathname = os.path.join(split_pathname[0], "mvesc")
parentdir = os.path.join(base_pathname, "ETL")
sys.path.insert(0,parentdir)

from  mvesc_utility_functions import *



def clean_graduate_grade_level(current_year,clean_schema):
    grad_query = """
    create temporary table grade_temp as (select student_lookup, grade
    from {s}.all_snapshots where school_year = {last});
    create temporary table joined_grades as (
    select current_year.student_lookup as student_lookup, max(last_year.grade::int) as last_grade
    from {s}.all_snapshots as current_year
    left join grade_temp as last_year on last_year.student_lookup = current_year.student_lookup
    where (current_year.grade like 'GR')
        and current_year.school_year = {current}
    group by current_year.student_lookup
    );
    
    update {s}.all_snapshots as s
    set grade = case
        when j.last_grade = 11 then '12'
        when j.last_grade > 11 then '23'
        when j.last_grade is null then '12'
        else j.last_grade::text
        end 
    from joined_grades as j
    where j.student_lookup = s.student_lookup
    and s.school_year = {current};
    
    drop table grade_temp;
    drop table joined_grades;
    """.format_map({'last': current_year-1, 'current':current_year, 's':clean_schema})
    return grad_query

def main(argv):

    clean_schema = argv[0]

    with postgres_pgconnection_generator() as connection:
        with connection.cursor() as cursor:
            for year in range(2007,2017):
                cursor.execute(clean_graduate_grade_level(year,clean_schema))
            cursor.execute("""
            alter table {s}.all_snapshots alter column grade 
            type int using grade::int
            """.format(s=clean_schema))
        connection.commit()

if __name__ == '__main__':
    main()
