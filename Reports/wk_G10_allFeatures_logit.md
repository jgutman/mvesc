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
	 * searching C in 1e-05, 0.0001, 0.001, 0.01, 0.1, 1.0, 10.0, 100, 1000
	 * chose C = 1e-05
	 * searching penalty in l1, l2
	 * chose penalty = l1
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
on average, model run in 0.37 seconds (18 times) <br/>precision on top 15%: 0.06371 <br/>precision on top 10%: 0.06371 <br/>precision on top 5%: 0.06371 <br/>recall on top 15%: 1.0 <br/>recall on top 10%: 1.0 <br/>recall on top 5%: 1.0 <br/>AUC value is: 0.5 <br/>top features: district_transition_in_gr_9 (0.0), city_transition_in_gr_9 (0.0), street_transition_in_gr_9 (0.0)
![wk_G10_allFeatures_logit_precision_recall_at_k.png](figs/wk_G10_allFeatures_logit_precision_recall_at_k.png)
![wk_G10_allFeatures_logit_confusion_mat_0.3.png](figs/wk_G10_allFeatures_logit_confusion_mat_0.3.png)
![wk_G10_allFeatures_3_logit_confusion_mat_0.3.png](figs/wk_G10_allFeatures_3_logit_confusion_mat_0.3.png)
![wk_G10_allFeatures_logit_score_dist.png](figs/wk_G10_allFeatures_logit_score_dist.png)
![wk_G10_allFeatures_3_logit_score_dist.png](figs/wk_G10_allFeatures_3_logit_score_dist.png)
![wk_G10_allFeatures_3_logit_pr_vs_threshold.png](figs/wk_G10_allFeatures_3_logit_pr_vs_threshold.png)
![wk_G10_allFeatures_logit_pr_vs_threshold.png](figs/wk_G10_allFeatures_logit_pr_vs_threshold.png)
![wk_G10_allFeatures_3_logit_precision_recall_at_k.png](figs/wk_G10_allFeatures_3_logit_precision_recall_at_k.png)
