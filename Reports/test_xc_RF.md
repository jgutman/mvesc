# Report for test xc RF
expand features and grade range

### Model Options
* label used: definite
* initial cohort grade: 9
* test cohorts: 2011
	 * 107 positive examples, 1713 negative examples
* train cohorts: 2007, 2008, 2009, 2010
	 * 126 postive examples, 4067 negative examples
* cross-validation scheme: leave cohort out
	 * using custom_recall_10
* imputation strategy: median plus dummies
* scaling strategy: robust

### Features Used
* grades
	 * gpa_gr_9
* absence
	 * tardy_unexcused_gr_9
	 * absence_consec_gr_9
	 * tardy_gr_9
	 * tardy_consec_gr_9
	 * medical_gr_9
* snapshots
	 * limited_english_gr_9
	 * district_gr_9
	 * iss_gr_9
	 * discipline_incidents_gr_9
	 * gifted_gr_9
	 * days_absent_gr_9
	 * disadvantagement_gr_9
	 * disability_gr_9
	 * special_ed_gr_9
	 * days_absent_unexcused_gr_9
	 * status_gr_9
	 * oss_gr_9
* mobility
	 * n_cities_to_gr_9
	 * n_addresses_to_gr_9
	 * n_districts_to_gr_9

### Performance Metrics
on average, model run in 1.68 seconds (1 times) <br/>precision on top 15%: 0.173 <br/>precision on top 10%: 0.219 <br/>precision on top 5%: 0.284 <br/>recall on top 15%: 0.477 <br/>recall on top 10%: 0.402 <br/>recall on top 5%: 0.252 <br/>AUC value is: 0.724 <br/>