from  mvesc_utility_functions import *


def clean_graduate_grade_level(current_year):
    grad_query = """
    create temporary table grade_temp as (select student_lookup, grade
    from clean.all_snapshots where school_year = {last});
    create temporary table joined_grades as (
    select current_year.student_lookup as student_lookup, max(last_year.grade::int) as last_grade
    from clean.all_snapshots as current_year
    left join grade_temp as last_year on last_year.student_lookup = current_year.student_lookup
    where (current_year.grade like 'GR')
        and current_year.school_year = {current}
    group by current_year.student_lookup
    );
    
    update clean.all_snapshots as s
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
    """.format_map({'last': current_year-1, 'current':current_year})
    #print(grad_query)
    return grad_query

def main():
    with postgres_pgconnection_generator() as connection:
        with connection.cursor() as cursor:
            for year in range(2007,2017):
                cursor.execute(clean_graduate_grade_level(year))
            cursor.execute("""
                 alter table clean.all_snapshots alter column grade 
                 type int using grade::int
                 """)
        connection.commit()

if __name__ == '__main__':
    main()
