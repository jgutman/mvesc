# Report for testing write to database logit
expand features and grade range

### Model Options
* label used: definite
* initial cohort grade: 9
* test cohorts: 2011
	 * 128 positive examples, 1881 negative examples
* train cohorts: 2009, 2010
	 * 65 postive examples, 2062 negative examples
* cross-validation scheme: leave cohort out
	 * searching C in 1.0
	 * chose C = 1.0
	 * searching penalty in l1
	 * chose penalty = l1
	 * using custom_recall_10
* imputation strategy: median plus dummies
* scaling strategy: robust

### Features Used
* demographics
	 * ethnicity
	 * gender
* mobility
	 * n_addresses_to_gr_9
	 * n_cities_to_gr_9
	 * n_districts_to_gr_9
	 * n_addresses_to_gr_8
	 * n_districts_to_gr_8
	 * n_cities_to_gr_8
* snapshots
	 * days_absent_unexcused_gr_9
	 * status_gr_9
	 * limited_english_gr_9
	 * days_absent_gr_8
	 * discipline_incidents_gr_8
	 * days_absent_unexcused_gr_8
	 * discipline_incidents_gr_9
	 * days_absent_gr_9
	 * iss_gr_8
	 * special_ed_gr_9
	 * gifted_gr_8
	 * disadvantagement_gr_9
	 * gifted_gr_9
	 * disability_gr_9
	 * oss_gr_8
	 * oss_gr_9
	 * disadvantagement_gr_8
	 * district_gr_8
	 * limited_english_gr_8
	 * special_ed_gr_8
	 * iss_gr_9
	 * status_gr_8
	 * district_gr_9
	 * disability_gr_8
* grades
	 * gpa_gr_9
	 * gpa_gr_8

### Performance Metrics
on average, model run in 0.24 seconds (1 times) <br/>precision on top 10%: 0.224 <br/>precision on top 5%: 0.297 <br/>top features: status_gr_9_esc (4.4), status_gr_9_inactive (1.4), district_gr_8_Franklin (-1.4)
![testing_write_to_database_logit_precision_recall_at_k.png](testing_write_to_database_logit_precision_recall_at_k.png)
![testing_write_to_database_logit_score_dist.png](testing_write_to_database_logit_score_dist.png)
![testing_write_to_database_logit_confusion_mat_0.3.png](testing_write_to_database_logit_confusion_mat_0.3.png)
![testing_write_to_database_logit_pr.png](testing_write_to_database_logit_pr.png)
