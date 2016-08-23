# Report for 08 17 2016 grade 8 param set 16 RF
fourth pass for grade 8

### Model Options
* label used: definite_plus_ogt
* prediction grade: 8
* validation cohorts: 2010
* test cohorts: 2011
	 * 226 positive examples, 1801 negative examples
* train cohorts: 2007, 2008, 2009
	 * 278 postive examples, 2738 negative examples
* parameter choices
	 * min_samples_split = 3
	 * max_features = sqrt
	 * n_estimators = 1000
	 * max_depth = 20
	 * criterion = entropy
* cross-validation scores: k fold, with 5 folds
	 * custom_precision_5_15 score: 0.29
	 * custom_recall_5_15 score: 0.31
* imputation strategy: median plus dummies
* scaling strategy: robust

### Features Used
* absence
	 * tardy_wkd_1_gr_7
	 * tardy_wkd_2_gr_7
	 * tardy_wkd_4_gr_7
	 * tardy_wkd_3_gr_7
	 * absence_wkd_1_gr_7
	 * absence_unexcused_gr_7
	 * tardy_gr_7
	 * tardy_wkd_5_gr_7
	 * absence_consec_gr_7
	 * absence_wkd_2_gr_7
	 * tardy_unexcused_gr_7
	 * absence_wkd_5_gr_7
	 * tardy_consec_gr_7
	 * absence_gr_7
	 * absence_wkd_3_gr_7
	 * medical_gr_7
	 * absence_wkd_4_gr_7
* intervention
	 * academic_inv_gr_7
	 * spec_instruc_gr_7
	 * school_program_gr_7
	 * extracurr_program_gr_7
	 * placement_gr_7
	 * atheletics_gr_7
	 * academic_intracurr_gr_7
	 * titlei_gr_7
	 * vocational_gr_7
	 * post_secondary_gr_7
* oaa_normalized
	 * read_normalized_gr_3
	 * read_normalized_gr_4
	 * science_normalized_gr_5
	 * socstudies_normalized_gr_5
	 * math_normalized_gr_4
	 * math_normalized_gr_3
	 * read_normalized_gr_5
	 * math_normalized_gr_5
	 * math_normalized_gr_6
	 * read_normalized_gr_7
	 * math_normalized_gr_7
	 * read_normalized_gr_6
* snapshots
	 * special_ed_gr_7
	 * section_504_plan_gr_7
	 * district_gr_7
	 * oss_gr_7
	 * disadvantagement_gr_7
	 * limited_english_gr_7
	 * status_gr_7
	 * gifted_gr_7
	 * discipline_incidents_gr_7
	 * disability_gr_7
	 * iss_gr_7
* demographics
	 * ethnicity
	 * gender
* grades
	 * num_future_prep_classes_gr_7
	 * health_gpa_gr_7
	 * num_stem_classes_gr_7
	 * language_gpa_gr_7
	 * future_prep_gpa_gr_7
	 * num_pf_classes_gr_7
	 * stem_gpa_gr_7
	 * gpa_gr_7
	 * num_health_classes_gr_7
	 * num_interventions_classes_gr_7
	 * percent_passed_pf_classes_gr_7
	 * humanities_gpa_gr_7
	 * gpa_district_gr_7
	 * interventions_gpa_gr_7
	 * num_art_classes_gr_7
	 * num_humanities_classes_gr_7
	 * art_gpa_gr_7
	 * num_language_classes_gr_7
* mobility
	 * city_transition_in_gr_7
	 * n_records_to_gr_7
	 * street_transition_in_gr_7
	 * n_districts_to_gr_7
	 * avg_address_change_to_gr_7
	 * n_addresses_to_gr_7
	 * avg_city_change_to_gr_7
	 * mid_year_withdraw_gr_7
	 * n_cities_to_gr_7
	 * avg_district_change_to_gr_7
	 * district_transition_in_gr_7

### Performance Metrics
on average, model run in 3.42 seconds (16 times) <br/><br/>metrics on the test set: <br/>precision on top 15%: 0.3487 <br/>precision on top 10%: 0.3911 <br/>precision on top 5%: 0.4356 <br/>recall on top 15%: 0.469 <br/>recall on top 10%: 0.3496 <br/>recall on top 5%: 0.1947 <br/><br/>metrics on the validation set: <br/>precision on top 15%: 0.3511 <br/>precision on top 10%: 0.352 <br/>precision on top 5%: 0.4355 <br/>recall on top 15%: 0.4681 <br/>recall on top 10%: 0.3121 <br/>recall on top 5%: 0.1915 <br/>AUC value is: 0.8229 <br/>top features: gpa_gr_7 (0.066), gpa_district_gr_7 (0.064), humanities_gpa_gr_7 (0.06)
![08_17_2016_grade_8_param_set_16_RF_pr.png](figs/08_17_2016_grade_8_param_set_16_RF_pr.png)
![08_17_2016_grade_8_param_set_16_RF_score_dist.png](figs/08_17_2016_grade_8_param_set_16_RF_score_dist.png)
![08_17_2016_grade_8_param_set_16_RF_precision_recall_at_k.png](figs/08_17_2016_grade_8_param_set_16_RF_precision_recall_at_k.png)
![08_17_2016_grade_8_param_set_16_RF_confusion_mat_0.3.png](figs/08_17_2016_grade_8_param_set_16_RF_confusion_mat_0.3.png)
