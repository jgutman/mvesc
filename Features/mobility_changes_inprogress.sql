create or replace function idx(anyarray, anyelement)
  returns int as
$$
  select i from (
     select generate_series(array_lower($1,1),array_upper($1,1))
  ) g(i)
  where $2 like $1[i]
  limit 1;
$$ language SQL immutable;

drop table if exists mobility_changes;

create temporary table mobility_changes as
  select distinct on (student_lookup, school_year)
    student_lookup, school_year, grade, status, street, district, city,
    district_withdraw_date, district_admit_date from clean.all_snapshots
  order by student_lookup, school_year,
    idx(array['active','foster','inactive', 'resident', '%'], status),
    district_admit_date desc
;
