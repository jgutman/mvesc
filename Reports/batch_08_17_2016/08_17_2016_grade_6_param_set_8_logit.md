# Report for 08 17 2016 grade 6 param set 8 logit
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
	 * penalty = l1
	 * C = 1.0
* cross-validation scores: k fold, with 5 folds
	 * custom_precision_5_15 score: 0.2
	 * custom_recall_5_15 score: 0.21
* imputation strategy: median plus dummies
* scaling strategy: robust

### Features Used
* absence
	 * tardy_wkd_4_gr_5
	 * absence_wkd_2_gr_5
	 * tardy_wkd_1_gr_5
	 * absence_wkd_5_gr_5
	 * absence_gr_5
	 * medical_gr_5
	 * absence_wkd_1_gr_5
	 * absence_wkd_3_gr_5
	 * absence_wkd_4_gr_5
	 * tardy_unexcused_gr_5
	 * tardy_wkd_2_gr_5
	 * absence_unexcused_gr_5
	 * tardy_wkd_3_gr_5
	 * tardy_gr_5
	 * absence_consec_gr_5
	 * tardy_consec_gr_5
	 * tardy_wkd_5_gr_5
* intervention
	 * school_program_gr_5
	 * placement_gr_5
	 * academic_inv_gr_5
	 * extracurr_program_gr_5
	 * titlei_gr_5
	 * academic_intracurr_gr_5
	 * post_secondary_gr_5
	 * spec_instruc_gr_5
	 * vocational_gr_5
	 * atheletics_gr_5
* grades
	 * num_pf_classes_gr_5
	 * num_interventions_classes_gr_5
	 * num_humanities_classes_gr_5
	 * future_prep_gpa_gr_5
	 * num_health_classes_gr_5
	 * gpa_district_gr_5
	 * health_gpa_gr_5
	 * num_stem_classes_gr_5
	 * art_gpa_gr_5
	 * language_gpa_gr_5
	 * percent_passed_pf_classes_gr_5
	 * gpa_gr_5
	 * humanities_gpa_gr_5
	 * num_art_classes_gr_5
	 * stem_gpa_gr_5
	 * interventions_gpa_gr_5
	 * num_language_classes_gr_5
	 * num_future_prep_classes_gr_5
* snapshots
	 * disability_gr_5
	 * discipline_incidents_gr_5
	 * iss_gr_5
	 * limited_english_gr_5
	 * section_504_plan_gr_5
	 * status_gr_5
	 * district_gr_5
	 * oss_gr_5
	 * disadvantagement_gr_5
	 * special_ed_gr_5
	 * gifted_gr_5
* demographics
	 * ethnicity
	 * gender
* oaa_normalized
	 * math_normalized_gr_5
	 * socstudies_normalized_gr_5
	 * read_normalized_gr_4
	 * math_normalized_gr_4
	 * science_normalized_gr_5
	 * read_normalized_gr_3
	 * math_normalized_gr_3
	 * read_normalized_gr_5
* mobility
	 * district_transition_in_gr_5
	 * n_addresses_to_gr_5
	 * avg_address_change_to_gr_5
	 * avg_city_change_to_gr_5
	 * avg_district_change_to_gr_5
	 * n_cities_to_gr_5
	 * n_districts_to_gr_5
	 * mid_year_withdraw_gr_5
	 * city_transition_in_gr_5
	 * n_records_to_gr_5
	 * street_transition_in_gr_5

### Performance Metrics
on average, model run in 0.05 seconds (12 times) <br/><br/>metrics on the test set: <br/>precision on top 15%: 0.2763 <br/>precision on top 10%: 0.3267 <br/>precision on top 5%: 0.42 <br/>recall on top 15%: 0.4773 <br/>recall on top 10%: 0.375 <br/>recall on top 5%: 0.2386 <br/><br/>metrics on the validation set: <br/>precision on top 15%: 0.3129 <br/>precision on top 10%: 0.3469 <br/>precision on top 5%: 0.4694 <br/>recall on top 15%: 0.4299 <br/>recall on top 10%: 0.3178 <br/>recall on top 5%: 0.215 <br/>AUC value is: 0.7773 <br/>top features: n_cities_to_gr_5 (-1.4), humanities_gpa_gr_5 (-1.3), num_pf_classes_gr_5_isnull (0.82)
![08_17_2016_grade_6_param_set_8_logit_pr.png](figs/08_17_2016_grade_6_param_set_8_logit_pr.png)
![08_17_2016_grade_6_param_set_8_logit_score_dist.png](figs/08_17_2016_grade_6_param_set_8_logit_score_dist.png)
![08_17_2016_grade_6_param_set_8_logit_precision_recall_at_k.png](figs/08_17_2016_grade_6_param_set_8_logit_precision_recall_at_k.png)
![08_17_2016_grade_6_param_set_8_logit_confusion_mat_0.3.png](figs/08_17_2016_grade_6_param_set_8_logit_confusion_mat_0.3.png)
