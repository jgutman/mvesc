-- first, clean the term field --
select distinct term from clean.all_grades order by term asc;
-- 		build the case statement using the output
select distinct clean_term, count(clean_term)
from
(select term,
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
	end
	as "clean_term"
	from clean.all_grades
) as zzq1 group by clean_term;

-- next, clean the grade field --

-- check year field for issues? --
select distinct year from clean.all_grades;
-- convert years like 2007-08 to 2007
alter table clean.all_grades
	alter column year type int using cast(left(nullif(year, ''),
				strpos(nullif(year, ''), '-') - 1) as integer) ;
--		we have some 99,455 records with a null year field, why?
select year, count(*) from clean.all_grades group by year;
