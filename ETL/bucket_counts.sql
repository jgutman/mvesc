select count(distinct(student_lookup)) from clean.wrk_tracking_students where
  "2010" = '09';
select count(distinct(student_lookup)) from clean.wrk_tracking_students where
  "2010" = '09' and student_lookup in (select student_lookup from clean.all_graduates);
select count(distinct(student_lookup)) from clean.wrk_tracking_students where
  "2010" = '09' and student_lookup in (select student_lookup from clean.all_graduates
    where graduation_date <= '2014-09-01');
select count(distinct(student_lookup)) from clean.wrk_tracking_students where
  "2010" = '09' and student_lookup in (select student_lookup from clean.all_graduates
    where graduation_date <= '2015-09-01' and graduation_date > '2014-09-01');
select count(distinct(student_lookup)) from clean.wrk_tracking_students where
  "2010" = '09' and student_lookup in (select student_lookup from clean.all_graduates
    where graduation_date > '2015-09-01');

select count(distinct(student_lookup)) from clean.wrk_tracking_students where
  "2010" = '09' and student_lookup not in (select student_lookup from clean.all_graduates);
select count(distinct(student_lookup)) from clean.wrk_tracking_students where
  "2010" = '09' and student_lookup not in (select student_lookup from clean.all_graduates)
  and withdraw_reason is not null;

select count(distinct(student_lookup)) from clean.wrk_tracking_students where
  "2010" = '09' and student_lookup not in (select student_lookup from clean.all_graduates)
  and withdraw_reason like 'dropout%';

select count(distinct student_lookup) from clean.wrk_tracking_students where
  "2010" = '09' and student_lookup not in (select student_lookup from clean.all_graduates)
  and withdraw_reason like 'transfer%' and withdrawn_to_irn::int in
    (select building_irn from public."IRN_DORP_GRAD_RATE1415");
