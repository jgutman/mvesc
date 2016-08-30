# Report for four years ninth DT
expand features and grade range

### Model Options
* label used: definite
* initial cohort grade: 9
* test cohorts: 2011
	 * 128 positive examples, 1881 negative examples
* train cohorts: 2009, 2010
	 * 65 postive examples, 2062 negative examples
* cross-validation scheme: leave cohort out
	 * searching criterion in entropy
	 * chose criterion = entropy
	 * searching max_depth in 5
	 * chose max_depth = 5
	 * using custom_recall_10
* imputation strategy: median plus dummies
* scaling strategy: robust

### Features Used
* grades
	 * gpa_gr_8
	 * gpa_gr_6
	 * gpa_gr_7
	 * gpa_gr_9
* snapshots
	 * iss_gr_7
	 * disadvantagement_gr_9
	 * oss_gr_7
	 * special_ed_gr_6
	 * iss_gr_8
	 * discipline_incidents_gr_9
	 * status_gr_6
	 * limited_english_gr_8
	 * oss_gr_6
	 * days_absent_gr_9
	 * disability_gr_8
	 * days_absent_gr_6
	 * discipline_incidents_gr_8
	 * gifted_gr_9
	 * limited_english_gr_6
	 * disability_gr_6
	 * iss_gr_6
	 * gifted_gr_7
	 * disadvantagement_gr_6
	 * disadvantagement_gr_7
	 * discipline_incidents_gr_6
	 * district_gr_8
	 * days_absent_gr_7
	 * disability_gr_7
	 * oss_gr_8
	 * limited_english_gr_9
	 * special_ed_gr_9
	 * limited_english_gr_7
	 * district_gr_9
	 * district_gr_6
	 * discipline_incidents_gr_7
	 * status_gr_8
	 * days_absent_unexcused_gr_8
	 * status_gr_9
	 * disability_gr_9
	 * days_absent_unexcused_gr_9
	 * days_absent_unexcused_gr_6
	 * district_gr_7
	 * iss_gr_9
	 * oss_gr_9
	 * status_gr_7
	 * gifted_gr_6
	 * days_absent_unexcused_gr_7
	 * disadvantagement_gr_8
	 * gifted_gr_8
	 * special_ed_gr_8
	 * days_absent_gr_8
	 * special_ed_gr_7
* mobility
	 * n_districts_to_gr_6
	 * n_addresses_to_gr_6
	 * n_cities_to_gr_9
	 * n_cities_to_gr_7
	 * n_districts_to_gr_8
	 * n_addresses_to_gr_7
	 * n_districts_to_gr_7
	 * n_addresses_to_gr_8
	 * n_districts_to_gr_9
	 * n_cities_to_gr_8
	 * n_addresses_to_gr_9
	 * n_cities_to_gr_6
* demographics
	 * ethnicity
	 * gender

### Performance Metrics
on average, model run in 0.08 seconds (1 times) <br/>precision on top 10%: 0.0718 <br/>precision on top 5%: 0.0718 <br/>top features: gpa_gr_9 (0.32), gpa_gr_8 (0.094), gpa_gr_7 (0.087)
![four_years_ninth_DT_pr.png](four_years_ninth_DT_pr.png)
![four_years_ninth_DT_score_dist.png](four_years_ninth_DT_score_dist.png)
![four_years_ninth_DT_precision_recall_at_k.png](four_years_ninth_DT_precision_recall_at_k.png)
![four_years_ninth_DT_confusion_mat_0.3.png](four_years_ninth_DT_confusion_mat_0.3.png)
