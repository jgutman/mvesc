/* Generate Month, Week, and Day from a data in table `all_absences` 
 * code may be modified for other tables
*/

-- check current date data type: column 'date' is `date` data type
--SELECT table_schema, table_name, column_name, data_type, character_maximum_length 
--	FROM information_schema.columns
--	WHERE table_schema='clean' and table_name='all_absences';

--1. create month of the year: test, add col, update col
--select date, EXTRACT(MONTH FROM "date") from clean.all_absences limit 20;
alter table clean.all_absences add column month int default null;
update only clean.all_absences SET month = EXTRACT(MONTH FROM date);

--2. create day of the week: test, add col, update col
--select date, EXTRACT(WEEK FROM date) from clean.all_absences limit 10;
alter table clean.all_absences add column week int default null;
update only clean.all_absences SET week = EXTRACT(WEEK FROM date);

--3. create weekday of the week: test, add col, update col
--select date, EXTRACT(dow FROM date) from clean.all_absences limit 10;
alter table clean.all_absences add column weekday int default null;
update only clean.all_absences SET weekday = EXTRACT(dow FROM date);

