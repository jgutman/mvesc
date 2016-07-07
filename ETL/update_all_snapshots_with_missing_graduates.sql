------------- Complete process of updating all_snapshots with missing_graduates data in table `Districts1516MissingGraddates` --------
 /* Procedures:
  * 1. Create temporary table of missing_graduates;
  * 2. Alter temp_missing_graduates data types to be consistent with `all_snapshots`;
  * 3. Check matches in `all_snapshots` before matching and updating; (code in comments)
  * 4. Update `all_snapshots` based on null graduate_date and matched student_lookup;
  * 5. Check matches again after updating; (code in comments)
  */
 -- create temp miss_graduates table
drop table temp_miss_graduates;
create temporary table temp_miss_graduates as 
(select * from public."Districts1516MissingGraddates");

-- change data types of temp_miss_graduates to be consistent with clean.all_graduates
alter table temp_miss_graduates alter column "GraduationDate" type date using to_date("GraduationDate", 'MM/DD/YYYY');
alter table temp_miss_graduates alter column "StudentLookup" type integer;

-- check if the graduation_date are the same or not
-- all_snapshots either has null or the same graduation_date as in missing_graduates
--select  t1.student_lookup, t1.graduation_date, t2."GraduationDate", count(*)
--	from temp_all_snapshots t1, temp_miss_graduates t2
--	where t1.student_lookup = t2."StudentLookup" and t1.graduation_date is null
--	group by t1.student_lookup, t1.graduation_date, t2."GraduationDate"
--	order by t1.graduation_date desc, student_lookup;


-- use `coalesce` to add the missing graduation date to all_snapshots
update clean.all_snapshots t1 
set graduation_date=
( select "GraduationDate" from temp_miss_graduates t2
  where t2."StudentLookup"=t1.student_lookup limit 1
)
where t1.graduation_date is null and exists 
( select * from temp_miss_graduates t2 
  where t2."StudentLookup"=t1.student_lookup
)
;

-- check the updated all_sanpshots and compare dates to missing_graduates
--select  t1.student_lookup, t2."StudentLookup", t1.graduation_date, t2."GraduationDate", count(*)
--	from clean.all_snapshots t1, temp_miss_graduates t2
--	where t1.student_lookup = t2."StudentLookup"
--	group by t1.student_lookup, t2."StudentLookup", t1.graduation_date, t2."GraduationDate"
--	order by t1.graduation_date desc, student_lookup;
