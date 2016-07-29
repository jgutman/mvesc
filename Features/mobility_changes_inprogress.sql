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
drop table if exists mobility_transitions;

create table mobility_changes as
  select distinct on (student_lookup, school_year)
    student_lookup, school_year, grade, status, street, district, city,
    district_withdraw_date, district_admit_date from clean.all_snapshots
  order by student_lookup, school_year,
    # what are these single digit status codes
    # priority sort by status : active > foster > inactive > other / null
    # then for identical statuses, grab the most recent district admit
    # for binary transition variables only, not for mobility counts
    idx(array['active','foster','inactive', '%'], status),
    district_admit_date desc;

create table mobility_transitions as
select * from
	(select student_lookup, grade, school_year,
    street != lag(street) over (partition by student_lookup
      order by school_year) as different_street,
    district != lag(district) over (partition by student_lookup
      order by school_year) as different_district,
    city != lag(city) over (partition by student_lookup
      order by school_year) as different_city
      from mobility_changes) compare_street;
