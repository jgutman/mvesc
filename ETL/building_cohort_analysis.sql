-- most common withdrawal reasons for all students in snapshots file
select withdraw_reason, count(withdraw_reason) from clean.all_snapshots
	group by withdraw_reason
	order by count(withdraw_reason) desc;

-- start with the number of students in 4th grade in 2006, show how many progress to the next grade level each year
-- how many are left of the original cohort by 12th grade?
	(select 2006 as school_year, count(*) from (select distinct(student_lookup) from clean.wrk_tracking_students
		where "2006" = '04') as grade_4_in_2006)
union
	(select 2007 as school_year, count(*) from (select distinct(student_lookup) from clean.wrk_tracking_students
		where "2006" = '04') as grade_4_in_2006
	where student_lookup in (select distinct(student_lookup) from clean.wrk_tracking_students
		where "2007" = '05'))
union
	(select 2008 as school_year, count(*) from (select distinct(student_lookup) from clean.wrk_tracking_students
		where "2006" = '04') as grade_4_in_2006
	where student_lookup in (select distinct(student_lookup) from clean.wrk_tracking_students
		where "2008" = '06'))
union
	(select 2009 as school_year, count(*) from (select distinct(student_lookup) from clean.wrk_tracking_students
		where "2006" = '04') as grade_4_in_2006
	where student_lookup in (select distinct(student_lookup) from clean.wrk_tracking_students
		where "2009" = '07'))
union
	(select 2010 as school_year, count(*) from (select distinct(student_lookup) from clean.wrk_tracking_students
		where "2006" = '04') as grade_4_in_2006
	where student_lookup in (select distinct(student_lookup) from clean.wrk_tracking_students
		where "2010" = '08'))
union
	(select 2011 as school_year, count(*) from (select distinct(student_lookup) from clean.wrk_tracking_students
		where "2006" = '04') as grade_4_in_2006
	where student_lookup in (select distinct(student_lookup) from clean.wrk_tracking_students
		where "2011" = '09'))
union
	(select 2012 as school_year, count(*) from (select distinct(student_lookup) from clean.wrk_tracking_students
		where "2006" = '04') as grade_4_in_2006
	where student_lookup in (select distinct(student_lookup) from clean.wrk_tracking_students
		where "2012" = '10'))
union
	(select 2013 as school_year, count(*) from (select distinct(student_lookup) from clean.wrk_tracking_students
		where "2006" = '04') as grade_4_in_2006
	where student_lookup in (select distinct(student_lookup) from clean.wrk_tracking_students
		where "2013" = '11'))
union
	(select 2014 as school_year, count(*) from (select distinct(student_lookup) from clean.wrk_tracking_students
		where "2006" = '04') as grade_4_in_2006
	where student_lookup in (select distinct(student_lookup) from clean.wrk_tracking_students
		where "2014" = '12'))
order by school_year;
