# Report for 08 17 2016 grade 10 param set 16 RF
fourth pass for grade 10

### Model Options
* label used: definite_plus_ogt
* prediction grade: 10
* validation cohorts: 2012
* test cohorts: 2013
	 * 252 positive examples, 2034 negative examples
* train cohorts: 2007, 2008, 2009, 2010, 2011
	 * 493 postive examples, 4952 negative examples
* parameter choices
	 * min_samples_split = 3
	 * max_features = sqrt
	 * n_estimators = 1000
	 * criterion = gini
	 * max_depth = 20
* cross-validation scores: k fold, with 5 folds
	 * custom_precision_5_15 score: 0.39
	 * custom_recall_5_15 score: 0.42
* imputation strategy: median plus dummies
* scaling strategy: robust

### Features Used
* absence
	 * tardy_unexcused_gr_9
	 * tardy_gr_9
	 * absence_consec_gr_9
	 * absence_gr_9
	 * medical_gr_9
	 * absence_wkd_5_gr_9
	 * absence_wkd_1_gr_9
	 * absence_wkd_4_gr_9
	 * absence_wkd_3_gr_9
	 * tardy_wkd_1_gr_9
	 * absence_unexcused_gr_9
	 * tardy_wkd_5_gr_9
	 * absence_wkd_2_gr_9
	 * tardy_wkd_3_gr_9
	 * tardy_wkd_4_gr_9
	 * tardy_consec_gr_9
	 * tardy_wkd_2_gr_9
* intervention
	 * post_secondary_gr_9
	 * titlei_gr_9
	 * extracurr_program_gr_9
	 * placement_gr_9
	 * academic_intracurr_gr_9
	 * atheletics_gr_9
	 * spec_instruc_gr_9
	 * academic_inv_gr_9
	 * school_program_gr_9
	 * vocational_gr_9
* oaa_normalized
	 * read_normalized_gr_6
	 * read_normalized_gr_3
	 * math_normalized_gr_6
	 * math_normalized_gr_7
	 * science_normalized_gr_5
	 * socstudies_normalized_gr_5
	 * read_normalized_gr_4
	 * read_normalized_gr_8
	 * math_normalized_gr_4
	 * read_normalized_gr_5
	 * math_normalized_gr_8
	 * science_normalized_gr_8
	 * math_normalized_gr_5
	 * read_normalized_gr_7
	 * math_normalized_gr_3
* snapshots
	 * status_gr_9
	 * discipline_incidents_gr_9
	 * special_ed_gr_9
	 * oss_gr_9
	 * iss_gr_9
	 * limited_english_gr_9
	 * gifted_gr_9
	 * disability_gr_9
	 * section_504_plan_gr_9
	 * disadvantagement_gr_9
	 * district_gr_9
* demographics
	 * ethnicity
	 * gender
* grades
	 * language_gpa_gr_9
	 * humanities_gpa_gr_9
	 * num_stem_classes_gr_9
	 * num_interventions_classes_gr_9
	 * num_future_prep_classes_gr_9
	 * gpa_district_gr_9
	 * num_art_classes_gr_9
	 * health_gpa_gr_9
	 * future_prep_gpa_gr_9
	 * art_gpa_gr_9
	 * num_humanities_classes_gr_9
	 * interventions_gpa_gr_9
	 * num_health_classes_gr_9
	 * num_language_classes_gr_9
	 * percent_passed_pf_classes_gr_9
	 * num_pf_classes_gr_9
	 * stem_gpa_gr_9
	 * gpa_gr_9
* mobility
	 * avg_address_change_to_gr_9
	 * mid_year_withdraw_gr_9
	 * avg_city_change_to_gr_9
	 * n_records_to_gr_9
	 * city_transition_in_gr_9
	 * n_districts_to_gr_9
	 * n_cities_to_gr_9
	 * avg_district_change_to_gr_9
	 * district_transition_in_gr_9
	 * n_addresses_to_gr_9
	 * street_transition_in_gr_9

### Performance Metrics
on average, model run in 3.08 seconds (16 times) <br/><br/>metrics on the test set: <br/>precision on top 15%: 0.4327 <br/>precision on top 10%: 0.5044 <br/>precision on top 5%: 0.5614 <br/>recall on top 15%: 0.5873 <br/>recall on top 10%: 0.4563 <br/>recall on top 5%: 0.254 <br/><br/>metrics on the validation set: <br/>precision on top 15%: 0.4089 <br/>precision on top 10%: 0.5 <br/>precision on top 5%: 0.5577 <br/>recall on top 15%: 0.5079 <br/>recall on top 10%: 0.4127 <br/>recall on top 5%: 0.2302 <br/>AUC value is: 0.8717 <br/>top features: humanities_gpa_gr_9 (0.057), gpa_district_gr_9 (0.057), gpa_gr_9 (0.056)
![08_17_2016_grade_10_param_set_16_RF_score_dist.png](figs/08_17_2016_grade_10_param_set_16_RF_score_dist.png)
![08_17_2016_grade_10_param_set_16_RF_pr.png](figs/08_17_2016_grade_10_param_set_16_RF_pr.png)
![08_17_2016_grade_10_param_set_16_RF_confusion_mat_0.3.png](figs/08_17_2016_grade_10_param_set_16_RF_confusion_mat_0.3.png)
![08_17_2016_grade_10_param_set_16_RF_precision_recall_at_k.png](figs/08_17_2016_grade_10_param_set_16_RF_precision_recall_at_k.png)
