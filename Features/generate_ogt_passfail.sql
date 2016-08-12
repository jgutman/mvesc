-----------------------------
-- MAKE OGT_PASSFAIL TABLE --
-----------------------------

-- convert oaaogt to numeric
drop table if exists ogt_temp;
create temp table ogt_temp as (
	select student_lookup, 
		case
			when ogt_read_ss in ('DNA', 'INV', 'DNS', '99', 'TOG') then null
			else cast(ogt_read_ss as int)
			end,
		case
			when ogt_math_ss in ('DNA', 'INV', 'DNS', '99', 'TOG') then null
			else cast(ogt_math_ss as int)
			end,
		case
			when ogt_write_ss in ('DNA', 'INV', 'DNS', '99', 'TOG') then null
			else cast(ogt_write_ss as int)
			end,
		case
			when ogt_science_ss in ('DNA', 'INV', 'DNS', '99', 'TOG') then null
			else cast(ogt_science_ss as int)
			end,
		case
			when ogt_socstudies_ss in ('DNA', 'INV', 'DNS', '99', 'TOG') then null
			else cast(ogt_socstudies_ss as int)
			end
	from clean.oaaogt
);

drop table if exists ogt_pass_temp;
create temp table ogt_pass_temp as (
	select student_lookup,
		case
			when ogt_read_ss > 399 then 1
			else 0
			end as ogt_read_pass,
		case
			when ogt_math_ss > 399 then 1
			else 0
			end as ogt_math_pass,
		case
			when ogt_write_ss > 399 then 1
			else 0
			end as ogt_write_pass,
		case
			when ogt_science_ss > 399 then 1
			else 0
			end as ogt_science_pass,
		case
			when ogt_socstudies_ss > 399 then 1
			else 0
			end as ogt_socstudies_pass,
		-- getting total number of tests taken
		case
			when ogt_read_ss is not null then 1
			else 0
			end as ogt_read_took,
		case
			when ogt_math_ss is not null then 1
			else 0
			end as ogt_math_took,
		case
			when ogt_write_ss is not null then 1
			else 0
			end as ogt_write_took,
		case
			when ogt_science_ss is not null then 1
			else 0
			end as ogt_science_took,
		case
			when ogt_socstudies_ss is not null then 1
			else 0
			end as ogt_socstudies_took
	from ogt_temp
);

alter table ogt_pass_temp add num_ogt_passed int;
update ogt_pass_temp set
	num_ogt_passed = ogt_read_pass + ogt_math_pass + ogt_write_pass +
		ogt_science_pass + ogt_socstudies_pass;
alter table ogt_pass_temp add num_ogt_took int;
update ogt_pass_temp set
	num_ogt_took = ogt_read_took + ogt_math_took + ogt_write_took +
		ogt_science_took + ogt_socstudies_took;

drop table if exists model.ogt_passfail;
create table model.ogt_passfail as (
	select student_lookup, num_ogt_passed, num_ogt_took from ogt_pass_temp
);

-----------------------------
-- ADD COLUMNS TO OUTCOME --
-----------------------------

drop table if exists model.outcome_old;
-- rename current outcome table
alter table model.outcome rename to outcome_old;

-- create new table using left join
create table model.outcome as 
(select * from
	(	select *
		from model.outcome_old
	) as orig_outcomes
	-- ogt test info
	left join
	(   select student_lookup, max(num_ogt_passed) as num_ogt_passed,
			max(num_ogt_took) as num_ogt_took
	    from model.ogt_passfail
	    group by student_lookup
	) as ogt_info
	using(student_lookup)
	-- absence info
	left join
	(   select student_lookup, max(absence_unexcused_gr_11) as absence_unexcused_gr_11,
	        max(absence_unexcused_gr_12) as absence_unexcused_gr_12
	    from model.absence
	    group by student_lookup
	) as absence_unexcused
	using(student_lookup)
	-- gpa info
	left join
	(   select student_lookup, max(gpa_gr_10) as gpa_gr_10,
			max(gpa_gr_11) as gpa_gr_11,
			max(gpa_gr_12) as gpa_gr_12
	    from model.grades
	    group by student_lookup
	) as grades_10_12
	using(student_lookup)
);


-------------------------
-- MAKE NEW CATEGORIES --
-------------------------

alter table model.outcome drop column if exists definite_plus_ogt;
alter table model.outcome add column definite_plus_ogt int;
update model.outcome
	set definite_plus_ogt = case
		when definite = 1 then 1
		when definite = 0 then 0
		when outcome_category = 'uncertain' and 
			((num_ogt_passed < 4 and num_ogt_took > 0) or
				absence_unexcused_gr_11 > 15 or
				absence_unexcused_gr_12 > 15 or
				gpa_gr_10 < 2 or
				gpa_gr_11 < 2 or
				gpa_gr_12 < 2
			) then 1
		when outcome_bucket = 'JVSD/career tech' then 1
		end;

-- drop old outcome table
drop table model.outcome_old;

-- select * from new_outcomes limit 100;

-- select outcome_category, outcome_bucket, definite, definite_plus_ogt, count(outcome_category) from model.outcome 
-- group by outcome_category, outcome_bucket, definite, definite_plus_ogt order by outcome_category, count desc;
						
						