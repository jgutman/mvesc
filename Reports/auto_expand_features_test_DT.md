# Report for auto expand features test DT
expand features and grade range

### Model Options
* label used: definite
* initial cohort grade: 9
* test cohorts: 2011
	 * 128 positive examples, 1881 negative examples
* train cohorts: 2009, 2010
	 * 65 postive examples, 2062 negative examples
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
	 * n_districts_to_gr_9
	 * n_districts_to_gr_8
	 * n_addresses_to_gr_8
	 * n_addresses_to_gr_9
	 * n_cities_to_gr_8
	 * n_cities_to_gr_9
* grades
	 * language_gpa_gr_9
	 * num_stem_classes_gr_8
	 * num_humanities_classes_gr_9
	 * humanities_gpa_gr_8
	 * gpa_gr_9
	 * stem_gpa_gr_8
	 * num_humanities_classes_gr_8
	 * stem_gpa_gr_9
	 * num_language_classes_gr_8
	 * gpa_gr_8
	 * humanities_gpa_gr_9
	 * num_stem_classes_gr_9
	 * language_gpa_gr_8
	 * num_language_classes_gr_9
* snapshots
	 * days_absent_gr_8
	 * special_ed_gr_9
	 * disadvantagement_gr_8
	 * disability_gr_9
	 * limited_english_gr_8
	 * status_gr_8
	 * special_ed_gr_8
	 * limited_english_gr_9
	 * gifted_gr_8
	 * iss_gr_8
	 * disadvantagement_gr_9
	 * district_gr_9
	 * gifted_gr_9
	 * days_absent_gr_9
	 * oss_gr_9
	 * iss_gr_9
	 * days_absent_unexcused_gr_8
	 * status_gr_9
	 * discipline_incidents_gr_8
	 * discipline_incidents_gr_9
	 * oss_gr_8
	 * district_gr_8
	 * days_absent_unexcused_gr_9
	 * disability_gr_8
* demographics
	 * ethnicity
	 * gender

### Performance Metrics
on average, model run in 0.15 seconds (1 times) <br/>precision on top 10%: 0.0938 <br/>precision on top 5%: 0.0938 <br/>top features: gpa_gr_9 (0.34), days_absent_gr_9 (0.16), language_gpa_gr_9_isnull (0.14)
![auto_expand_features_test_DT_precision_recall.png](auto_expand_features_test_DT_precision_recall.png)
![auto_expand_features_test_DT_pr_vs_threshold.png](auto_expand_features_test_DT_pr_vs_threshold.png)
![auto_expand_features_test_DT_precision_recall_at_k.png](auto_expand_features_test_DT_precision_recall_at_k.png)
![auto_expand_features_test_DT_score_dist.png](auto_expand_features_test_DT_score_dist.png)
![auto_expand_features_test_DT_confusion_mat_0.3.png](auto_expand_features_test_DT_confusion_mat_0.3.png)
![auto_expand_features_test_DT_confusion_mat_0.5.png](auto_expand_features_test_DT_confusion_mat_0.5.png)
