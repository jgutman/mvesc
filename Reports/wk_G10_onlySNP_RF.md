# Report for wk G10 onlySNP RF
weekly update Grade 10 model (xc)

### Model Options
* label used: definite
* initial cohort grade: 9
* test cohorts: 2011
	 * 128 positive examples, 1881 negative examples
* train cohorts: 2008, 2009, 2010
	 * 96 postive examples, 3046 negative examples
* cross-validation scheme: leave cohort out
	 * using custom_recall_15
* imputation strategy: median plus dummies
* scaling strategy: robust

### Features Used
* snapshots
	 * discipline_incidents_gr_9
	 * days_absent_unexcused_gr_9
	 * iss_gr_9
	 * special_ed_gr_9
	 * disability_gr_9
	 * days_absent_gr_9
	 * gifted_gr_9
	 * status_gr_9
	 * district_gr_9
	 * oss_gr_9
	 * limited_english_gr_9
	 * disadvantagement_gr_9

### Performance Metrics
on average, model run in 1.00 seconds (1 times) <br/>precision on top 15%: 0.1359 <br/>precision on top 10%: 0.1891 <br/>precision on top 5%: 0.1905 <br/>recall on top 15%: 0.3281 <br/>recall on top 10%: 0.2969 <br/>recall on top 5%: 0.1562 <br/>AUC value is: 0.6664 <br/>