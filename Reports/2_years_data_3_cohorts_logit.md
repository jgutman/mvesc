# Report for 2 years data 3 cohorts logit
testing yaml creation

### Model Options
* label used: definite
* initial cohort grade: 9
* test cohorts: 2011, 2012
	 * 239 positive examples, 3918 negative examples
* train cohorts: 2008, 2009, 2010
	 * 96 postive examples, 3046 negative examples
* cross-validation scheme: leave cohort out
	 * searching penalty in l1
	 * chose penalty = l1
	 * searching C in 1.0
	 * chose C = 1.0
	 * using custom_precision_10
* imputation strategy: median plus dummies
* scaling strategy: robust

### Features Used
* grades
	 * num_art_classes_gr_7
	 * health_gpa_gr_7
	 * language_gpa_gr_7
	 * num_interventions_classes_gr_7
	 * health_gpa_gr_8
	 * interventions_gpa_gr_7
	 * humanities_gpa_gr_7
	 * num_art_classes_gr_8
	 * stem_gpa_gr_7
	 * num_humanities_classes_gr_8
	 * num_health_classes_gr_7
	 * num_interventions_classes_gr_8
	 * language_gpa_gr_8
	 * future_prep_gpa_gr_7
	 * num_stem_classes_gr_7
	 * num_humanities_classes_gr_7
	 * percent_passed_pf_classes_gr_7
	 * stem_gpa_gr_8
	 * num_language_classes_gr_7
	 * humanities_gpa_gr_8
	 * art_gpa_gr_8
	 * num_pf_classes_gr_7
	 * interventions_gpa_gr_8
	 * art_gpa_gr_7
	 * num_future_prep_classes_gr_7
	 * num_health_classes_gr_8
	 * percent_passed_pf_classes_gr_8
	 * gpa_district_gr_7
	 * future_prep_gpa_gr_8
	 * num_stem_classes_gr_8
	 * num_future_prep_classes_gr_8
	 * gpa_district_gr_8
	 * num_pf_classes_gr_8
	 * num_language_classes_gr_8
* mobility
	 * avg_address_change_to_gr_7
	 * n_records_to_gr_8
	 * n_records_to_gr_7
	 * mid_year_withdraw_gr_8
	 * avg_city_change_to_gr_8
	 * avg_district_change_to_gr_8
	 * n_cities_to_gr_8
	 * avg_district_change_to_gr_7
	 * city_transition_in_gr_7
	 * district_transition_in_gr_8
	 * city_transition_in_gr_8
	 * street_transition_in_gr_8
	 * district_transition_in_gr_7
	 * n_addresses_to_gr_8
	 * n_districts_to_gr_7
	 * mid_year_withdraw_gr_7
	 * avg_city_change_to_gr_7
	 * avg_address_change_to_gr_8
	 * street_transition_in_gr_7
	 * n_addresses_to_gr_7
	 * n_cities_to_gr_7
	 * n_districts_to_gr_8
* demographics
	 * ethnicity
	 * gender

### Performance Metrics
on average, model run in 2.08 seconds (1 times) <br/>precision on top 15%: 0.0912 <br/>precision on top 10%: 0.07547 <br/>precision on top 5%: 0.1058 <br/>recall on top 15%: 0.2385 <br/>recall on top 10%: 0.1506 <br/>recall on top 5%: 0.09205 <br/>AUC value is: 0.6522 <br/>top features: mid_year_withdraw_gr_8_nan (-1.5), num_interventions_classes_gr_8_isnull (1.1), percent_passed_pf_classes_gr_7_isnull (1.0)
![2_years_data_3_cohorts_logit_pr_vs_threshold.png](figs/2_years_data_3_cohorts_logit_pr_vs_threshold.png)
![2_years_data_3_cohorts_logit_confusion_mat_0.3.png](figs/2_years_data_3_cohorts_logit_confusion_mat_0.3.png)
![2_years_data_3_cohorts_logit_score_dist.png](figs/2_years_data_3_cohorts_logit_score_dist.png)
![2_years_data_3_cohorts_logit_precision_recall_at_k.png](figs/2_years_data_3_cohorts_logit_precision_recall_at_k.png)
