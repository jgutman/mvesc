# Report for auto expand features test xc DT
expand features and grade range

### Model Options
* label used: definite
* initial cohort grade: 9
* test cohorts: 2011
	 * 107 positive examples, 1713 negative examples
* train cohorts: 2009, 2010
	 * 66 postive examples, 2062 negative examples
* cross-validation scheme: leave cohort out
	 * searching criterion in entropy
	 * chose criterion = entropy
	 * searching max_depth in 5
	 * chose max_depth = 5
	 * using custom_recall_10
* imputation strategy: median plus dummies
* scaling strategy: robust

### Features Used
* mobility
	 * n_cities_to_gr_9
	 * n_addresses_to_gr_9
	 * n_districts_to_gr_9
* snapshots
	 * disadvantagement_gr_9
	 * days_absent_unexcused_gr_9
	 * gifted_gr_9
	 * status_gr_9
	 * disability_gr_9
	 * district_gr_9
	 * special_ed_gr_9
	 * oss_gr_9
	 * limited_english_gr_9
	 * days_absent_gr_9
	 * discipline_incidents_gr_9
	 * iss_gr_9
* grades
	 * gpa_gr_9

### Performance Metrics
on average, model run in 0.04 seconds (1 times) <br/>precision on top 10%: 0.119 <br/>precision on top 5%: 0.119 <br/>top features: gpa_gr_9 (0.45), days_absent_gr_9 (0.24), district_gr_9_Coshocton (0.061)
![auto_expand_features_test_xc_DT_precision_recall_at_k.png](auto_expand_features_test_xc_DT_precision_recall_at_k.png)
![auto_expand_features_test_xc_DT_score_dist.png](auto_expand_features_test_xc_DT_score_dist.png)
![auto_expand_features_test_xc_DT_pr_vs_threshold.png](auto_expand_features_test_xc_DT_pr_vs_threshold.png)
![auto_expand_features_test_xc_DT_confusion_mat_0.3.png](auto_expand_features_test_xc_DT_confusion_mat_0.3.png)
