-- most common withdrawal reasons for all students in snapshots file
select withdraw_reason, count(withdraw_reason) from clean.all_snapshots
	group by withdraw_reason
	order by count(withdraw_reason) desc;

-- start with the number of students in 4th grade in 2006, show how many progress to the next grade level each year
-- how many are left of the original cohort by 12th grade?
	(select '04' AS grade, 2006 as school_year, count(*) from (select distinct(student_lookup) from clean.wrk_tracking_students
		where "2006" = '04') as grade_4_in_2006)
union
	(select '05' AS grade, 2007 as school_year, count(*) from (select distinct(student_lookup) from clean.wrk_tracking_students
		where "2006" = '04') as grade_4_in_2006
	where student_lookup in (select distinct(student_lookup) from clean.wrk_tracking_students
		where "2007" = '05'))
union
	(select '06' AS grade, 2008 as school_year, count(*) from (select distinct(student_lookup) from clean.wrk_tracking_students
		where "2006" = '04') as grade_4_in_2006
	where student_lookup in (select distinct(student_lookup) from clean.wrk_tracking_students
		where "2008" = '06'))
union
	(select '07' AS grade, 2009 as school_year, count(*) from (select distinct(student_lookup) from clean.wrk_tracking_students
		where "2006" = '04') as grade_4_in_2006
	where student_lookup in (select distinct(student_lookup) from clean.wrk_tracking_students
		where "2009" = '07'))
union
	(select '08' AS grade, 2010 as school_year, count(*) from (select distinct(student_lookup) from clean.wrk_tracking_students
		where "2006" = '04') as grade_4_in_2006
	where student_lookup in (select distinct(student_lookup) from clean.wrk_tracking_students
		where "2010" = '08'))
union
	(select '09' AS grade, 2011 as school_year, count(*) from (select distinct(student_lookup) from clean.wrk_tracking_students
		where "2006" = '04') as grade_4_in_2006
	where student_lookup in (select distinct(student_lookup) from clean.wrk_tracking_students
		where "2011" = '09'))
union
	(select '10' AS grade, 2012 as school_year, count(*) from (select distinct(student_lookup) from clean.wrk_tracking_students
		where "2006" = '04') as grade_4_in_2006
	where student_lookup in (select distinct(student_lookup) from clean.wrk_tracking_students
		where "2012" = '10'))
union
	(select '11' AS grade, 2013 as school_year, count(*) from (select distinct(student_lookup) from clean.wrk_tracking_students
		where "2006" = '04') as grade_4_in_2006
	where student_lookup in (select distinct(student_lookup) from clean.wrk_tracking_students
		where "2013" = '11'))
union
	(select '12' AS grade, 2014 as school_year, count(*) from (select distinct(student_lookup) from clean.wrk_tracking_students
		where "2006" = '04') as grade_4_in_2006
	where student_lookup in (select distinct(student_lookup) from clean.wrk_tracking_students
		where "2014" = '12'))
order by school_year;

drop table clean.all_graduates;
-- get all students with a non-null graduation date
-- if multiple conflicting non-null graduation dates, select date from most recent school year snapshot record
create table clean.all_graduates as
(select student_lookup, graduation_date from
	(select student_lookup, max(school_year) as school_year from clean.all_snapshots
		where student_lookup in
			(select distinct student_lookup from clean.all_snapshots where graduation_date is not null)
		and graduation_date is not null
	group by student_lookup) as latest_grade_with_graduation
left join
	(select student_lookup, school_year, graduation_date from clean.all_snapshots
		where graduation_date is not null) as graduation_dates_valid
using (student_lookup, school_year)) ;

-- 9,222 graduates in both sets
select count(student_lookup) from clean.all_graduates;
select count(distinct student_lookup) from clean.all_snapshots
	where graduation_date is not null;

----------------

	select count(distinct(student_lookup)) from clean.wrk_tracking_students where
		"2010" = '09';
	select count(distinct(student_lookup)) from clean.wrk_tracking_students where
		"2010" = '09' and student_lookup in (select student_lookup from clean.all_graduates);
	select count(distinct(student_lookup)) from clean.wrk_tracking_students where
		"2010" = '09' and student_lookup in (select student_lookup from clean.all_graduates
			where graduation_date <= '2014-09-01');
	select count(distinct(student_lookup)) from clean.wrk_tracking_students where
		"2010" = '09' and student_lookup in (select student_lookup from clean.all_graduates
			where graduation_date <= '2015-09-01' and graduation_date > '2014-09-01');
	select count(distinct(student_lookup)) from clean.wrk_tracking_students where
		"2010" = '09' and student_lookup in (select student_lookup from clean.all_graduates
			where graduation_date > '2015-09-01');

	select count(distinct(student_lookup)) from clean.wrk_tracking_students where
		"2010" = '09' and student_lookup not in (select student_lookup from clean.all_graduates);
	select count(distinct(student_lookup)) from clean.wrk_tracking_students where
		"2010" = '09' and student_lookup not in (select student_lookup from clean.all_graduates)
		and withdraw_reason is not null;

	select count(distinct(student_lookup)) from clean.wrk_tracking_students where
		"2010" = '09' and student_lookup not in (select student_lookup from clean.all_graduates)
		and withdraw_reason like 'dropout%';

	select count(distinct student_lookup) from clean.wrk_tracking_students where
		"2010" = '09' and student_lookup not in (select student_lookup from clean.all_graduates)
		and withdraw_reason like 'transfer%' and withdrawn_to_irn::int in
			(select building_irn from public."IRN_DORP_GRAD_RATE1415");

	select * from clean.all_snapshots where withdrawn_to_irn = '149328'; -- foxfire high school

	select distinct(withdrawn_to_irn::int) from clean.all_snapshots
	where withdrawn_to_irn::int in
		(select distinct(district_irn) from public."IRN_DORP_GRAD_RATE1415" order by district_irn)
		order by withdrawn_to_irn ;

	select district, count(district) from clean.all_snapshots
		where school_year = 2010 and grade = '09'
		group by district;

	select distinct(withdrawn_to_irn::int) from clean.all_snapshots order by withdrawn_to_irn ;

	select student_lookup, withdraw_reason, withdrawn_to_irn, district_withdraw_date
		from clean.wrk_tracking_students where student_lookup in
	(select student_lookup from clean.wrk_tracking_students where
		"2010" = '09' and student_lookup not in (select student_lookup from clean.all_graduates)
		and withdraw_reason like 'transfer%'
		group by student_lookup having count(student_lookup) > 1);


	select * from clean.wrk_tracking_students where
		"2010" = '09' and student_lookup not in (select student_lookup from clean.all_graduates)
		and withdraw_reason like 'expelled%';

	select * from clean.all_snapshots where student_lookup = 51354 order by school_year;
	select student_lookup, withdraw_reason from clean.wrk_tracking_students where withdraw_reason like 'dropout%';

	select student_lookup, grade, school_year, withdraw_reason, district, district_withdraw_date, graduation_date from
		clean.all_snapshots where student_lookup in
		(select distinct(student_lookup) from clean.wrk_tracking_students where
		"2010" = '09' and student_lookup not in (select student_lookup from clean.all_graduates))
		and (withdraw_reason = 'did not withdraw' or withdraw_reason is null)
		order by student_lookup, grade desc;

select * from clean.all_snapshots where student_lookup = 50215 order by school_year;


select * from clean.all_graduates where graduation_date <= '2014-09-01' order by graduation_date desc;
select withdraw_reason, count(withdraw_reason) from clean.wrk_tracking_students
	group by withdraw_reason order by count(withdraw_reason) desc;
select count(*) from clean.wrk_tracking_students where withdraw_reason is null;





-- total of 39 students who do not move from grade 4 to grade 5
select count(distinct student_lookup) from clean.all_snapshots where
	student_lookup in
	(select student_lookup from (select distinct(student_lookup) from clean.wrk_tracking_students
		where "2006" = '04') as grade_4_in_2006
	where student_lookup not in (select distinct(student_lookup) from clean.wrk_tracking_students
		where "2007" = '05'));

-- look at students in grade 4 in 2006 who are not in grade 12 in 2014
select student_lookup, birth_date, school_year, withdraw_reason, grade,
	district_admit_date, district_withdraw_date, graduation_date from clean.all_snapshots where
	student_lookup in
	(select student_lookup from (select distinct(student_lookup) from clean.wrk_tracking_students
		where "2006" = '04') as grade_4_in_2006
	where student_lookup not in (select distinct(student_lookup) from clean.wrk_tracking_students
		where "2014" = '12'))
	order by student_lookup, school_year;

-- what happens to the students who leave in early grades? they seem to just not show up anymore
-- typically will have district_withdraw_date but null withdraw_reason


select student_lookup, school_year, grade, graduation_date, birth_date,
	district_admit_date, district_withdraw_date, withdraw_reason, withdrawn_to_irn
	from clean.all_snapshots where student_lookup = 48 order by school_year;

-- some possible categories of student outcomes for tracking:
-- withdrew from school district, district_withdraw_date in between school years, no withdraw_reason
-- transferred to JVS, completed senior year, did not graduate

select count(student_lookup) from
	from clean.all_snapshots where student_lookup in
	(select student_lookup from (select distinct(student_lookup) from clean.all_snapshots
		where ))


select extract(year from graduation_date) as grad_year, count(*)
	from clean.all_snapshots where
	student_lookup in
	(select distinct student_lookup from clean.all_snapshots
		where grade = '09' and school_year = 2010)
	group by grad_year
	order by grad_year;


-- look at students in grade 10 in 2011-2012 who are not in grade 12 in 2013-2014
select student_lookup, birth_date, school_year, grade, withdraw_reason, withdrawn_to_irn,
	district_admit_date, district_withdraw_date, graduation_date from clean.all_snapshots where
	student_lookup in
	(select student_lookup from (select distinct(student_lookup) from clean.wrk_tracking_students
		where "2011" = '10') as grade_10_in_2011
	where student_lookup not in (select distinct(student_lookup) from clean.wrk_tracking_students
		where "2013" = '12' or "2013" = 'GR'))
	order by student_lookup, school_year;

select student_lookup, grade, school_year, district, graduation_date, district_admit_date, district_withdraw_date
	from clean.all_snapshots where student_lookup = 34388 order by school_year, district_admit_date;

-- add graduation date column to tracking students table

-- get numbers on 12th graders how many are recorded how many go to 11 to graduation date or 11 to 23
select count(distinct student_lookup) from
((select distinct student_lookup from clean.all_snapshots
	where school_year = 2011
	and grade = '11')
except
(select distinct student_lookup from clean.all_snapshots
	where school_year = 2012
	and grade = '12')) as grade_11_to_12;
