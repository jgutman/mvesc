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
	select student_lookup, num_ogt_passed from ogt_pass_temp
);