# Report for test xc SVM
expand features and grade range

### Model Options
* label used: definite
* initial cohort grade: 9
* test cohorts: 2011
	 * 107 positive examples, 1713 negative examples
* train cohorts: 2007, 2008, 2009, 2010
	 * 126 postive examples, 4067 negative examples
* cross-validation scheme: leave cohort out
	 * searching C in 1.0
	 * chose C = 1.0
	 * searching kernel in linear
	 * chose kernel = linear
	 * using custom_recall_10
* imputation strategy: median plus dummies
* scaling strategy: robust

### Features Used
* snapshots
	 * gifted_gr_9
	 * district_gr_9
	 * oss_gr_9
	 * disability_gr_9
	 * discipline_incidents_gr_9
	 * days_absent_gr_9
	 * days_absent_unexcused_gr_9
	 * special_ed_gr_9
	 * status_gr_9
	 * limited_english_gr_9
	 * disadvantagement_gr_9
	 * iss_gr_9
* grades
	 * gpa_gr_9
* mobility
	 * n_districts_to_gr_9
	 * n_addresses_to_gr_9
	 * n_cities_to_gr_9
* absence
	 * absence_consec_gr_9
	 * tardy_gr_9
	 * tardy_consec_gr_9
	 * medical_gr_9
	 * tardy_unexcused_gr_9

### Performance Metrics
on average, model run in 2.86 seconds (1 times) <br/>precision on top 15%: 0.08696 <br/>precision on top 10%: 0.09626 <br/>precision on top 5%: 0.09836 <br/>recall on top 15%: 0.2243 <br/>recall on top 10%: 0.1682 <br/>recall on top 5%: 0.1121 <br/>AUC value is: 0.5237 <br/>top features: disability_gr_9_other major (1.0), status_gr_9_mrdd (1.0), tardy_unexcused_gr_9 (0.00097)
