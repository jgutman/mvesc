# Report for 1 years data 4 cohorts logit
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
* grades
	 * num_art_classes_gr_8
	 * num_health_classes_gr_8
	 * percent_passed_pf_classes_gr_8
	 * future_prep_gpa_gr_8
	 * num_humanities_classes_gr_8
	 * num_stem_classes_gr_8
	 * num_future_prep_classes_gr_8
	 * gpa_district_gr_8
	 * health_gpa_gr_8
	 * num_pf_classes_gr_8
	 * num_interventions_classes_gr_8
	 * stem_gpa_gr_8
	 * art_gpa_gr_8
	 * humanities_gpa_gr_8
	 * language_gpa_gr_8
	 * num_language_classes_gr_8
	 * interventions_gpa_gr_8
* mobility
	 * n_records_to_gr_8
	 * street_transition_in_gr_8
	 * mid_year_withdraw_gr_8
	 * avg_city_change_to_gr_8
	 * district_transition_in_gr_8
	 * avg_district_change_to_gr_8
	 * avg_address_change_to_gr_8
	 * n_addresses_to_gr_8
	 * n_cities_to_gr_8
	 * city_transition_in_gr_8
	 * n_districts_to_gr_8
* demographics
	 * ethnicity
	 * gender

### Performance Metrics
on average, model run in 1.12 seconds (1 times) <br/>precision on top 15%: 0.09914 <br/>precision on top 10%: 0.09814 <br/>precision on top 5%: 0.1538 <br/>recall on top 15%: 0.2887 <br/>recall on top 10%: 0.2427 <br/>recall on top 5%: 0.1339 <br/>AUC value is: 0.6862 <br/>top features: mid_year_withdraw_gr_8_nan (-1.6), health_gpa_gr_8_isnull (1.2), gpa_district_gr_8 (-0.87)
![1_years_data_4_cohorts_logit_precision_recall_at_k.png](figs/1_years_data_4_cohorts_logit_precision_recall_at_k.png)
![1_years_data_4_cohorts_logit_pr_vs_threshold.png](figs/1_years_data_4_cohorts_logit_pr_vs_threshold.png)
![1_years_data_4_cohorts_logit_confusion_mat_0.3.png](figs/1_years_data_4_cohorts_logit_confusion_mat_0.3.png)
![1_years_data_4_cohorts_logit_score_dist.png](figs/1_years_data_4_cohorts_logit_score_dist.png)
