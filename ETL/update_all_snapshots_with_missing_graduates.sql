------------- updating clean.all_snapshots with missing_graduates data in table `Districts1516MissingGraddates` --------

update clean.all_snapshots t1 
	set graduation_date=
	( 
		select to_date(t2."GraduationDate", 'MM/DD/YYYY') as grad_date from public."Districts1516MissingGraddates" t2
  		where t2."StudentLookup"=t1.student_lookup 
  		order by grad_date desc limit 1
  	)
	where exists 
	( 
		select * from public."Districts1516MissingGraddates" t2 
  		where t2."StudentLookup"=t1.student_lookup
	);

-- check the updated all_sanpshots and compare dates to missing_graduates
--select  t1.student_lookup, t1.graduation_date, to_date(t2."GraduationDate", 'MM/DD/YYYY) as miss_grad_date, t2."GraduationDate", count(*)
--	from clean.all_snapshots t1, public."Districts1516MissingGraddates" t2
--	where t1.student_lookup = t2."StudentLookup"
--	group by t1.student_lookup, t2."StudentLookup", t1.graduation_date, miss_grad_date
--	order by t1.graduation_date desc, student_lookup;
