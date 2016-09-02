""" Generate GPA
Procedures:
1. Read from tracking table to get student_lookups;
2. Generate `model.grades` from `clean.all_grades`
"""
from feature_utilities import *

def generate_gpa(clean_schema, model_schema, 
                 grade_range=range(3,12),replace=False):
    table =  "grades"
    with postgres_pgconnection_generator() as connection:
        with connection.cursor() as cursor:
            # creating base table (if not existing)
            create_feature_table(cursor, table, model_schema, replace=replace)
            
            # grabbing relevant grades
            cursor.execute("""
            create temp table grades as select * from 
            {c}.all_grades where
            student_lookup in
            (select student_lookup from {m}.outcome)
            and grade <= {max_yr} and grade >= {min_yr};
            """.format(max_yr=max(grade_range),min_yr=min(grade_range)),
                           c=clean_schema, m=model_schema)
            
            # selecting numeric grades
            cursor.execute("""
             create temp table numeric_grades as
             select * from grades where 
                 mark like '0%' or mark like '1%' or mark like '2%' or 
                 mark like '3%' or mark like '4%' or mark like '5%' or
                 mark like '6%' or mark like '7%' or mark like '8%' or 
                 mark like '9%';
             alter table numeric_grades alter column mark 
                 type float using mark::float;
             alter table numeric_grades alter column mark type float using
             case when  mark != 1 and mark != 0 and mark != 200 then mark end;
            """)
            
            # selecting letter grades
            cursor.execute("""
            create temp table letter_grades as
            select * from grades where 
                lower(mark) like 'a%' or  lower(mark) like 'b%' or  
                lower(mark) like 'c%' or  lower(mark) like 'd%' or  
                lower(mark) like 'f%';

            alter table letter_grades alter column mark 
                type text using lower(mark);
            delete from letter_grades where 
                mark like 'ap' or mark like 'fw' or mark like 'dw' or 
                mark like 'fa' or mark like 'blk';
            """)
            
            # standardizing numeric grades
            cursor.execute("""
            create temp table numeric_standard_grades as
            select student_lookup, course_code, course_name, grade, 
                school_year, district,clean_term, percent_of_year,
            case
                when mark < 60 then 0
                when mark < 63 then 0.7
                when mark < 67 then 1
                when mark < 70 then 1.3
                when mark < 73 then 1.7
                when mark < 77 then 2
                when mark < 80 then 2.3
                when mark < 83 then 2.7
                when mark < 87 then 3
                when mark < 90 then 3.3
                when mark < 94 then 3.7
                when mark < 100 then 4
            end as "mark"
            from numeric_grades;
            """)
            
            # standardizing letter grades
            cursor.execute("""
            create temp table letter_standard_grades as
            select student_lookup, course_code, course_name, grade, 
                school_year, district,clean_term, percent_of_year,
            case
                when mark like 'a' or mark like 'a+' then 4
                when mark like 'a-' then 3.7
                when mark like 'b+' then 3.3
                when mark like 'b' then 3
                when mark like 'b-' then 2.7
                when mark like 'c+' then 2.3
                when mark like 'c' then 2
                when mark like 'c-' then 1.7
                when mark like 'd+' then 1.3
                when mark like 'd' then 1
                when mark like 'd-' then 0.7
                when mark like 'f' then 0
            end as "mark"
            from letter_grades;
            """)
            
            # unioning standardized grades
            cursor.execute("""
            create temp table standard_grades as 
            select * from numeric_standard_grades 
            union all 
            select * from  letter_standard_grades;
            """)

            print('grades standardized')

            # function for custom ordering
            cursor.execute("""
            create or replace function idx(anyarray, anyelement)
            returns int as
            $$
            select i from (
            select generate_series(array_lower($1,1),array_upper($1,1))
            ) g(i)
            where $2 like $1[i]
            limit 1;
            $$ language SQL immutable;
            """)

            # selecting final grades and weighting by length
            cursor.execute("""
            create temp table avg_grades as
            select student_lookup, course_code, 
            case when sum(percent_of_year) = 0 then null 
                 else sum(mark*percent_of_year)/sum(percent_of_year) end 
                 as avg_mark, 
            sum(percent_of_year) as course_length
            from standard_grades
            group by student_lookup, course_code;
            
            drop table if exists {c}.final_grades;
            create table {c}.final_grades as 
            select distinct on (s.student_lookup, s.course_code) 
            s.student_lookup, s.course_code, s.course_name,  
            case when clean_term = 'final' then mark else avg_mark end       
            as final_mark,                          
            coalesce(nullif(course_length,0),1) as course_length,
            s.grade, s.district
            from standard_grades as s                               
            left join avg_grades  as a 
            on s.student_lookup = a.student_lookup               
            and s.course_code = a.course_code
            order by s.student_lookup, 
                s.course_code,idx(array['final'], clean_term);
            """.format(c=clean_schema))

            # district gpas
            cursor.execute("""
            create temp table district_mean as
            select district, sum(final_mark * course_length)/sum(course_length) 
                as district_gpa_mean
            from {c}.final_grades 
            group by district;

            create temp table district_grades as
            select m.district, m.district_gpa_mean, 
            n.district_gpa_std from district_mean as m left join (
            select
            sqrt(sum(course_length * (final_mark - district_gpa_mean)^2)
                 /(sum(course_length)-1)) as district_gpa_std, d.district
            from clean.final_grades as f
            left join district_mean as d
            on f.district = d.district
            group by d.district
            ) as n on n.district = m.district;
            """.format(c=clean_schema))

            cursor.execute( """
            create temp table district_zscores as 
            select student_lookup, grade, course_length,
                (final_mark - district_gpa_mean)/district_gpa_std 
                   as district_zscore
            from {c}.final_grades as f
            left join
            district_grades as d
            on f.district = d.district
            """.format(c=clean_schema))
            
            print('district stats calculated')

            # adding subjects to final grades table
            clean_column(cursor, 'class_subjects.json', 'course_name',
                         'final_grades', new_column_name = 'subject',
                         replace = 0, exact = 0)

            # yearly gpa
            gpa_query = """
            create temp table gpa as
            select student_lookup, """
            for grade in grade_range:
                gpa_query += """
                case
                when sum(case when grade = {grade} then course_length end) = 0 
                     then 0
                else sum(case when grade = {grade} then 
                              final_mark * course_length end)/
                              sum(case when grade = {grade} 
                     then course_length end)
                end as gpa_gr_{grade}, """.format(grade=grade)
            gpa_query = gpa_query[:-2] + """
                from {c}.final_grades
                group by student_lookup;
                """.format(c=clean_schema)
            cursor.execute(gpa_query)
            cursor.execute("""
            create index gpa_lookup_index on gpa(student_lookup)
            """)
            gpa_col_list = ["gpa_gr_{}".format(gr)
                           for gr in grade_range]

            print('gpa calculated')

            # district z-scores for gpa
            district_gpa_query = """
            create temp table district_gpa_zscores as
            select student_lookup, """
            for grade in grade_range:
                district_gpa_query += """
                case
                when sum(case when grade = {grade} then course_length end) = 0 
                     then 0
                else sum(case when grade = {grade} then 
                         district_zscore * course_length end)/
                     sum(case when grade = {grade} then course_length end)
                end as gpa_district_gr_{grade}, """.format(grade=grade)
            district_gpa_query = district_gpa_query[:-2] + """
                from district_zscores
                group by student_lookup;
                """
            cursor.execute(district_gpa_query)
            district_gpa_zscores_col_list = ['gpa_district_gr_{}'.format(g) 
                                             for g in grade_range]
            cursor.execute("""
            create index district_index on district_gpa_zscores(student_lookup)
            """)

            print('normalized gpa calculated')

            # getting pass/fail classes
            cursor.execute("""
            create temp table pass_fail as
            select student_lookup, grade, case 
            when lower(mark) like 'u%' or
                 lower(mark) like '0' 
            then 'f'
            when lower(mark) like 's%' or 
                 lower(mark) like 'p%' or
                 lower(mark) like 'o%' or
                 lower(mark) like '1' or
                 lower(mark) like '200'
            then 'p'
            end as mark
            from grades;
            delete from pass_fail where mark is null;
            """)
            
            # computing pass/fail features
            pf_feature_query = """
            create temp table pf_features as
            select student_lookup, """
            for grade in grade_range:
                pf_feature_query += """
                sum(case when grade = {gr} then 1 else 0 end) 
                as num_pf_classes_gr_{gr},
                sum(case when mark = 'p' and grade = {gr} then 1
                         when mark = 'f' and grade = {gr} then 0 end)
                    /sum(case when grade = {gr} then 1 else 0 end)::float 
                as percent_passed_pf_classes_gr_{gr}, """.format(gr=grade)
            pf_feature_query = pf_feature_query[:-2] + """
                from pass_fail
                group by student_lookup
                """;
            cursor.execute(pf_feature_query)
            cursor.execute("""
            create index pf_lookup_index on pf_features(student_lookup)
            """)

            pf_col_list = ["percent_passed_pf_classes_gr_{}".format(gr) 
                           for gr in grade_range]
            pf_col_list += ["num_pf_classes_gr_{}".format(gr)
                           for gr in grade_range]
            

            print('pass/fail classes calculated')

            # grouping by subject
            subject_list = ['language', 'stem','humanities','art','health',
                            'future_prep','interventions']
            subject_gpa_query = """
            create temp table subject_gpa_counts as
            select student_lookup, """
            for grade in grade_range:
                for i, subject in enumerate(subject_list):
                    subject_gpa_query += """ 
                    case
                    when sum(case when grade = {grade} and subject = %({i})s
                                  then course_length end) = 0 
                    then 0
                    else sum(case when grade = {grade} and subject = %({i})s
                    then final_mark * course_length end)/
                         sum(case when grade = {grade} and subject = %({i})s
                                  then course_length end)
                    end as {subject}_gpa_gr_{grade}, 
                    sum(case when grade = {grade} and subject = %({i})s
                             then 1 else 0 end) 
                        as num_{subject}_classes_gr_{grade}, """\
                        .format(grade=grade, subject=subject, i=i)
            subject_gpa_query = subject_gpa_query[:-2] + """
            from {c}.final_grades
            group by student_lookup;
            """.format(c=clean_schema)
            subject_dict = dict(zip([str(i) for i in range(len(subject_list))],
                                    subject_list))
            cursor.execute(subject_gpa_query, subject_dict)
            cursor.execute('select * from subject_gpa_counts limit 0')
            subject_gpa_counts_cols = [i[0] for i in cursor.description]
            subject_gpa_counts_cols.remove('student_lookup')
            cursor.execute(""" 
            create index subject_lookup_index on 
            subject_gpa_counts(student_lookup)
            """)


            print('subject gpa calculated')


            #cursor.execute("drop table clean.final_grades;")

            update_column_with_join(cursor,table, model_schema,
                                    column_list=subject_gpa_counts_cols,
                                    source_table='subject_gpa_counts')
            update_column_with_join(cursor,table, model_schema,
                                    column_list=gpa_col_list,
                                    source_table='gpa')
            update_column_with_join(cursor, table, model_schema,
                                    column_list=pf_col_list,
                                    source_table='pf_features')
            update_column_with_join(cursor, table,model_schema,
                                    column_list = district_gpa_zscores_col_list,
                                    source_table = 'district_gpa_zscores')
            print(' - All features added to grades table!')
                                        
        connection.commit()

def main(argv):
    clean_schema=argv[0]
    model_schema=argv[1]
    generate_gpa(clean_schema, model_schema,range(3,13),replace=True)

if __name__=='__main__':
    main()
