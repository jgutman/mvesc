/* Cleaning Table OAAOGT_0616
 * Step 1: Copy original table from public to clean
 * Step 2: *Change column names to lower case
 * Step 3: clean column by column 
*/

/****************** Step 1: copy table ***********************/
-- create a new and same table in schema clean
CREATE TABLE clean.oaaogt_0616 as table public."OAAOGT_0616";

/********* Step 2: change column names to lower case *************/
-- sql command to generate sql command to lower column names
--SELECT array_to_string(ARRAY(SELECT 'ALTER TABLE ' || quote_ident(c.table_schema) || '.'
--  || quote_ident(c.table_name) || ' RENAME "' || c.column_name || '" TO ' || quote_ident(lower(c.column_name)) || ';'
--  FROM information_schema.columns As c
--  WHERE c.table_schema NOT IN('information_schema', 'pg_catalog') 
--  	  and c.table_schema='clean'
--  	  and c.table_name='oaaogt_0616'
--      AND c.column_name <> lower(c.column_name) 
--  ORDER BY c.table_schema, c.table_name, c.column_name
--  ) , E'\r') As ddlsql;
  
-- the following commands are to lower column names
ALTER TABLE clean.oaaogt_0616 RENAME "DOB" TO dob;
ALTER TABLE clean.oaaogt_0616 RENAME "Eighth_Math_PL" TO eighth_math_pl;
ALTER TABLE clean.oaaogt_0616 RENAME "Eighth_Math_SS" TO eighth_math_ss;
ALTER TABLE clean.oaaogt_0616 RENAME "Eighth_Read_PL" TO eighth_read_pl;
ALTER TABLE clean.oaaogt_0616 RENAME "Eighth_Read_SS" TO eighth_read_ss;
ALTER TABLE clean.oaaogt_0616 RENAME "Eighth_Science_PL" TO eighth_science_pl;
ALTER TABLE clean.oaaogt_0616 RENAME "Eighth_Science_SS" TO eighth_science_ss;
ALTER TABLE clean.oaaogt_0616 RENAME "Eighth_SocStudies_PL" TO eighth_socstudies_pl;
ALTER TABLE clean.oaaogt_0616 RENAME "Eighth_SocStudies_SS" TO eighth_socstudies_ss;
ALTER TABLE clean.oaaogt_0616 RENAME "Ethnicity" TO ethnicity;
ALTER TABLE clean.oaaogt_0616 RENAME "Fifth_Math_PL" TO fifth_math_pl;
ALTER TABLE clean.oaaogt_0616 RENAME "Fifth_Math_SS" TO fifth_math_ss;
ALTER TABLE clean.oaaogt_0616 RENAME "Fifth_Read_PL" TO fifth_read_pl;
ALTER TABLE clean.oaaogt_0616 RENAME "Fifth_Read_SS" TO fifth_read_ss;
ALTER TABLE clean.oaaogt_0616 RENAME "Fifth_Science_PL" TO fifth_science_pl;
ALTER TABLE clean.oaaogt_0616 RENAME "Fifth_Science_SS" TO fifth_science_ss;
ALTER TABLE clean.oaaogt_0616 RENAME "Fifth_SocStudies_PL" TO fifth_socstudies_pl;
ALTER TABLE clean.oaaogt_0616 RENAME "Fifth_SocStudies_SS" TO fifth_socstudies_ss;
ALTER TABLE clean.oaaogt_0616 RENAME "Fourth_Ctz_PL" TO fourth_ctz_pl;
ALTER TABLE clean.oaaogt_0616 RENAME "Fourth_Ctz_SS" TO fourth_ctz_ss;
ALTER TABLE clean.oaaogt_0616 RENAME "Fourth_Math_PL" TO fourth_math_pl;
ALTER TABLE clean.oaaogt_0616 RENAME "Fourth_Math_SS" TO fourth_math_ss;
ALTER TABLE clean.oaaogt_0616 RENAME "Fourth_Read_PL" TO fourth_read_pl;
ALTER TABLE clean.oaaogt_0616 RENAME "Fourth_Read_SS" TO fourth_read_ss;
ALTER TABLE clean.oaaogt_0616 RENAME "Fourth_Science_PL" TO fourth_science_pl;
ALTER TABLE clean.oaaogt_0616 RENAME "Fourth_Science_SS" TO fourth_science_ss;
ALTER TABLE clean.oaaogt_0616 RENAME "Fourth_Write_PL" TO fourth_write_pl;
ALTER TABLE clean.oaaogt_0616 RENAME "Fourth_Write_SS" TO fourth_write_ss;
ALTER TABLE clean.oaaogt_0616 RENAME "Gender" TO gender;
ALTER TABLE clean.oaaogt_0616 RENAME "KRAL" TO kral;
ALTER TABLE clean.oaaogt_0616 RENAME "KRAL_PL" TO kral_pl;
ALTER TABLE clean.oaaogt_0616 RENAME "MI" TO mi;
ALTER TABLE clean.oaaogt_0616 RENAME "OGT_Math_PL" TO ogt_math_pl;
ALTER TABLE clean.oaaogt_0616 RENAME "OGT_Math_SS" TO ogt_math_ss;
ALTER TABLE clean.oaaogt_0616 RENAME "OGT_Read_PL" TO ogt_read_pl;
ALTER TABLE clean.oaaogt_0616 RENAME "OGT_Read_SS" TO ogt_read_ss;
ALTER TABLE clean.oaaogt_0616 RENAME "OGT_Science_PL" TO ogt_science_pl;
ALTER TABLE clean.oaaogt_0616 RENAME "OGT_Science_SS" TO ogt_science_ss;
ALTER TABLE clean.oaaogt_0616 RENAME "OGT_SocStudies_PL" TO ogt_socstudies_pl;
ALTER TABLE clean.oaaogt_0616 RENAME "OGT_SocStudies_SS" TO ogt_socstudies_ss;
ALTER TABLE clean.oaaogt_0616 RENAME "OGT_Write_PL" TO ogt_write_pl;
ALTER TABLE clean.oaaogt_0616 RENAME "OGT_Write_SS" TO ogt_write_ss;
ALTER TABLE clean.oaaogt_0616 RENAME "Seventh_Math_PL" TO seventh_math_pl;
ALTER TABLE clean.oaaogt_0616 RENAME "Seventh_Math_SS" TO seventh_math_ss;
ALTER TABLE clean.oaaogt_0616 RENAME "Seventh_Read_PL" TO seventh_read_pl;
ALTER TABLE clean.oaaogt_0616 RENAME "Seventh_Read_SS" TO seventh_read_ss;
ALTER TABLE clean.oaaogt_0616 RENAME "Seventh_Write_PL" TO seventh_write_pl;
ALTER TABLE clean.oaaogt_0616 RENAME "Seventh_Write_SS" TO seventh_write_ss;
ALTER TABLE clean.oaaogt_0616 RENAME "Sixth_Ctz_PL" TO sixth_ctz_pl;
ALTER TABLE clean.oaaogt_0616 RENAME "Sixth_Ctz_SS" TO sixth_ctz_ss;
ALTER TABLE clean.oaaogt_0616 RENAME "Sixth_Math_PL" TO sixth_math_pl;
ALTER TABLE clean.oaaogt_0616 RENAME "Sixth_Math_SS" TO sixth_math_ss;
ALTER TABLE clean.oaaogt_0616 RENAME "Sixth_Read_PL" TO sixth_read_pl;
ALTER TABLE clean.oaaogt_0616 RENAME "Sixth_Read_SS" TO sixth_read_ss;
ALTER TABLE clean.oaaogt_0616 RENAME "Sixth_Science_PL" TO sixth_science_pl;
ALTER TABLE clean.oaaogt_0616 RENAME "Sixth_Science_SS" TO sixth_science_ss;
ALTER TABLE clean.oaaogt_0616 RENAME "Sixth_Write_PL" TO sixth_write_pl;
ALTER TABLE clean.oaaogt_0616 RENAME "Sixth_Write_SS" TO sixth_write_ss;
ALTER TABLE clean.oaaogt_0616 RENAME "SSN" TO ssn;
ALTER TABLE clean.oaaogt_0616 RENAME "StudentLookup" TO studentlookup;
ALTER TABLE clean.oaaogt_0616 RENAME "Third_Math_PL" TO third_math_pl;
ALTER TABLE clean.oaaogt_0616 RENAME "Third_Math_SS" TO third_math_ss;
ALTER TABLE clean.oaaogt_0616 RENAME "Third_Read_PL" TO third_read_pl;
ALTER TABLE clean.oaaogt_0616 RENAME "Third_Read_SS" TO third_read_ss;

-- Columns data types 
--select TABLE_SCHEMA, COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH 
--from INFORMATION_SCHEMA.COLUMNS 
--where TABLE_NAME='oaaogt_0616' and TABLE_SCHEMA='clean';


/**************** Step 3: clean data column by column ****************/
-- column 1: studentlookup: nothing to clean
--select count(distinct studentlookup) from clean.oaaogt_0616; 
--select studentlookup, count(*) from clean.oaaogt_0616
--	where studentlookup=0 or studentlookup is null
--	group by studentlookup;
	
-- column 2: mi: mostly missing values and should be deleted
--select mi, count(*) from clean.oaaogt_0616 group by mi order by count(*) desc;
ALTER TABLE clean.oaaogt_0616 DROP COLUMN mi;

-- column 3: dob (1485 missing) data type converted to DATE
--select dob, count(*) from clean.oaaogt_0616
--	where dob='' or dob is null group by dob;
--select to_date(dob, 'MM/DD/YYYY') 
--	from clean.oaaogt_0616 where dob is not null limit 100;
ALTER TABLE clean.oaaogt_0616 ALTER COLUMN dob TYPE DATE using to_date(dob, 'MM/DD/YYYY');
--select dob, count(*) from clean.oaaogt_0616 where dob is null group by dob; 

-- column 4: gender (NULL: 1485) data type converted to DATE
--select trim(gender), count(*) from clean.oaaogt_0616 group by gender;
--select upper(left(trim(gender), 1)), count(*) from clean.oaaogt_0616 group by left(trim(gender), 1);
UPDATE clean.oaaogt_0616 SET gender=upper(left(trim(gender), 1));

-- column: ssn: dropped
ALTER TABLE clean.oaaogt_0616 DROP COLUMN ssn;

-- column: ethnicity (!!! need codes and categories to clean)
--select trim(ethnicity) as ethn, count(*) from clean.oaaogt_0616 group by trim(ethnicity) order by ethn;
--select ethnicity, count(*) from clean.oaaogt_0616 group by ethnicity order by ethnicity;

UPDATE ONLY clean.oaaogt_0616
SET ethnicity = 
		case
		when trim(ethnicity)='*' then 'Multiracial'
		when trim(ethnicity)='1' then 'American Indian'
		when trim(ethnicity)='2' then 'Asian/Pacific Islander'
		when trim(ethnicity)='3' then 'Black/African American'
		when trim(ethnicity)='4' then 'Hispanic'
		when trim(ethnicity)='5' then 'White'
		when trim(ethnicity)='6' then 'Multi-Racial'
		when trim(ethnicity)='7' then 'Other'
		when lower(trim(ethnicity))='i' then 'American Indian'
		when lower(trim(ethnicity))='a' then 'Asian/Pacific Islander'
		when lower(trim(ethnicity))='b' then 'Black'
		when lower(trim(ethnicity))='h' then 'Hispanic'
		when lower(trim(ethnicity))='w' then 'White'
		when lower(trim(ethnicity))='m' then 'Multiracial'
		when lower(trim(ethnicity))='p' then 'Asian/Pacific Islander'
		when lower(trim(ethnicity))='american_ind' then 'American Indian'
		when lower(trim(ethnicity))='am_indian' then 'American Indian'
		when lower(trim(ethnicity))='asian or pacific islander' then 'Asian/Pacific Islander'
		when lower(trim(ethnicity))='asian_pac isl' then 'Asian/Pacific Islander'
		when lower(trim(ethnicity))='black, non-hispanic' then 'Black'
		when lower(trim(ethnicity))='black/african american' then 'Black'
		when lower(trim(ethnicity))='black_afr am' then 'Black/African American'
		when lower(trim(ethnicity))='hispanic' then 'Hispanic'
		when lower(trim(ethnicity))='multi' then 'Multiracial'
		when lower(trim(ethnicity))='multiple mark' then 'Multiracial'
		when lower(trim(ethnicity))='multi racial' then 'Multiracial'
		when lower(trim(ethnicity))='multi_racial' then 'Multiracial'
		when lower(trim(ethnicity))='multi-racial' then 'Multiracial'
		when lower(trim(ethnicity))='white, non-hispanic' then 'White'
		else trim(ethnicity)
		end;
		

-- column: kral (Kindergarten Readiness Assessment; 73% missing; match kral_pl)
--select kral, count(*)/1.0/(select count(*)from clean.oaaogt_0616) 
--	from clean.oaaogt_0616 group by kral order by kral;

-- column: kral_pl (Kindergarden Readiness Assessment; 73% missing; match kral)
--select kral_pl, count(*)/1.0/(select count(*)from clean.oaaogt_0616) 
--	from clean.oaaogt_0616 group by kral_pl order by kral_pl;
	
-- column: eigth_read_pl and eigth_read_ss, 61% missing
--select eighth_read_pl, eighth_read_ss, count(*)
--	from clean.oaaogt_0616
--	group by eighth_read_pl, eighth_read_ss
--	order by eighth_read_ss;
--	
-- column: eigth_science_pl and eigth_science_ss, 66% missing
--select eighth_science_pl, eighth_science_ss, count(*)
--	from clean.oaaogt_0616
--	group by eighth_science_pl, eighth_science_ss
--	order by eighth_science_ss;
--	
-- column: eigth_science_pl and eigth_science_ss, 66% missing
--select ogt_science_pl, ogt_science_ss, count(*)
--	from clean.oaaogt_0616
--	group by ogt_science_pl, ogt_science_ss
--	order by ogt_science_ss;
