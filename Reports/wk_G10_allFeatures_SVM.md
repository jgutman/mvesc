# Report for wk G10 allFeatures SVM
weekly update Grade 10 model (xc)

### Model Options
* label used: definite
* initial cohort grade: 9
* test cohorts: 2011
	 * 128 positive examples, 1881 negative examples
* train cohorts: 2008, 2009, 2010
	 * 96 postive examples, 3046 negative examples
* cross-validation scheme: leave cohort out
	 * searching C in 0.0001, 0.001, 0.01, 0.1, 1, 10
	 * chose C = 0.0001
	 * searching kernel in linear
	 * chose kernel = linear
	 * using custom_precision_10
* imputation strategy: median plus dummies
* scaling strategy: robust

### Features Used
* grades
	 * gpa_gr_9
* mobility
	 * district_transition_in_gr_9
	 * mid_year_withdraw_gr_9
	 * n_addresses_to_gr_9
	 * n_cities_to_gr_9
	 * avg_address_change_to_gr_9
	 * city_transition_in_gr_9
	 * street_transition_in_gr_9
	 * avg_city_change_to_gr_9
	 * n_districts_to_gr_9
	 * n_records_to_gr_9
	 * avg_district_change_to_gr_9
* snapshots
	 * disadvantagement_gr_9
	 * special_ed_gr_9
	 * status_gr_9
	 * days_absent_gr_9
	 * discipline_incidents_gr_9
	 * gifted_gr_9
	 * limited_english_gr_9
	 * iss_gr_9
	 * district_gr_9
	 * oss_gr_9
	 * days_absent_unexcused_gr_9
	 * disability_gr_9
* oaa_normalized
	 * eighth_math_normalized
	 * eighth_read_normalized
	 * eighth_science_normalized
* demographics
	 * ethnicity
	 * gender

### Performance Metrics
on average, model run in 5.85 seconds (6 times) <br/>precision on top 15%: 0.1556 <br/>precision on top 10%: 0.1675 <br/>precision on top 5%: 0.2475 <br/>recall on top 15%: 0.3672 <br/>recall on top 10%: 0.2656 <br/>recall on top 5%: 0.1953 <br/>AUC value is: 0.669 <br/>top features: status_gr_9_esc (0.0002), mid_year_withdraw_gr_9_True (0.00015), disability_gr_9_other major (0.0001)
![wk_G10_allFeatures_3_SVM_score_dist.png](figs/wk_G10_allFeatures_3_SVM_score_dist.png)
![wk_G10_allFeatures_3_SVM_pr_vs_threshold.png](figs/wk_G10_allFeatures_3_SVM_pr_vs_threshold.png)
![wk_G10_allFeatures_SVM_precision_recall_at_k.png](figs/wk_G10_allFeatures_SVM_precision_recall_at_k.png)
![wk_G10_allFeatures_SVM_pr_vs_threshold.png](figs/wk_G10_allFeatures_SVM_pr_vs_threshold.png)
![wk_G10_allFeatures_SVM_score_dist.png](figs/wk_G10_allFeatures_SVM_score_dist.png)
![wk_G10_allFeatures_3_SVM_precision_recall_at_k.png](figs/wk_G10_allFeatures_3_SVM_precision_recall_at_k.png)
![wk_G10_allFeatures_SVM_confusion_mat_0.3.png](figs/wk_G10_allFeatures_SVM_confusion_mat_0.3.png)
![wk_G10_allFeatures_3_SVM_confusion_mat_0.3.png](figs/wk_G10_allFeatures_3_SVM_confusion_mat_0.3.png)
