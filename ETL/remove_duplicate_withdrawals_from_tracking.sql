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

create temporary table sorted_withdrawal_reasons as
  (select student_lookup, withdraw_reason, withdrawn_to_irn,
      district_withdraw_date
	from clean.wrk_tracking_students
	where student_lookup in (
	select student_lookup from clean.wrk_tracking_students
	group by student_lookup
	having count(distinct withdraw_reason) > 1
	or count(distinct withdrawn_to_irn) > 1)
	order by student_lookup,
	idx(array['graduate','dropout%','withdrew%','expelled',
      'transferred%', '%'], withdraw_reason));

drop table if exists clean.wrk_tracking_students;
create table clean.wrk_tracking_students as
  select distinct on (student_lookup) *
  from sorted_withdrawal_reasons
  order by student_lookup,
  idx(array['graduate','dropout%','withdrew%','expelled',
    'transferred%', '%'], withdraw_reason);
