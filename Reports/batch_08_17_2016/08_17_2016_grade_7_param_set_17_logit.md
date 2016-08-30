# Report for 08 17 2016 grade 7 param set 17 logit
fourth pass for grade 7

### Model Options
* label used: definite_plus_ogt
* prediction grade: 7
* validation cohorts: 2009
* test cohorts: 2010
	 * 117 positive examples, 1036 negative examples
* train cohorts: 2008
	 * 89 postive examples, 808 negative examples
* parameter choices
	 * penalty = l2
	 * C = 0.1
* cross-validation scores: k fold, with 5 folds
	 * custom_precision_5_15 score: 0.23
	 * custom_recall_5_15 score: 0.25
* imputation strategy: median plus dummies
* scaling strategy: robust

### Features Used
* absence
	 * absence_consec_gr_5
	 * tardy_wkd_3_gr_5
	 * absence_unexcused_gr_5
	 * tardy_wkd_2_gr_6
	 * absence_wkd_1_gr_6
	 * tardy_gr_6
	 * tardy_wkd_3_gr_6
	 * tardy_wkd_2_gr_5
	 * tardy_wkd_5_gr_6
	 * absence_wkd_4_gr_6
	 * tardy_wkd_4_gr_5
	 * absence_wkd_1_gr_5
	 * tardy_wkd_1_gr_5
	 * tardy_unexcused_gr_6
	 * tardy_consec_gr_5
	 * absence_wkd_2_gr_5
	 * absence_unexcused_gr_6
	 * tardy_wkd_5_gr_5
	 * tardy_gr_5
	 * tardy_consec_gr_6
	 * tardy_unexcused_gr_5
	 * absence_consec_gr_6
	 * absence_wkd_2_gr_6
	 * absence_wkd_3_gr_6
	 * absence_wkd_5_gr_5
	 * medical_gr_5
	 * tardy_wkd_4_gr_6
	 * absence_wkd_3_gr_5
	 * absence_gr_6
	 * medical_gr_6
	 * absence_wkd_4_gr_5
	 * absence_gr_5
	 * absence_wkd_5_gr_6
	 * tardy_wkd_1_gr_6
* intervention
	 * extracurr_program_gr_6
	 * spec_instruc_gr_6
	 * academic_intracurr_gr_6
	 * spec_instruc_gr_5
	 * post_secondary_gr_5
	 * post_secondary_gr_6
	 * placement_gr_5
	 * vocational_gr_5
	 * school_program_gr_6
	 * titlei_gr_5
	 * atheletics_gr_6
	 * academic_inv_gr_5
	 * academic_intracurr_gr_5
	 * titlei_gr_6
	 * school_program_gr_5
	 * placement_gr_6
	 * extracurr_program_gr_5
	 * atheletics_gr_5
	 * academic_inv_gr_6
	 * vocational_gr_6
* grades
	 * gpa_gr_6
	 * num_humanities_classes_gr_5
	 * future_prep_gpa_gr_5
	 * stem_gpa_gr_5
	 * stem_gpa_gr_6
	 * humanities_gpa_gr_6
	 * num_health_classes_gr_5
	 * health_gpa_gr_5
	 * humanities_gpa_gr_5
	 * num_art_classes_gr_6
	 * art_gpa_gr_5
	 * num_health_classes_gr_6
	 * num_language_classes_gr_6
	 * gpa_district_gr_5
	 * health_gpa_gr_6
	 * language_gpa_gr_6
	 * num_future_prep_classes_gr_6
	 * percent_passed_pf_classes_gr_5
	 * num_humanities_classes_gr_6
	 * num_stem_classes_gr_6
	 * language_gpa_gr_5
	 * interventions_gpa_gr_6
	 * num_future_prep_classes_gr_5
	 * gpa_gr_5
	 * future_prep_gpa_gr_6
	 * gpa_district_gr_6
	 * art_gpa_gr_6
	 * num_art_classes_gr_5
	 * num_pf_classes_gr_5
	 * percent_passed_pf_classes_gr_6
	 * num_interventions_classes_gr_5
	 * num_stem_classes_gr_5
	 * interventions_gpa_gr_5
	 * num_interventions_classes_gr_6
	 * num_language_classes_gr_5
	 * num_pf_classes_gr_6
* snapshots
	 * limited_english_gr_6
	 * disadvantagement_gr_5
	 * gifted_gr_5
	 * disability_gr_5
	 * status_gr_6
	 * oss_gr_5
	 * district_gr_6
	 * district_gr_5
	 * disadvantagement_gr_6
	 * oss_gr_6
	 * section_504_plan_gr_6
	 * section_504_plan_gr_5
	 * discipline_incidents_gr_5
	 * iss_gr_6
	 * special_ed_gr_5
	 * gifted_gr_6
	 * special_ed_gr_6
	 * disability_gr_6
	 * iss_gr_5
	 * limited_english_gr_5
	 * discipline_incidents_gr_6
	 * status_gr_5
* demographics
	 * ethnicity
	 * gender
* oaa_normalized
	 * science_normalized_gr_5
	 * math_normalized_gr_3
	 * read_normalized_gr_3
	 * math_normalized_gr_4
	 * read_normalized_gr_4
	 * socstudies_normalized_gr_5
	 * math_normalized_gr_5
	 * read_normalized_gr_6
	 * math_normalized_gr_6
	 * read_normalized_gr_5
* mobility
	 * n_addresses_to_gr_5
	 * n_districts_to_gr_6
	 * mid_year_withdraw_gr_5
	 * n_cities_to_gr_5
	 * n_records_to_gr_5
	 * district_transition_in_gr_6
	 * avg_address_change_to_gr_5
	 * avg_district_change_to_gr_6
	 * street_transition_in_gr_6
	 * n_addresses_to_gr_6
	 * district_transition_in_gr_5
	 * avg_city_change_to_gr_6
	 * avg_city_change_to_gr_5
	 * avg_address_change_to_gr_6
	 * n_records_to_gr_6
	 * mid_year_withdraw_gr_6
	 * street_transition_in_gr_5
	 * city_transition_in_gr_6
	 * n_cities_to_gr_6
	 * avg_district_change_to_gr_5
	 * n_districts_to_gr_5
	 * city_transition_in_gr_5

### Performance Metrics
on average, model run in 0.04 seconds (12 times) <br/><br/>metrics on the test set: <br/>precision on top 15%: 0.3198 <br/>precision on top 10%: 0.3478 <br/>precision on top 5%: 0.4211 <br/>recall on top 15%: 0.4701 <br/>recall on top 10%: 0.3419 <br/>recall on top 5%: 0.2051 <br/><br/>metrics on the validation set: <br/>precision on top 15%: 0.3 <br/>precision on top 10%: 0.35 <br/>precision on top 5%: 0.44 <br/>recall on top 15%: 0.4091 <br/>recall on top 10%: 0.3182 <br/>recall on top 5%: 0.2 <br/>AUC value is: 0.7873 <br/>top features: science_normalized_gr_5 (-0.51), disadvantagement_gr_6_none (-0.41), iss_gr_6 (-0.4)
![08_17_2016_grade_7_param_set_17_logit_precision_recall_at_k.png](figs/08_17_2016_grade_7_param_set_17_logit_precision_recall_at_k.png)
![08_17_2016_grade_7_param_set_17_logit_score_dist.png](figs/08_17_2016_grade_7_param_set_17_logit_score_dist.png)
![08_17_2016_grade_7_param_set_17_logit_confusion_mat_0.3.png](figs/08_17_2016_grade_7_param_set_17_logit_confusion_mat_0.3.png)
![08_17_2016_grade_7_param_set_17_logit_pr.png](figs/08_17_2016_grade_7_param_set_17_logit_pr.png)
