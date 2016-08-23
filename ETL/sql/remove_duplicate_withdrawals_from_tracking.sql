-- function to take an array of strings and a table column and
-- map string matching 'pattern%' in column to int
-- to be used in conjunction with order by clause
create or replace function idx(anyarray, anyelement)
  returns int as
$$
  select i from (
     select generate_series(array_lower($1,1),array_upper($1,1))
  ) g(i)
  where $2 like $1[i]
  limit 1;
$$ language SQL immutable;

-- There's probably a better way to over-write the contents of this table
-- For now, copy old contents to temporary table and drop the original
create temporary table tracking_students_experiment as
  select * from clean.wrk_tracking_students;
drop table clean.wrk_tracking_students;

-- Selects students who have more than one withdraw reason or irn on same date
-- Sorts these records for each student in custom sort order defined below
create temporary table sorted_withdrawal_reasons as
  (select *
	from tracking_students_experiment
	where student_lookup in (
	select student_lookup from tracking_students_experiment
	group by student_lookup
	having count(distinct withdraw_reason) > 1
	or count(distinct withdrawn_to_irn) > 1)
	order by student_lookup,
	idx(array['graduate','dropout%','withdrew%','expelled',
      'transferred%', '%'], withdraw_reason));

-- Grab only the firstmost record for each student in custom sort order
-- Then union with all the students that have only one record
create table clean.wrk_tracking_students as
  (select distinct on (student_lookup) *
  from sorted_withdrawal_reasons
  order by student_lookup,
  idx(array['graduate','dropout%','withdrew%','expelled',
    'transferred%', '%'], withdraw_reason))
union
  (select * from tracking_students_experiment
	where student_lookup not in
	(select distinct student_lookup from sorted_withdrawal_reasons));
