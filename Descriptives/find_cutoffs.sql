-- temporary table comparing GPA in 9th grade for positives and negatives
-- in 10th grade model test set
drop table if exists grades_compare;
create temporary table grades_compare as
select student_lookup, gpa_gr_9,
	case
		when student_lookup in (select student_lookup from model.outcome
			where definite_plus_ogt = 1
			and cohort_10th = 2013) then 1
		when student_lookup in (select student_lookup from model.outcome
			where definite_plus_ogt = 0
			and cohort_10th = 2013) then 0
	end as dropout
from model.grades;

-- temporary table comparing absences in 9th grade for positives and negatives
-- in 10th grade model test set (total and unexcused)
drop table if exists attendance_compare;
create temporary table attendance_compare as
select student_lookup, absence_gr_9, absence_unexcused_gr_9,
	case
		when student_lookup in (select student_lookup from model.outcome
			where definite_plus_ogt = 1
			and cohort_10th = 2013) then 1
		when student_lookup in (select student_lookup from model.outcome
			where definite_plus_ogt = 0
			and cohort_10th = 2013) then 0
	end as dropout
from model.absence;

-- temporary table comparing discipline in 9th grade for positives and negatives
-- in 10th grade model test set (total and in/out school suspensions)
drop table if exists discipline_compare;
create temporary table discipline_compare as
select student_lookup, discipline_incidents_gr_9, iss_gr_9, oss_gr_9,
	case
		when student_lookup in (select student_lookup from model.outcome
			where definite_plus_ogt = 1
			and cohort_10th = 2013) then 1
		when student_lookup in (select student_lookup from model.outcome
			where definite_plus_ogt = 0
			and cohort_10th = 2013) then 0
	end as dropout
from model.snapshots;

--------- grades comparison
select * from grades_compare where dropout is not null;

-- compare grades percentiles across groups to find cutoffs
select dropout,
  percentile_cont(.50) within group (order by gpa_gr_9) as pct_50_gpa_gr_9,
	percentile_cont(.75) within group (order by gpa_gr_9) as pct_75_gpa_gr_9,
	percentile_cont(.90) within group (order by gpa_gr_9) as pct_90_gpa_gr_9
	from grades_compare
	where dropout is not null
	group by dropout;

-- using gpa 2.0 cutoff how many of each group are flagged?
select dropout,
  avg(case when gpa_gr_9 < 2.0 then 1 else 0 end) as avg_low_gpa,
	count(case when gpa_gr_9 < 2.0 then 1 end) as num_low_gpa,
  count(gpa_gr_9)
	from grades_compare
	where dropout is not null
	and gpa_gr_9 is not null
	group by dropout;
-- 58.7% of dropouts vs. 14.8% of non-dropouts

--------- attendance comparison
select * from attendance_compare where dropout is not null;

-- compare total absences percentiles across groups to find cutoffs
select dropout,
  percentile_cont(.50) within group (order by absence_gr_9) as
    pct_50_absence_gr_9,
	percentile_cont(.75) within group (order by absence_gr_9) as
    pct_75_absence_gr_9,
	percentile_cont(.90) within group (order by absence_gr_9) as
    pct_90_absence_gr_9
	from attendance_compare
	where dropout is not null
	group by dropout;

-- using absences 12 or greater cutoff how many of each group are flagged?
select dropout,
  avg(case when absence_gr_9 >= 12.0 then 1 else 0 end) as avg_high_absence,
	count(case when absence_gr_9 >= 12.0 then 1 end) as num_high_absence,
  count(absence_gr_9)
	from attendance_compare
	where dropout is not null
	group by dropout;
  -- 47.6% of dropouts vs. 24.2% of non-dropouts (12 absences)
  -- 29.0% of dropouts vs. 7.9% of non-dropouts (18 absences)

--------- attendance comparison
select * from discipline_compare where dropout is not null;

-- compare total discipline percentiles across groups to find cutoffs
select dropout,
  percentile_cont(.50) within group (order by discipline_incidents_gr_9) as
    pct_50_discipline_gr_9,
  percentile_cont(.75) within group (order by discipline_incidents_gr_9) as
    pct_75_discipline_gr_9,
  percentile_cont(.90) within group (order by discipline_incidents_gr_9) as
    pct_90_discipline_gr_9
	from discipline_compare
	where dropout is not null
	group by dropout;

-- using discipline 2 or greater cutoff how many of each group are flagged?
select dropout,
  avg(case when discipline_incidents_gr_9 >= 2.0 then 1 else 0 end) as
    avg_discipline,
	count(case when discipline_incidents_gr_9 >= 2.0 then 1 end) as
    num_discipline,
  count(discipline_incidents_gr_9)
	from discipline_compare
	where dropout is not null
	group by dropout;
  -- 41.6% of dropouts vs. 17.2% of non-dropouts with 2 or more incidents
  -- 34.1% of dropouts vs. 11.2% of non-dropouts with 3 or more incidents

-- get flags on three categories for all students
drop table if exists all_flags;
create temporary table all_flags as
select * from
	(select student_lookup, dropout,
	case when gpa_gr_9 < 2.0 then 1 else 0 end as grades_flagged
	from grades_compare
	where dropout is not null) grades
left join
	(select student_lookup,
	case when absence_gr_9 >= 12.0 then 1 else 0 end as attendance_flagged
	from attendance_compare
	where dropout is not null) attendance
using(student_lookup)
left join
	(select student_lookup,
	case when discipline_incidents_gr_9 >= 2.0 then 1 else 0 end as discipline_flagged
	from discipline_compare
	where dropout is not null) discipline
using(student_lookup);

-- add number of flags triggered per student
alter table all_flags add column count_flags int default 0;
update all_flags
    set count_flags =
      (grades_flagged + attendance_flagged + discipline_flagged);

select dropout, count_flags, count(*)
	from all_flags
	group by dropout, count_flags
	order by dropout, count_flags;

-- dropouts:
-- 	3 flags: 7.9%
--  2-3 flags: 43.7%
--  1-3 flags: 77.8%

-- graduates:
-- 	3 flags: 3.1%
--  2-3 flags: 11.2%
--  1-3 flags: 39.4%

-- system flags 14.8% of students
-- if you flag all students with 2 or more flags:
-- * total flagged = 338
-- * total students = 2286
-- out of 338 flagged:
-- * 110 dropouts
-- * precision = .325
-- out of 252 dropouts:
-- * 110 flagged
-- * recall = .437

drop table if exists top_risk;
create temporary table top_risk as
select student_lookup, filename, true_label,
	rank() over(partition by filename order by predicted_score desc) risk_rank
	from model.predictions_new where
	filename in ('08_17_2016_grade_10_param_set_22_logit_jg_123',
		'08_17_2016_grade_10_param_set_16_RF_jg_139')
	and split = 'test';

alter table top_risk add column predicted_label int default 0;
update top_risk
    set predicted_label =
      case when risk_rank <= 338 then 1 else 0 end;

select filename, true_label, predicted_label, count(*)
    from top_risk
    group by filename, true_label, predicted_label
    order by filename, true_label, predicted_label;

-- if we change disciplines incidents to 3 or more and absences to 18 or more
-- now we flag only 197 students out of 2286, or 8.6%
