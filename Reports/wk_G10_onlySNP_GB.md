# Report for wk G10 onlySNP GB
weekly update Grade 10 model (xc)

### Model Options
* label used: definite
* initial cohort grade: 9
* test cohorts: 2011
	 * 128 positive examples, 1881 negative examples
* train cohorts: 2008, 2009, 2010
	 * 96 postive examples, 3046 negative examples
* cross-validation scheme: leave cohort out
	 * searching learning_rate in 0.01
	 * chose learning_rate = 0.01
	 * searching max_depth in 10, 50
	 * chose max_depth = 10
	 * searching n_estimators in 100, 500
	 * chose n_estimators = 100
	 * searching subsample in 0.5, 1.0
	 * chose subsample = 0.5
	 * using custom_recall_15
* imputation strategy: median plus dummies
* scaling strategy: robust

### Features Used
* demographics
	 * ethnicity
	 * gender
* snapshots
	 * discipline_incidents_gr_9
	 * disadvantagement_gr_9
	 * days_absent_unexcused_gr_9
	 * district_gr_9
	 * iss_gr_9
	 * disability_gr_9
	 * special_ed_gr_9
	 * status_gr_9
	 * limited_english_gr_9
	 * oss_gr_9
	 * gifted_gr_9
	 * days_absent_gr_9

### Performance Metrics
on average, model run in 30.17 seconds (8 times) <br/>precision on top 15%: 0.1333 <br/>precision on top 10%: 0.1393 <br/>precision on top 5%: 0.1881 <br/>recall on top 15%: 0.3438 <br/>recall on top 10%: 0.2188 <br/>recall on top 5%: 0.1484 <br/>AUC value is: 0.6862 <br/>