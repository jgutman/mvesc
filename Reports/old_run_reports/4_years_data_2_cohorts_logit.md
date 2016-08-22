# Report for 4 years data 2 cohorts logit
testing yaml creation

### Model Options
* label used: definite
* initial cohort grade: 9
* test cohorts: 2011, 2012
	 * 239 positive examples, 3918 negative examples
* train cohorts: 2009, 2010
	 * 65 postive examples, 2062 negative examples
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
	 * city_transition_in_gr_7
	 * district_transition_in_gr_7
	 * avg_district_change_to_gr_8
	 * street_transition_in_gr_7
	 * mid_year_withdraw_gr_9
	 * avg_address_change_to_gr_6
	 * avg_city_change_to_gr_8
	 * n_districts_to_gr_6
	 * avg_address_change_to_gr_8
	 * n_records_to_gr_7
	 * avg_city_change_to_gr_6
	 * n_records_to_gr_6
	 * n_districts_to_gr_9
	 * n_cities_to_gr_6
	 * n_cities_to_gr_9
	 * street_transition_in_gr_6
	 * city_transition_in_gr_6
	 * mid_year_withdraw_gr_6
	 * n_addresses_to_gr_6
	 * avg_address_change_to_gr_9
	 * district_transition_in_gr_9
	 * avg_city_change_to_gr_7
	 * street_transition_in_gr_9
	 * n_cities_to_gr_8
	 * n_cities_to_gr_7
	 * n_addresses_to_gr_9
	 * mid_year_withdraw_gr_7
	 * avg_district_change_to_gr_7
	 * district_transition_in_gr_6
	 * city_transition_in_gr_8
	 * avg_district_change_to_gr_9
	 * avg_city_change_to_gr_9
	 * avg_address_change_to_gr_7
	 * mid_year_withdraw_gr_8
	 * n_addresses_to_gr_8
	 * n_districts_to_gr_7
	 * avg_district_change_to_gr_6
	 * n_districts_to_gr_8
	 * n_records_to_gr_9
	 * street_transition_in_gr_8
	 * city_transition_in_gr_9
	 * n_addresses_to_gr_7
	 * n_records_to_gr_8
	 * district_transition_in_gr_8
* grades
	 * num_art_classes_gr_8
	 * num_interventions_classes_gr_6
	 * language_gpa_gr_9
	 * humanities_gpa_gr_9
	 * num_art_classes_gr_9
	 * num_humanities_classes_gr_6
	 * interventions_gpa_gr_7
	 * num_language_classes_gr_6
	 * num_humanities_classes_gr_7
	 * num_art_classes_gr_7
	 * num_future_prep_classes_gr_7
	 * num_stem_classes_gr_7
	 * num_health_classes_gr_8
	 * future_prep_gpa_gr_7
	 * language_gpa_gr_8
	 * humanities_gpa_gr_7
	 * gpa_district_gr_9
	 * num_future_prep_classes_gr_6
	 * num_interventions_classes_gr_7
	 * num_interventions_classes_gr_8
	 * health_gpa_gr_7
	 * art_gpa_gr_6
	 * num_language_classes_gr_8
	 * num_pf_classes_gr_7
	 * num_stem_classes_gr_8
	 * gpa_district_gr_7
	 * future_prep_gpa_gr_8
	 * health_gpa_gr_9
	 * art_gpa_gr_9
	 * humanities_gpa_gr_8
	 * future_prep_gpa_gr_6
	 * future_prep_gpa_gr_9
	 * num_pf_classes_gr_8
	 * humanities_gpa_gr_6
	 * interventions_gpa_gr_9
	 * stem_gpa_gr_7
	 * health_gpa_gr_8
	 * stem_gpa_gr_9
	 * art_gpa_gr_8
	 * stem_gpa_gr_8
	 * num_humanities_classes_gr_9
	 * percent_passed_pf_classes_gr_9
	 * gpa_district_gr_8
	 * num_pf_classes_gr_6
	 * interventions_gpa_gr_8
	 * health_gpa_gr_6
	 * num_art_classes_gr_6
	 * stem_gpa_gr_6
	 * num_language_classes_gr_9
	 * num_interventions_classes_gr_9
	 * art_gpa_gr_7
	 * percent_passed_pf_classes_gr_6
	 * language_gpa_gr_7
	 * num_humanities_classes_gr_8
	 * percent_passed_pf_classes_gr_7
	 * num_stem_classes_gr_6
	 * percent_passed_pf_classes_gr_8
	 * num_health_classes_gr_6
	 * gpa_district_gr_6
	 * num_language_classes_gr_7
	 * num_health_classes_gr_7
	 * num_pf_classes_gr_9
	 * num_stem_classes_gr_9
	 * num_future_prep_classes_gr_8
	 * num_health_classes_gr_9
	 * num_future_prep_classes_gr_9
	 * interventions_gpa_gr_6
	 * language_gpa_gr_6
* demographics
	 * gender
	 * ethnicity

### Performance Metrics
on average, model run in 0.93 seconds (1 times) <br/>precision on top 15%: 0.1052 <br/>precision on top 10%: 0.1707 <br/>precision on top 5%: 0.226 <br/>recall on top 15%: 0.4142 <br/>recall on top 10%: 0.2971 <br/>recall on top 5%: 0.1967 <br/>AUC value is: 0.7178 <br/>top features: n_districts_to_gr_6 (-3.1), humanities_gpa_gr_9_isnull (1.4), num_health_classes_gr_6 (-1.1)
![4_years_data_2_cohorts_logit_pr_vs_threshold.png](figs/4_years_data_2_cohorts_logit_pr_vs_threshold.png)
![4_years_data_2_cohorts_logit_confusion_mat_0.3.png](figs/4_years_data_2_cohorts_logit_confusion_mat_0.3.png)
![4_years_data_2_cohorts_logit_score_dist.png](figs/4_years_data_2_cohorts_logit_score_dist.png)
![4_years_data_2_cohorts_logit_precision_recall_at_k.png](figs/4_years_data_2_cohorts_logit_precision_recall_at_k.png)
