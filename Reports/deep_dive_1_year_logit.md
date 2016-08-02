# Report for deep dive 1 year logit
initial results to use in the deep dive 6/26, only using 9th grade data, re-running on 7/2

### Model Options
* label used: definite
* initial cohort grade: 9
* test cohorts: 2008
	 * 31 positive examples, 984 negative examples
* train cohorts: 2006, 2007
	 * 48 postive examples, 1964 negative examples
* cross-validation scheme: leave cohort out
	 * searching penalty in l1
	 * chose penalty = l1
	 * searching C in 1.0
	 * chose C = 1.0
	 * using custom_precision_10
* imputation strategy: median plus dummies
* scaling strategy: robust

### Features Used
* demographics
	 * gender
	 * ethnicity
* snapshots
	 * days_absent_gr_9
	 * gifted_gr_9
	 * days_absent_unexcused_gr_9
	 * limited_english_gr_9
	 * special_ed_gr_9
	 * status_gr_9
	 * iss_gr_9
	 * discipline_incidents_gr_9
	 * disadvantagement_gr_9
	 * oss_gr_9
	 * disability_gr_9
	 * district_gr_9
* grades
	 * gpa_gr_9
* mobility
	 * n_cities_to_gr_9
	 * n_districts_to_gr_9
	 * n_addresses_to_gr_9

### Performance Metrics
on average, model run in 0.06 seconds (1 times) <br/>precision on top 10%: 0.196 <br/>precision on top 5%: 0.294 <br/>top features: gpa_gr_9_isnull (1.5), gpa_gr_9 (-1.5), special_ed_gr_9_100 (-1.4)
![deep_dive_1_year_logit_score_dist.png](deep_dive_1_year_logit_score_dist.png)
![deep_dive_1_year_logit_precision_recall_at_k.png](deep_dive_1_year_logit_precision_recall_at_k.png)
![deep_dive_1_year_logit_pr_vs_threshold.png](deep_dive_1_year_logit_pr_vs_threshold.png)
![deep_dive_1_year_logit_confusion_mat_0.3.png](deep_dive_1_year_logit_confusion_mat_0.3.png)
