-- **** -- **** --
-- TERM field -- The fields are either finals, periods 1-4, or semesters
--		problems: there are some empty fields that are hard to understand
--			- '' empty string?
--			- '0' field?
alter table clean.all_grades add column clean_term text;
update only clean.all_grades
set
	clean_term =
	case replace(replace(replace(replace(trim(trailing ' ' from Lower(term)), '9', 'nine'),
			'weeks', 'week'), 'perod', 'period'), '4tn', '4th')
	when '' then 'empty'
	when '0' then 'zero'
	-- assume that nine weeks == periods == quarters
	when '1st nine week' then 'period_1'
	when '2nd nine week' then 'period_2'
	when '2nd  nine week' then 'period_2' -- manual typo adjustment
	when '3rd nine week' then 'period_3'
	when '4th nine week' then 'period_4'
	when '1st semester' then 'sem_1'
	when '2nd semester' then 'sem_2'
	when '4th' then 'period_4' -- assumption
	when 'all year courses' then 'all_year_course'
	when 'final' then 'all_year_course' -- assumption
	when 'final year end' then 'all_year_course'
	when 'full year' then 'all_year_course'
	when 'grading period' then 'period'
	when 'grading period 1' then 'period_1'
	when 'grading period 2' then 'period_2'
	when 'grading period 3' then 'period_3'
	when 'grading period 4' then 'period_4'
	when 'quarter 1' then 'period_1'
	when 'quarter 2' then 'period_2'
	when 'quarter 3' then 'period_3'
	when 'quarter 4' then 'period_4'
	when 'semester 1' then 'sem_1'
	when 'semester 2' then 'sem_2'
	when 'year' then 'all_year_course'
	else 'CANNOT FIND CHECK VALUES'
	end;

--select distinct clean_term, count(clean_term) from clean.all_grades group by clean_term;

-- **** -- **** --
-- GRADE field -- marking what grade the student is in

alter table clean.all_grades alter column grade type int using
      case when grade like '**' then null
      when grade like '13' or grade like '14' then 23
      when grade like 'PS%' or grade like '-2%' then -1
      when grade like 'KG' then 0
      when grade like 'IN' or grade like 'DR' then null -- inactive students
      else grade::int
      end;

-- output distinct values to assess
--select distinct grade, count(grade)
--from clean.all_grades group by grade order by grade;

-- **** -- **** --
-- COURSE_NAME & COURSE_CODE -- Lots of variety here
--		Not a necessary priority currently; can wait until more focused feature creation?
--		Zhe: I think we just need to parse the course_name, the course_code is too difficult
--select distinct course_name from clean.all_grades order by course_name asc limit 150;
--select distinct course_code from clean.all_grades limit 150;

--select course_name,
--	case
--	when course_name ~* '*bio*' then 'bio'
--	when course_name ~* '*chem*' then 'chem'
--	when course_name ~* '*math*' then 'math'
--	when course_name ~* '*engl*' then 'english'
--	when course_name ~* '*chem*' then 'chem'
--	when course_name ~* '*art*' then 'art'
--	when course_name ~* '*music*' then 'music'
--	when course_name ~* '*social studies*' then 'social_studies'
--	when course_name ~* '*writing*' then 'writing'
--	when course_name ~* '*science*' then 'science'
--	when course_name ~* '*%phys ed*' then 'gym'
--	when course_name ~* '*history*' then 'gym'
--	else course_name
--	end
--	as "new_course_name"
--	from clean.all_grades where district = 'Coshocton'
--	limit 500;

-- **** -- **** --
-- MARK field --
--		If no numbers, treat as a big case statement?
--select mark, district, count(mark) from clean.all_grades where mark ~ '^[^0-9]*$' group by mark, district order by count desc;
-- 		If contains only numbers or dots, do a different operation?
--select * from clean.all_grades where mark ~ '^[0-9]*$' limit 100;
-- 		Zhe: finish the exploration in R

-- **** -- **** --
-- YEAR field -- Jackie updated to make the years into a single integer value
-- 		Convert years like 2007-08 to 2007
--alter table clean.all_grades
--	alter column school_year type int using cast(left(nullif(school_year, ''),
--				strpos(nullif(school_year, ''), '-') - 1) as integer) ;

--		Missing? There are 99,455 records with a null year field, why?
--			We need to see what information we can fill in from other sources
--select year, count(*) from clean.all_grades group by year;

alter table clean.all_grades alter column school_year type int using
substring(school_year,1,4)::int;

-- **** -- **** --
-- DISTRICT field --
-- select distinct district from clean.all_grades;
alter table clean.all_grades alter column district type text using
case when district like 'Maysville%' then 'Maysville'
     when district like 'Ridgewood%' then 'Ridgewood'
     when district like 'Franklin%' then 'Franklin'
     else district
     end;
