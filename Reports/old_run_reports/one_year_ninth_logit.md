# Report for one year ninth logit
expand features and grade range

### Model Options
* label used: definite
* initial cohort grade: 9
* test cohorts: 2011
	 * 128 positive examples, 1881 negative examples
* train cohorts: 2009, 2010
	 * 65 postive examples, 2062 negative examples
* cross-validation scheme: leave cohort out
	 * searching penalty in l1
	 * chose penalty = l1
	 * searching C in 1.0
	 * chose C = 1.0
	 * using custom_recall_10
* imputation strategy: median plus dummies
* scaling strategy: robust

### Features Used
* grades
	 * gpa_gr_9
* mobility
	 * n_cities_to_gr_9
	 * n_districts_to_gr_9
	 * n_addresses_to_gr_9
* snapshots
	 * status_gr_9
	 * district_gr_9
	 * days_absent_unexcused_gr_9
	 * disability_gr_9
	 * iss_gr_9
	 * special_ed_gr_9
	 * disadvantagement_gr_9
	 * discipline_incidents_gr_9
	 * limited_english_gr_9
	 * gifted_gr_9
	 * days_absent_gr_9
	 * oss_gr_9
* demographics
	 * ethnicity
	 * gender

### Performance Metrics
on average, model run in 0.06 seconds (1 times) <br/>precision on top 10%: 0.244 <br/>precision on top 5%: 0.307 <br/>top features: status_gr_9_esc (3.9), status_gr_9_inactive (1.5), gpa_gr_9 (-1.4)
![one_year_ninth_logit_pr.png](one_year_ninth_logit_pr.png)
![one_year_ninth_logit_score_dist.png](one_year_ninth_logit_score_dist.png)
![one_year_ninth_logit_confusion_mat_0.3.png](one_year_ninth_logit_confusion_mat_0.3.png)
![one_year_ninth_logit_precision_recall_at_k.png](one_year_ninth_logit_precision_recall_at_k.png)
