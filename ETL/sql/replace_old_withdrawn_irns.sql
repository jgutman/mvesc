-- create a temporary table of new IRNs with better column names
create temporary table explore_new_withdrawal_irns as
select "StudentLookup" student_lookup, "SentToIRN" withdrawn_to_irn,
  "SenttoDistrict" withdrawn_to_district, "School" school, "District" district
  from public."Miss_transfer_MLF_71916";

-- replace the new irns in the withdrawn to irn column where new irn is not null
create temporary table joined_new_irns as
  (select *, coalesce(new_irns.new_irn, tracking.withdrawn_to_irn) keep_irn from
      (select * from clean.wrk_tracking_students) as tracking
  left join
      (select student_lookup, withdrawn_to_irn new_irn from
        explore_new_withdrawal_irns
        where withdrawn_to_irn is not null) as new_irns
  using(student_lookup));

-- remove unmerged versions of withdrawn_to_irn
alter table joined_new_irns
drop column withdrawn_to_irn,
drop column new_irn;
alter table joined_new_irns
rename column keep_irn to withdrawn_to_irn;

-- replace tracking table with updated version
drop table clean.wrk_tracking_students;
create table clean.wrk_tracking_students as
  select * from joined_new_irns;

-- drop temporary tables
drop table joined_new_irns;
drop table explore_new_withdrawal_irns;
