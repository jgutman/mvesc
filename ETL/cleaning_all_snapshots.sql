-- birth dates
--select min(birth_date), max(birth_date) from clean.all_snapshots;
	-- older than 21 in 2006
--select student_lookup, birth_date, grade, school_name, school_year from clean.all_snapshots where birth_date < cast('1986-04-11' as date);
	-- 17 questionable birth_dates
	-- 63878 is a 30 year old 1st grader at tri-valley high school?

-- cities
--select city, count(city) from clean.all_snapshots group by city order by city;
alter table clean.all_snapshots alter column city type text using lower(city);
alter table clean.all_snapshots alter column city type text using
case
when city like '%vile' then overlay(city placing 'ville' from (char_length(city)-3) for 5  )
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
end;

-- diplomas
--select diploma_type, count(diploma_type) from clean.all_snapshots group by diploma_type;
alter table clean.all_snapshots alter column diploma_type type text using
case
when diploma_type like '%Regular%' then 'regular'
when diploma_type like '*%' then 'none'
when diploma_type like '%Honors%' then 'honors'
end;

-- disability
--select disability_code, disability_desc from clean.all_snapshots group by disability_code, disability_desc order by disability_code, disability_desc;
--select disability_desc, count(disability_desc) from clean.all_snapshots group by disability_desc;
--select disability_code, count(disability_code) from clean.all_snapshots group by disability_code;
alter table clean.all_snapshots alter column disability_desc type text using
case
when lower(disability_desc) like '%multiple%' or disability_code like '01' then 'multiple'
when lower(disability_desc) like 'deaf%/blind' or disability_code like '02' then 'deaf/blind'
when lower(disability_desc) like '%deaf' or disability_code like '03' then 'deafness'
when lower(disability_desc) like '%visual%' or disability_code like '04' then 'visual impairment'
when lower(disability_desc) like '%speech%' or disability_code like '05' then 'speech and language impairment'
when lower(disability_desc) like '%orthopedic%' or disability_code like '06' then 'orthopedic impairment'
when lower(disability_desc) like '%emotional%' or disability_code like '08' then 'emotional disturbance'
when lower(disability_desc) like '%cognitive%' or disability_code like '09' then 'cognitive disability'
when lower(disability_desc) like '%learning%' or disability_code like '10' then 'learning disability'
when lower(disability_desc) like '%autism%' or disability_code like '12' then 'autism'
when lower(disability_desc) like '%brain injury%' or disability_code like '13' then 'traumatic brain injury'
when lower(disability_desc) like '%other%(major)%' or disability_code like '14' then 'other major'
when lower(disability_desc) like '%other%(minor)%' or disability_code like '15' then 'other minor'
when lower(disability_desc) like '%delay%' or disability_code like '16' then 'developmental delay'
when lower(disability_desc) like '**' or disability_code like '**' then 'none'
else lower(disability_desc) end;
alter table clean.all_snapshots rename column disability_desc to disability;
alter table clean.all_snapshots drop column disability_code;

-- disadvantagement
--select disadvantagement_code, disadvantagement_desc, count(*) from clean.all_snapshots group by disadvantagement_code, disadvantagement_desc order by disadvantagement_code, disadvantagement_desc;
alter table clean.all_snapshots alter column disadvantagement_desc type text using
case
when disadvantagement_code like '1' then 'economic'
when disadvantagement_code like '2' then 'academic'
when disadvantagement_code like '3' then 'both'
when disadvantagement_code like '*' then 'none'
else null end; -- tossing one 6 value
alter table clean.all_snapshots rename column disadvantagement_desc to disadvantagement;
alter table clean.all_snapshots drop column disadvantagement_code;

--select disadvantagement, count(*) from clean.all_snapshots group by  disadvantagement order by count(*)

-- discipline
--select discipline_incidents, count(discipline_incidents) from clean.all_snapshots group by discipline_incidents order by discipline_incidents;

-- district admission
--select date_part('year', district_admit_date) as d, count(*) from clean.all_snapshots group by d order by d;

-- district withdrawal
--select date_part('year', district_withdraw_date) as d, count(*) from clean.all_snapshots group by d order by d;
alter table clean.all_snapshots alter column district_withdraw_date type date using district_withdraw_date::date

-- ethnicity
--select ethnicity as d, count(*) from clean.all_snapshots group by d order by d;
UPDATE ONLY clean.all_snapshots
            SET ethnicity =
            case
            when trim(ethnicity)='*' then 'M' --'Multiracial'
            when trim(ethnicity)='1' then 'I' --'American Indian'
            when trim(ethnicity)='2' then 'A' --'Asian/Pacific Islander'
            when trim(ethnicity)='3' then 'B' --'Black'
            when trim(ethnicity)='4' then 'H' --'Hispanic'
            when trim(ethnicity)='5' then 'W' --'White'
            when trim(ethnicity)='6' then 'M' -- 'Multiracial'
            when trim(ethnicity)='7' then 'M' --'Other'
            when lower(trim(ethnicity))='i' then 'I' --'American Indian'
            when lower(trim(ethnicity))='a' then 'A' --'Asian/Pacific Islander'
            when lower(trim(ethnicity))='b' then 'B' --'Black'
            when lower(trim(ethnicity))='h' then 'H' --'Hispanic'
            when lower(trim(ethnicity))='w' then 'W' --'White'
            when lower(trim(ethnicity))='m' then 'M' --'Multiracial'
            when lower(trim(ethnicity))='p' then 'A' --'Asian/Pacific Islander'
            when lower(trim(ethnicity)) like '%american_ind%' then 'I' -- 'American Indian'
            when lower(trim(ethnicity)) like '%am_indian%' then 'I' -- 'American Indian'
            when lower(trim(ethnicity)) like '%hispanic%' then 'H' -- 'Hispanic'
            when lower(trim(ethnicity)) like '%indian%' then 'I' -- 'Hispanic'
            when lower(trim(ethnicity)) like '%alaskan%' then 'I' -- 'American Indian or Alaskan Native'
            when lower(trim(ethnicity)) like '%asian%' then 'A' -- 'Asian/Pacific Islander'
            when lower(trim(ethnicity)) like '%pacific%' then 'A' -- 'Asian/Pacific Islander'
            when lower(trim(ethnicity)) like '%black%' then 'B' -- 'Black'
            when lower(trim(ethnicity)) like '%african%' then 'B' -- 'Black'
            when lower(trim(ethnicity)) like '%multi%' then 'M' -- 'Multiracial'
            when lower(trim(ethnicity)) like '%white%' then 'W' -- 'White'
            else trim(ethnicity)
            end;

-- flags
--select coalesce(flag1,flag2) as d, count(*) from clean.all_snapshots group by d order by d;

alter table clean.all_snapshots alter column flag1 type text using coalesce(flag1,flag2);
alter table clean.all_snapshots rename column flag1 to lunch;
alter table clean.all_snapshots drop column flag2;
alter table clean.all_snapshots alter column lunch type text using
case
when lower(lunch) like 'f' or lower(lunch) like 'r' then 'economic'
else null end; -- tossing a few (~50) miscelanous values

alter table clean.all_snapshots alter column disadvantagement type text using
coalesce(disadvantagement, lunch);
alter table clean.all_snapshots drop column lunch;

-- gender
--select gender as d, count(*) from clean.all_snapshots group by d order by d;
update clean.all_snapshots set gender=upper(left(trim(gender), 1));
-- set students with multiple conflicting ethnicity as multiracial
update snapshots set ethnicity='M' where student_lookup in
  (select student_lookup from snapshots
    group by student_lookup
    having count(distinct ethnicity) > 1);

-- gifted
--select gifted as d, count(*) from clean.all_snapshots group by d order by d;

-- grades
--select distinct grade from clean.all_snapshots order by grade;
--select count(student_lookup), school_year from clean.all_snapshots where grade = 'GR' group by school_year ;
--select count(*) from clean.wrk_tracking_students where "2015" = 'GR';
--select count(*) from clean.wrk_tracking_students where "2014" = 'GR'; -- 153
--select count(*) from clean.wrk_tracking_students where "2013" = 'GR';
--select count(*) from clean.wrk_tracking_students where "2012" = 'GR';
--select count(*) from clean.wrk_tracking_students where "2011" = 'GR';
--select count(*) from clean.wrk_tracking_students where "2010" = 'GR';
--select count(*) from clean.wrk_tracking_students where "2009" = 'GR';
--select count(*) from clean.wrk_tracking_students where "2008" = 'GR';
--select count(*) from clean.wrk_tracking_students where "2007" = 'GR';
--select count(*) from clean.wrk_tracking_students where "2006" = 'GR'; -- 524

-- dealing with graduate 'GR' codes using function in clean_and_consolidate
-- dealing with other codes
update clean.all_snapshots set grade =
	case when grade like '**' then null
		 when grade like '13' or grade like '14' then '23'
		 when grade like 'PS%' or grade like '-2' then '-1'
		 when grade like 'KG' then '0'
		 when grade like 'IN' or grade like 'DR' then null -- inactive students
		 when grade like 'GR' and school_year = 2006 then '12 '-- don't know what grade they were in before, but don't care about people graduating in 2006
		 when grade like 'UG' then null -- means ungraded
		 else grade
	end;


alter table clean.all_snapshots alter column grade type text using nullif(grade, '**');

-- graduation date
--select date_part('year', graduation_date) as d, count(distinct "StudentLookup") from clean.all_snapshots group by d order by d;

-- iss
--select iss as d, count(*) from clean.all_snapshots group by d order by d;

-- limited english
--select limited_english as d, count(*) from clean.all_snapshots group by d order by d;

-- oss
--select oss as d, count(*) from clean.all_snapshots group by d order by d;

-- school
--select school_code, lower(school_name), count(*) from clean.all_snapshots group by school_code, school_name order by school_code, school_name;
	-- names not very consistent, just use code?

-- section 504
--select section_504_plan as d, count(*) from clean.all_snapshots group by d order by d;

-- IRNs
--select coalesce(sent_to_1_irn, sent_to_2_irn, withdrawn_to_irn) as d, count(*) from clean.all_snapshots group by d order by d;
alter table clean.all_snapshots alter column withdrawn_to_irn type text using
coalesce(sent_to_1_irn, sent_to_2_irn, withdrawn_to_irn);
alter table clean.all_snapshots alter column withdrawn_to_irn type text using
nullif(withdrawn_to_irn, '******');
alter table clean.all_snapshots drop column sent_to_1_irn;
alter table clean.all_snapshots drop column sent_to_2_irn;

-- special_ed
--select cast(special_ed as int) as d, count(*) from clean.all_snapshots group by d order by d;

-- state
--select state as d, count(*) from clean.all_snapshots group by d order by d;

-- status
--select status_code, lower(status_desc), count(*) from clean.all_snapshots group by status_code, status_desc order by count(*) desc;

--select status as d, count(*) from clean.all_snapshots group by d order by d;
-- cleaned using a json file in cleaning_student_status.py


-- withdrawal codes
--select distinct withdraw_reason from clean.all_snapshots;
alter table clean.all_snapshots alter column withdraw_reason type text using
case
when withdraw_reason like '36' or withdraw_reason like '16' then 'withdrew - PS' -- the 16 is a typo correction for one student
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
when withdraw_reason like '75' then 'dropout - did not finish tests'
when withdraw_reason like '76' then 'dropout - attendance'
when withdraw_reason like '77' then 'dropout - online did not finish tests'
when withdraw_reason like '79' then 'withdrew - district eligibility'
when withdraw_reason like '81' then 'error'
when withdraw_reason like '99' then 'graduate'
when withdraw_reason like '**' then 'did not withdraw'
else withdraw_reason
end;
