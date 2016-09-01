import os, sys

pathname = os.path.dirname(sys.argv[0])
full_pathname = os.path.abspath(pathname)
split_pathname = full_pathname.split(sep="mvesc")
base_pathname = os.path.join(split_pathname[0], "mvesc")
parentdir = os.path.join(base_pathname, "ETL")
sys.path.insert(0,parentdir)

from mvesc_utility_functions import clean_column,\
    postgres_pgconnection_generator
import cleaning_grad_grades
import clean_addresses

def add_missing_grads(cursor, raw_schema, clean_schema):
    cursor.execute("""
    update {s}.all_snapshots t1
    set graduation_date=(
    select to_date(t2."GraduationDate", 'MM/DD/YYYY') as grad_date from
    {r}."Districts1516MissingGraddates" t2
    where t2."StudentLookup"=t1.student_lookup
    order by grad_date desc limit 1
    ) where exists (
    select * from {r}."Districts1516MissingGraddates" t2
    where t2."StudentLookup"=t1.student_lookup
    );""".format(r=raw_schema,s=clean_schema))

def clean_snapshots(raw_schema, clean_schema):
    with postgres_pgconnection_generator() as connection:
        with connection.cursor() as cursor:

            # cities
            # this is not comprehensive, but catches some of the common
            # misspellings 
            cursor.execute("""
            alter table {s}.all_snapshots alter column city type text 
            using lower(city);
            alter table {s}.all_snapshots alter column city type text using
            case
              when city like '%vile' then overlay(city placing 'ville' from 
                (char_length(city)-3) for 5)
              when city like 'cosh%' then 'coshocton'
              when city like 'cosh%' then 'coshocton'
              when city like 'duncan falls' then 'duncan falls'
              when city like '%fult%' then 'east fultonham'
              when city like '%fraze%' then 'frazeyburg'
              when city like '%frenso%' then 'fresno'
              when city like 'hopewell%' then 'hopewell'
              when city like '%perry' then 'mount perry'
              when city like 'new lex%' then 'new lexington'
              when city like '%s%zan%' then 'south zanesville'
              when city like 'zan%' then 'zanesville'
              when city like 'west laf%' then 'west lafayette'
              else city
            end;""".format(s=clean_schema))
            
            # diplomas
            cursor.execute("""
            alter table {s}.all_snapshots alter column diploma_type 
            type text using
            case
            when diploma_type like '%Regular%' then 'regular'
            when diploma_type like '*%' then 'none'
            when diploma_type like '%Honors%' then 'honors'
            end;""".format(s=clean_schema))

            # disability
            # 1-1 mapping determined between description and code
            cursor.execute("""
            alter table {s}.all_snapshots alter column disability_desc 
            type text using
            case
            when lower(disability_desc) like '%multiple%' 
              or disability_code like '01' then 'multiple'
            when lower(disability_desc) like 'deaf%/blind' 
              or disability_code like '02' then 'deaf/blind'
            when lower(disability_desc) like '%deaf' or disability_code 
              like '03' then 'deafness'
            when lower(disability_desc) like '%visual%' 
              or disability_code like '04' then 'visual impairment'
            when lower(disability_desc) like '%speech%' or disability_code 
              like '05' then 'speech and language impairment'
            when lower(disability_desc) like '%orthopedic%' or 
              disability_code like '06' then 'orthopedic impairment'
            when lower(disability_desc) like '%emotional%' or disability_code 
              like '08' then 'emotional disturbance'
            when lower(disability_desc) like '%cognitive%' or disability_code 
              like '09' then 'cognitive disability'
            when lower(disability_desc) like '%learning%' or disability_code 
              like '10' then 'learning disability'
            when lower(disability_desc) like '%autism%' or disability_code 
              like '12' then 'autism'
            when lower(disability_desc) like '%brain injury%' or 
              disability_code like '13' then 'traumatic brain injury'
            when lower(disability_desc) like '%other%(major)%' or 
              disability_code like '14' then 'other major'
            when lower(disability_desc) like '%other%(minor)%' or 
              disability_code like '15' then 'other minor'
            when lower(disability_desc) like '%delay%' or disability_code 
              like '16' then 'developmental delay'
            when lower(disability_desc) like '**' or disability_code 
              like '**' then 'none'
            else lower(disability_desc) 
            end;
            
            alter table {s}.all_snapshots rename column 
              disability_desc to disability;
            alter table {s}.all_snapshots drop column disability_code;
            """.format(s=clean_schema))

            # section 504 plan
            cursor.execute("""
            alter table {s}.all_snapshots alter column section_504_plan
            type text using case 
              when section_504_plan = 'N' then '0'
              when section_504_plan = 'Y' then '1'
              else section_504_plan 
            end;
            alter table {s}.all_snapshots alter column section_504_plan 
            type int using section_504_plan::int;
            """.format(s=clean_schema))

            # disadvantagement
            # information in disadvantagement, flag1, and flag2
            cursor.execute("""
            alter table {s}.all_snapshots alter column 
            disadvantagement_desc type text using
            case
            when disadvantagement_code like '1' then 'economic'
            when disadvantagement_code like '2' then 'academic'
            when disadvantagement_code like '3' then 'both'
            when disadvantagement_code like '*' then 'none'
            else null end; -- tossing one 6 value
            alter table {s}.all_snapshots rename column 
            disadvantagement_desc to disadvantagement;
            alter table {s}.all_snapshots drop column disadvantagement_code;
            
            alter table {s}.all_snapshots alter column flag1 type text 
            using coalesce(flag1,flag2);
            alter table {s}.all_snapshots rename column flag1 to lunch;
            alter table {s}.all_snapshots drop column flag2;
            alter table {s}.all_snapshots alter column lunch type text using
            case
            when lower(lunch) like 'f' or lower(lunch) like 'r' then 'economic'
            else null end; -- tossing a few (~50) miscelanous values                       
            alter table {s}.all_snapshots alter column disadvantagement 
            type text using coalesce(disadvantagement, lunch);
            alter table {s}.all_snapshots drop column lunch;
            """.format(s=clean_schema))

            # gender
            cursor.execute("""
            update {s}.all_snapshots set gender=upper(left(trim(gender), 1));
            """.format(s=clean_schema))

            # district withdrawal
            cursor.execute("""
            alter table {s}.all_snapshots alter column 
            district_withdraw_date type date using 
            district_withdraw_date::date;
            """.format(s=clean_schema))
            
            #ethnicity
            clean_column(cursor, os.path.join(base_pathname,'ETL',
                                              'json/ethnicity.json'),
                         "ethnicity", "all_snapshots")
            # set conflicting ethnicities to multiracial
            cursor.execute("""
            update {s}.all_snapshots set ethnicity='M' where student_lookup 
            in
            (select student_lookup from {s}.all_snapshots
            group by student_lookup
            having count(distinct ethnicity) > 1);
            """.format(s=clean_schema))

            # grade level
            # 'GR' codes dealt with in clean_and_consolidate
            cursor.execute("""
            update {s}.all_snapshots set grade =
            case when grade like '**' then null
            when grade like '13' or grade like '14' then '23'
            when grade like 'PS%' or grade like '-2' then '-1'
            when grade like 'KG' then '0'
            when grade like 'IN' or grade like 'DR' then null 
            when grade like 'GR' and school_year = 2006 then '12 '
            -- don't know what grade they were in before, but don't 
            -- care about people graduating in 2006                            
            when grade like 'UG' then null -- means ungraded 
            else grade
            end;
            alter table {s}.all_snapshots alter column grade type text 
              using nullif(grade, '**');
            """.format(s=clean_schema))

            # IRNs
            # from withdrawn_to_irn, sent_to_1_irn, and sent_to_2_irn
            cursor.execute("""
            alter table {s}.all_snapshots alter column withdrawn_to_irn 
            type text using
            coalesce(sent_to_1_irn, sent_to_2_irn, withdrawn_to_irn);
            alter table {s}.all_snapshots alter column withdrawn_to_irn 
            type text using
            nullif(withdrawn_to_irn, '******');
            alter table {s}.all_snapshots drop column sent_to_1_irn;
            alter table {s}.all_snapshots drop column sent_to_2_irn;
            """.format(s=clean_schema))

            # withdrawal codes
            cursor.execute("""
            alter table {s}.all_snapshots alter column withdraw_reason 
            type text using
            case
            when withdraw_reason like '36' or withdraw_reason like '16' 
            then 'withdrew - PS' -- the 16 is a typo correction for one student
            when withdraw_reason like '37' then 'withdrew - KG'
            when withdraw_reason like '39' then 'withdrew - must leave IRN'
            when withdraw_reason like '40' then 'transferred - out of state'
            when withdraw_reason like '41' then 'transferred - in state'
            when withdraw_reason like '42' then 'transferred - private'
            when withdraw_reason like '43' then 'transferred - homeschool'
            when withdraw_reason like '45' then 'transferred - court ordered'
            when withdraw_reason like '46' then 'transferred - out of country'
            when withdraw_reason like '47' then 'withdrew - amish'
            when withdraw_reason like '48' then 'expelled'
            when withdraw_reason like '51' then 'withdrew - illness'
            when withdraw_reason like '52' then 'withdrew - death'
            when withdraw_reason like '71' then 'dropout - attendance'
            when withdraw_reason like '72' then 'dropout - employment'
            when withdraw_reason like '73' then 'dropout - over 18'
            when withdraw_reason like '74' then 'dropout - moved'
            when withdraw_reason like '75' 
              then 'dropout - did not finish tests'
            when withdraw_reason like '76' then 'dropout - attendance'
            when withdraw_reason like '77' 
              then 'dropout - online did not finish tests'
            when withdraw_reason like '79' 
              then 'withdrew - district eligibility'
            when withdraw_reason like '81' then 'error'
            when withdraw_reason like '99' then 'graduate'
            when withdraw_reason like '**' then 'did not withdraw'
            else withdraw_reason
            end;""".format(s=clean_schema))

            # student status
            clean_column(cursor, values=os.path.join(
                base_pathname,'ETL',"json/student_status.json"),
                         old_column_name="status_code",
                         table_name="all_snapshots", replace=1,
                         exact=0)
            clean_column(cursor, values=os.path.join(
                base_pathname,'ETL',"json/student_status.json"),
                         old_column_name="status_desc",
                         table_name="all_snapshots", replace=1,
                         exact=0)
            cursor.execute("""
            alter table {s}.all_snapshots add column status text;
            alter table {s}.all_snapshots alter column status type
            text using coalesce(status_code, status_desc);
            alter table {s}.all_snapshots drop column status_code;
            alter table {s}.all_snapshots drop column status_desc;
            """.format(s=clean_schema))
            
            add_missing_grads(cursor, raw_schema, clean_schema)

        connection.commit()

    cleaning_grad_grades.main([clean_schema])
    clean_addresses.main([clean_schema])
