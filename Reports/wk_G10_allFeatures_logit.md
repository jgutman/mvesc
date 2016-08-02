# Report for wk G10 allFeatures logit
weekly update Grade 10 model (xc)

### Model Options
* label used: definite
* initial cohort grade: 9
* test cohorts: 2011
	 * 128 positive examples, 1881 negative examples
* train cohorts: 2008, 2009, 2010
	 * 96 postive examples, 3046 negative examples
* cross-validation scheme: leave cohort out
	 * searching penalty in l1, l2
	 * chose penalty = l1
	 * searching C in 0.001, 0.01, 0.1, 1.0, 10.0, 100, 1000
	 * chose C = 0.001
	 * using custom_precision_10
* imputation strategy: median plus dummies
* scaling strategy: robust

### Features Used
* grades
	 * gpa_gr_9
	 * gpa_gr_8
* oaa_normalized
	 * eighth_science_normalized
	 * eighth_read_normalized
	 * eighth_math_normalized
* mobility
	 * mid_year_withdraw_gr_9
	 * mid_year_withdraw_gr_8
	 * street_transition_in_gr_8
	 * district_transition_in_gr_8
	 * city_transition_in_gr_8
	 * n_addresses_to_gr_9
	 * street_transition_in_gr_9
	 * district_transition_in_gr_9
	 * avg_address_change_to_gr_8
	 * n_districts_to_gr_9
	 * avg_city_change_to_gr_8
	 * avg_district_change_to_gr_8
	 * n_districts_to_gr_8
	 * avg_address_change_to_gr_9
	 * n_records_to_gr_9
	 * n_cities_to_gr_9
	 * avg_district_change_to_gr_9
	 * city_transition_in_gr_9
	 * avg_city_change_to_gr_9
	 * n_records_to_gr_8
	 * n_addresses_to_gr_8
	 * n_cities_to_gr_8
* snapshots
	 * iss_gr_8
	 * limited_english_gr_8
	 * discipline_incidents_gr_8
	 * limited_english_gr_9
	 * days_absent_gr_8
	 * days_absent_unexcused_gr_9
	 * disadvantagement_gr_9
	 * special_ed_gr_8
	 * oss_gr_8
	 * iss_gr_9
	 * discipline_incidents_gr_9
	 * days_absent_unexcused_gr_8
	 * disadvantagement_gr_8
	 * district_gr_9
	 * gifted_gr_9
	 * disability_gr_9
	 * days_absent_gr_9
	 * district_gr_8
	 * disability_gr_8
	 * special_ed_gr_9
	 * oss_gr_9
	 * gifted_gr_8
* demographics
	 * ethnicity
	 * gender

### Performance Metrics
on average, model run in 0.64 seconds (14 times) <br/>precision on top 15%: 0.06208 <br/>precision on top 10%: 0.06208 <br/>precision on top 5%: 0.06208 <br/>recall on top 15%: 0.9375 <br/>recall on top 10%: 0.9375 <br/>recall on top 5%: 0.9375 <br/>AUC value is: 0.4869 <br/>top features: mid_year_withdraw_gr_9_True (0.0), mid_year_withdraw_gr_9_nan (0.0), mid_year_withdraw_gr_8_True (0.0)
![wk_G10_allFeatures_logit_precision_recall_at_k.png](figs/wk_G10_allFeatures_logit_precision_recall_at_k.png)
![wk_G10_allFeatures_logit_confusion_mat_0.3.png](figs/wk_G10_allFeatures_logit_confusion_mat_0.3.png)
![wk_G10_allFeatures_3_logit_confusion_mat_0.3.png](figs/wk_G10_allFeatures_3_logit_confusion_mat_0.3.png)
![wk_G10_allFeatures_logit_score_dist.png](figs/wk_G10_allFeatures_logit_score_dist.png)
![wk_G10_allFeatures_3_logit_score_dist.png](figs/wk_G10_allFeatures_3_logit_score_dist.png)
![wk_G10_allFeatures_3_logit_pr_vs_threshold.png](figs/wk_G10_allFeatures_3_logit_pr_vs_threshold.png)
![wk_G10_allFeatures_logit_pr_vs_threshold.png](figs/wk_G10_allFeatures_logit_pr_vs_threshold.png)
![wk_G10_allFeatures_3_logit_precision_recall_at_k.png](figs/wk_G10_allFeatures_3_logit_precision_recall_at_k.png)
