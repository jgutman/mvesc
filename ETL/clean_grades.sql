-- **** -- **** --
-- TERM field -- The fields are either finals, periods 1-4, or semesters
--		problems: there are some empty fields that are hard to understand
--			- '' empty string?
--			- '0' field?
alter table clean.all_grades add column clean_term varchar(20);
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
--		there are some oddities
--			- '' (empty). May need to be filled in based on snapshot data
--			- '**' asterisk.
--			- '22'. Guess a typo for grade 12?
--			- '23'. Guess a typo for grade 12?
--			- 'UG'. Only occurs for one StudentLookup 
--			- NULL. 
--		STATUS = wait on these odd cases 
--select distinct grade from clean.all_grades order by grade asc;
--select * from clean.all_grades where grade = '' limit 100;
--select * from clean.all_grades where grade = '**' limit 100;
--select * from clean.all_grades where grade = '22' limit 100;
--select * from clean.all_grades where grade = '23' limit 100;
--select * from clean.all_grades where grade = 'UG' limit 100;
--select * from clean.all_grades where grade is null limit 100;

-- 	Ignoring those oddities above for now.
--  Instead, we simply just remove the leading zeros from some values
update only clean.all_grades
set
	grade =
	case
	when grade = 'KG' then '0'
	else ltrim(grade, '0')
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
alter table clean.all_grades
	alter column year type int using cast(left(nullif(year, ''),
				strpos(nullif(year, ''), '-') - 1) as integer) ;
				
--		Missing? There are 99,455 records with a null year field, why?
--			We need to see what information we can fill in from other sources
--select year, count(*) from clean.all_grades group by year;
