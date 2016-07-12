drop table if exists clean.all_graduates;
-- get all students with a non-null graduation date
-- if multiple conflicting non-null graduation dates, select date
-- from most recent school year snapshot record
create table clean.all_graduates as
(select student_lookup, graduation_date from
	(select student_lookup, max(school_year) as school_year
    from clean.all_snapshots
		where student_lookup in
			(select distinct student_lookup from clean.all_snapshots
        where graduation_date is not null)
		and graduation_date is not null
	group by student_lookup) as latest_grade_with_graduation
left join
	(select student_lookup, school_year, graduation_date from clean.all_snapshots
		where graduation_date is not null) as graduation_dates_valid
using (student_lookup, school_year)) ;
-- some students are not included here
-- they don't have a graduation date in the snapshots table
-- but they do have one in the public."AllGradsTotal" table
insert into clean.all_graduates(student_lookup, graduation_date)
	select "StudentLookup" student_lookup,
		to_date("HIGH_SCHOOL_GRAD_DATE", 'YYYYMMDD') graduation_date
		from public."AllGradsTotal"
		where "StudentLookup" not in
		(select student_lookup from clean.all_graduates);
