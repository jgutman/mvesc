# Report for deep dive logit
initial results to use in the deep dive 6/26

### Model Options
* label used: definite
* initial cohort grade: 6
* test cohorts: 2008
	 * 48 positive examples, 887 negative examples
* train cohorts: 2006, 2007
	 * 49 postive examples, 1614 negative examples
* cross-validation scheme: leave cohort out
	 * searching C in 1e-05, 0.0001, 0.001, 0.01, 0.1, 1.0, 10.0, 100, 1000
	 * chose C = 1.0
	 * searching penalty in l1, l2
	 * chose penalty = l2
	 * using custom_precision_10
* imputation strategy: median plus dummies
* scaling strategy: robust

### Features Used
* mobility
	 * n_addresses_to_gr_6
	 * n_cities_to_gr_6
	 * n_districts_to_gr_6
	 * n_addresses_to_gr_7
	 * n_cities_to_gr_7
	 * n_districts_to_gr_7
	 * n_addresses_to_gr_8
	 * n_cities_to_gr_8
	 * n_districts_to_gr_8
	 * n_addresses_to_gr_9
	 * n_cities_to_gr_9
	 * n_districts_to_gr_9
* grades
	 * gpa_gr_6
	 * gpa_gr_7
	 * gpa_gr_8
	 * gpa_gr_9
* demographics
	 * ethnicity
	 * gender
* snapshots
	 * disadvantagement_gr_6
	 * disability_gr_6
	 * district_gr_6
	 * gifted_gr_6
	 * iss_gr_6
	 * oss_gr_6
	 * limited_english_gr_6
	 * special_ed_gr_6
	 * status_gr_6
	 * disadvantagement_gr_7
	 * disability_gr_7
	 * district_gr_7
	 * gifted_gr_7
	 * iss_gr_7
	 * oss_gr_7
	 * limited_english_gr_7
	 * special_ed_gr_7
	 * status_gr_7
	 * disadvantagement_gr_8
	 * disability_gr_8
	 * district_gr_8
	 * gifted_gr_8
	 * iss_gr_8
	 * oss_gr_8
	 * limited_english_gr_8
	 * special_ed_gr_8
	 * status_gr_8
	 * disadvantagement_gr_9
	 * disability_gr_9
	 * district_gr_9
	 * gifted_gr_9
	 * iss_gr_9
	 * oss_gr_9
	 * limited_english_gr_9
	 * special_ed_gr_9
	 * status_gr_9
	 * days_absent_gr_6
	 * days_absent_unexcused_gr_6
	 * discipline_incidents_gr_6
	 * days_absent_gr_7
	 * days_absent_unexcused_gr_7
	 * discipline_incidents_gr_7
	 * days_absent_gr_8
	 * days_absent_unexcused_gr_8
	 * discipline_incidents_gr_8
	 * days_absent_gr_9
	 * days_absent_unexcused_gr_9
	 * discipline_incidents_gr_9

### Performance Metrics
on average, model run in 0.19 seconds (18 times) <br/>precision on top 10%: 0.266 <br/>precision on top 5%: 0.404 <br/>top features: status_gr_9_esc (1.5), gpa_gr_7_isnull (1.4), n_cities_to_gr_9 (1.3)
![./figs/deep_dive_logit_confusion_mat_0.3.png](deep_dive_logit_confusion_mat_0.3.png)
![./figs/deep_dive_logit_pr_vs_threshold.png](deep_dive_logit_pr_vs_threshold.png)
![./figs/deep_dive_logit_precision_recall_at_k.png](deep_dive_logit_precision_recall_at_k.png)
![./figs/deep_dive_logit_score_dist.png](deep_dive_logit_score_dist.png)
