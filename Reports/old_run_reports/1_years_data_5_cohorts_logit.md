# Report for 1 years data 5 cohorts logit
testing yaml creation

### Model Options
* label used: definite
* initial cohort grade: 9
* test cohorts: 2011, 2012
	 * 239 positive examples, 3918 negative examples
* train cohorts: 2006, 2007, 2008, 2009, 2010
	 * 144 postive examples, 5010 negative examples
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
	 * avg_address_change_to_gr_9
	 * district_transition_in_gr_9
	 * avg_district_change_to_gr_9
	 * mid_year_withdraw_gr_9
	 * street_transition_in_gr_9
	 * n_records_to_gr_9
	 * avg_city_change_to_gr_9
	 * city_transition_in_gr_9
	 * n_addresses_to_gr_9
	 * n_districts_to_gr_9
	 * n_cities_to_gr_9
* grades
	 * interventions_gpa_gr_9
	 * language_gpa_gr_9
	 * humanities_gpa_gr_9
	 * stem_gpa_gr_9
	 * num_humanities_classes_gr_9
	 * num_art_classes_gr_9
	 * percent_passed_pf_classes_gr_9
	 * num_pf_classes_gr_9
	 * num_stem_classes_gr_9
	 * num_language_classes_gr_9
	 * num_health_classes_gr_9
	 * num_interventions_classes_gr_9
	 * health_gpa_gr_9
	 * art_gpa_gr_9
	 * num_future_prep_classes_gr_9
	 * future_prep_gpa_gr_9
	 * gpa_district_gr_9
* demographics
	 * gender
	 * ethnicity

### Performance Metrics
on average, model run in 1.76 seconds (1 times) <br/>precision on top 15%: 0.1318 <br/>precision on top 10%: 0.1779 <br/>precision on top 5%: 0.2692 <br/>recall on top 15%: 0.4184 <br/>recall on top 10%: 0.3096 <br/>recall on top 5%: 0.2343 <br/>AUC value is: 0.7434 <br/>top features: humanities_gpa_gr_9_isnull (2.6), gpa_district_gr_9 (-1.3), city_transition_in_gr_9_True (1.0)
![1_years_data_5_cohorts_logit_pr_vs_threshold.png](figs/1_years_data_5_cohorts_logit_pr_vs_threshold.png)
![1_years_data_5_cohorts_logit_confusion_mat_0.3.png](figs/1_years_data_5_cohorts_logit_confusion_mat_0.3.png)
![1_years_data_5_cohorts_logit_score_dist.png](figs/1_years_data_5_cohorts_logit_score_dist.png)
![1_years_data_5_cohorts_logit_precision_recall_at_k.png](figs/1_years_data_5_cohorts_logit_precision_recall_at_k.png)
