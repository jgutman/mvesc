# Report for param set 27 logit
testing all options by looping throughwith a just 100 students

### Model Options
* label used: definite
* initial cohort grade: 9
* test cohorts: 2011, 2012
	 * 31 positive examples, 19 negative examples
* train cohorts: 2007, 2008, 2009, 2010
	 * 17 postive examples, 26 negative examples
* cross-validation scheme: past cohorts only
	 * searching C in 1.0
	 * chose C = 1.0
	 * searching penalty in l1
	 * chose penalty = l1
	 * using ['custom_precision_5', 'f1']
* imputation strategy: median plus dummies
* scaling strategy: standard

### Features Used
* demographics
	 * gender
	 * ethnicity
* snapshots
	 * oss_gr_8
	 * section_504_plan_gr_8
	 * special_ed_gr_8
	 * district_gr_8
	 * days_absent_gr_8
	 * iss_gr_8
	 * days_present_gr_8
	 * disability_gr_8
	 * days_absent_unexcused_gr_8
	 * discipline_incidents_gr_8
	 * limited_english_gr_8
	 * status_gr_8
	 * gifted_gr_8
	 * days_absent_excused_gr_8
	 * disadvantagement_gr_8
* grades
	 * gpa_gr_8
* oaa_normalized
	 * third_math_percentile
	 * sixth_math_pl
	 * fifth_math_pl
	 * fourth_read_normalized
	 * eighth_math_pl
	 * sixth_math_percentile
	 * fourth_math_normalized
	 * seventh_read_pl
	 * seventh_math_percentile
	 * eighth_math_normalized
	 * seventh_read_percentile
	 * fifth_math_normalized
	 * seventh_math_normalized
	 * fifth_read_normalized
	 * eighth_read_percentile
	 * fifth_socstudies_normalized
	 * sixth_read_normalized
	 * seventh_read_normalized
	 * eighth_science_percentile
	 * fourth_read_percentile
	 * fifth_read_percentile
	 * fifth_math_percentile
	 * fifth_read_pl
	 * fifth_science_percentile
	 * third_read_percentile
	 * sixth_read_percentile
	 * sixth_math_normalized
	 * fifth_science_normalized
	 * eighth_science_pl
	 * third_read_pl
	 * fourth_math_pl
	 * fifth_socstudies_pl
	 * eighth_read_normalized
	 * eighth_read_pl
	 * eighth_math_percentile
	 * third_math_normalized
	 * fifth_science_pl
	 * eighth_science_normalized
	 * sixth_read_pl
	 * fourth_read_pl
	 * fourth_math_percentile
	 * seventh_math_pl
	 * third_read_normalized
	 * third_math_pl

### Performance Metrics
on average, model run in 0.00 seconds (1 times) <br/>precision on top 15%: 0.75 <br/>precision on top 10%: 0.8333 <br/>precision on top 5%: 1.0 <br/>recall on top 15%: 0.1935 <br/>recall on top 10%: 0.1613 <br/>recall on top 5%: 0.09677 <br/>AUC value is: 0.6655 <br/>top features: gpa_gr_8 (-1.4), fifth_science_normalized (-0.87), oss_gr_8 (0.86)
![param_set_27_logit_confusion_mat_0.3.png](figs/param_set_27_logit_confusion_mat_0.3.png)
![param_set_27_logit_pr_vs_threshold.png](figs/param_set_27_logit_pr_vs_threshold.png)
![param_set_27_logit_score_dist.png](figs/param_set_27_logit_score_dist.png)
![param_set_27_logit_precision_recall_at_k.png](figs/param_set_27_logit_precision_recall_at_k.png)
