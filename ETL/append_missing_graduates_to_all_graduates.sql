/* This script is to append public.Districts1516MissingGraddates to clean.all_graduates
 * Procedure:
 *  1. Create a temporary table of missing_graduates;
 *  2. Correct data types to be consistent with clean.all_graduates;
 *  3. Remove duplicates from temporary table: 5778, 7067, 48111, 21708, 3139;
 *  4. Append temporary table to clean.all_graduates; 
 *  5. Double check clean.all_graduates has unique student_lookup's. 
 */


--------- Append missing_graduates to clean.all_graduates --------
-- create temp miss_graduates table
drop table temp_miss_graduates;
create temporary table temp_miss_graduates as 
(select * from public."Districts1516MissingGraddates");

-- change data types of temp_miss_graduates to be consistent with clean.all_graduates
alter table temp_miss_graduates alter column "GraduationDate" type date using to_date("GraduationDate", 'MM/DD/YYYY');
alter table temp_miss_graduates alter column "StudentLookup" type integer;

-- delete duplicates 
delete from temp_miss_graduates 
	where "StudentLookup" in 
	(
		select student_lookup from clean.all_graduates
		where student_lookup in 
		(select "StudentLookup" from temp_miss_graduates)
	);
	
-- append the result to clean.all_graduates
insert into clean.all_graduates
(select "StudentLookup" as student_lookup, "GraduationDate" as graduation_date 
	from temp_miss_graduates
);

-- check current clean.all_graduates table; make sure unique student_lookup
select count(*) from clean.all_graduates;
select student_lookup, count(*) from clean.all_graduates
	group by student_lookup order by count(*) desc;


