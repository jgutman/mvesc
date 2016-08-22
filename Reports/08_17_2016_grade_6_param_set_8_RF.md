# Report for 08 17 2016 grade 6 param set 8 RF
fourth pass for grade 6

### Model Options
* label used: definite_plus_ogt
* prediction grade: 6
* validation cohorts: 2008
* test cohorts: 2009
	 * 88 positive examples, 930 negative examples
* train cohorts: 2007
	 * 88 postive examples, 778 negative examples
* parameter choices
	 * min_samples_split = 10
	 * max_features = sqrt
	 * n_estimators = 1000
	 * max_depth = 20
	 * criterion = gini
* cross-validation scores: k fold, with 5 folds
	 * custom_precision_5_15 score: 0.24
	 * custom_recall_5_15 score: 0.23
* imputation strategy: median plus dummies
* scaling strategy: robust

### Features Used
* absence
	 * absence_wkd_4_gr_5
	 * absence_consec_gr_5
	 * tardy_wkd_3_gr_5
	 * tardy_consec_gr_5
	 * absence_wkd_1_gr_5
	 * tardy_wkd_1_gr_5
	 * tardy_gr_5
	 * absence_wkd_5_gr_5
	 * tardy_unexcused_gr_5
	 * absence_gr_5
	 * absence_unexcused_gr_5
	 * tardy_wkd_5_gr_5
	 * tardy_wkd_2_gr_5
	 * absence_wkd_2_gr_5
	 * tardy_wkd_4_gr_5
	 * medical_gr_5
	 * absence_wkd_3_gr_5
* intervention
	 * placement_gr_5
	 * extracurr_program_gr_5
	 * titlei_gr_5
	 * academic_inv_gr_5
	 * academic_intracurr_gr_5
	 * school_program_gr_5
	 * vocational_gr_5
	 * atheletics_gr_5
	 * post_secondary_gr_5
	 * spec_instruc_gr_5
* oaa_normalized
	 * read_normalized_gr_3
	 * math_normalized_gr_4
	 * math_normalized_gr_5
	 * science_normalized_gr_5
	 * read_normalized_gr_4
	 * socstudies_normalized_gr_5
	 * read_normalized_gr_5
	 * math_normalized_gr_3
* snapshots
	 * limited_english_gr_5
	 * disadvantagement_gr_5
	 * special_ed_gr_5
	 * oss_gr_5
	 * section_504_plan_gr_5
	 * iss_gr_5
	 * discipline_incidents_gr_5
	 * status_gr_5
	 * district_gr_5
	 * disability_gr_5
	 * gifted_gr_5
* demographics
	 * ethnicity
	 * gender
* grades
	 * future_prep_gpa_gr_5
	 * num_humanities_classes_gr_5
	 * num_pf_classes_gr_5
	 * num_future_prep_classes_gr_5
	 * health_gpa_gr_5
	 * num_interventions_classes_gr_5
	 * num_language_classes_gr_5
	 * num_stem_classes_gr_5
	 * percent_passed_pf_classes_gr_5
	 * gpa_district_gr_5
	 * art_gpa_gr_5
	 * num_art_classes_gr_5
	 * num_health_classes_gr_5
	 * interventions_gpa_gr_5
	 * humanities_gpa_gr_5
	 * gpa_gr_5
	 * language_gpa_gr_5
	 * stem_gpa_gr_5
* mobility
	 * n_districts_to_gr_5
	 * n_addresses_to_gr_5
	 * avg_district_change_to_gr_5
	 * street_transition_in_gr_5
	 * n_records_to_gr_5
	 * mid_year_withdraw_gr_5
	 * n_cities_to_gr_5
	 * avg_address_change_to_gr_5
	 * city_transition_in_gr_5
	 * avg_city_change_to_gr_5
	 * district_transition_in_gr_5

### Performance Metrics
on average, model run in 1.29 seconds (16 times) <br/><br/>metrics on the test set: <br/>precision on top 15%: 0.3289 <br/>precision on top 10%: 0.3168 <br/>precision on top 5%: 0.32 <br/>recall on top 15%: 0.5682 <br/>recall on top 10%: 0.3636 <br/>recall on top 5%: 0.1818 <br/><br/>metrics on the validation set: <br/>precision on top 15%: 0.3265 <br/>precision on top 10%: 0.3776 <br/>precision on top 5%: 0.3673 <br/>recall on top 15%: 0.4486 <br/>recall on top 10%: 0.3458 <br/>recall on top 5%: 0.1682 <br/>AUC value is: 0.788 <br/>top features: socstudies_normalized_gr_5 (0.1), read_normalized_gr_5 (0.08), science_normalized_gr_5 (0.078)
![08_17_2016_grade_6_param_set_8_RF_pr.png](figs/08_17_2016_grade_6_param_set_8_RF_pr.png)
![08_17_2016_grade_6_param_set_8_RF_confusion_mat_0.3.png](figs/08_17_2016_grade_6_param_set_8_RF_confusion_mat_0.3.png)
![08_17_2016_grade_6_param_set_8_RF_precision_recall_at_k.png](figs/08_17_2016_grade_6_param_set_8_RF_precision_recall_at_k.png)
![08_17_2016_grade_6_param_set_8_RF_score_dist.png](figs/08_17_2016_grade_6_param_set_8_RF_score_dist.png)
