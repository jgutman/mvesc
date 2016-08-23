# Report for 2 years data 4 cohorts logit
testing yaml creation

### Model Options
* label used: definite
* initial cohort grade: 9
* test cohorts: 2011, 2012
	 * 239 positive examples, 3918 negative examples
* train cohorts: 2007, 2008, 2009, 2010
	 * 126 postive examples, 4067 negative examples
* cross-validation scheme: leave cohort out
	 * searching penalty in l1
	 * chose penalty = l1
	 * searching C in 1.0
	 * chose C = 1.0
	 * using custom_precision_10
* imputation strategy: median plus dummies
* scaling strategy: robust

### Features Used
* mobility
	 * avg_district_change_to_gr_8
	 * mid_year_withdraw_gr_9
	 * avg_city_change_to_gr_8
	 * avg_address_change_to_gr_8
	 * n_districts_to_gr_9
	 * n_cities_to_gr_9
	 * avg_address_change_to_gr_9
	 * district_transition_in_gr_9
	 * street_transition_in_gr_9
	 * n_cities_to_gr_8
	 * n_addresses_to_gr_9
	 * city_transition_in_gr_8
	 * avg_district_change_to_gr_9
	 * avg_city_change_to_gr_9
	 * mid_year_withdraw_gr_8
	 * n_addresses_to_gr_8
	 * n_districts_to_gr_8
	 * n_records_to_gr_9
	 * street_transition_in_gr_8
	 * city_transition_in_gr_9
	 * district_transition_in_gr_8
	 * n_records_to_gr_8
* grades
	 * num_art_classes_gr_8
	 * language_gpa_gr_9
	 * humanities_gpa_gr_9
	 * num_art_classes_gr_9
	 * num_health_classes_gr_8
	 * language_gpa_gr_8
	 * gpa_district_gr_9
	 * num_interventions_classes_gr_8
	 * num_language_classes_gr_8
	 * num_stem_classes_gr_8
	 * future_prep_gpa_gr_8
	 * health_gpa_gr_9
	 * art_gpa_gr_9
	 * humanities_gpa_gr_8
	 * future_prep_gpa_gr_9
	 * num_pf_classes_gr_8
	 * interventions_gpa_gr_9
	 * num_humanities_classes_gr_9
	 * health_gpa_gr_8
	 * stem_gpa_gr_9
	 * art_gpa_gr_8
	 * stem_gpa_gr_8
	 * percent_passed_pf_classes_gr_9
	 * gpa_district_gr_8
	 * interventions_gpa_gr_8
	 * num_language_classes_gr_9
	 * num_interventions_classes_gr_9
	 * num_humanities_classes_gr_8
	 * percent_passed_pf_classes_gr_8
	 * num_pf_classes_gr_9
	 * num_stem_classes_gr_9
	 * num_future_prep_classes_gr_8
	 * num_health_classes_gr_9
	 * num_future_prep_classes_gr_9
* demographics
	 * gender
	 * ethnicity

### Performance Metrics
on average, model run in 3.87 seconds (1 times) <br/>precision on top 15%: 0.1067 <br/>precision on top 10%: 0.1378 <br/>precision on top 5%: 0.1378 <br/>recall on top 15%: 0.2803 <br/>recall on top 10%: 0.2427 <br/>recall on top 5%: 0.2427 <br/>AUC value is: 0.7394 <br/>top features: humanities_gpa_gr_9_isnull (2.1), mid_year_withdraw_gr_8_nan (-1.7), gpa_district_gr_9 (-1.1)
![2_years_data_4_cohorts_logit_score_dist.png](figs/2_years_data_4_cohorts_logit_score_dist.png)
![2_years_data_4_cohorts_logit_precision_recall_at_k.png](figs/2_years_data_4_cohorts_logit_precision_recall_at_k.png)
![2_years_data_4_cohorts_logit_pr_vs_threshold.png](figs/2_years_data_4_cohorts_logit_pr_vs_threshold.png)
![2_years_data_4_cohorts_logit_confusion_mat_0.3.png](figs/2_years_data_4_cohorts_logit_confusion_mat_0.3.png)
