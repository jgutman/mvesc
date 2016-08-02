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
	 * searching max_depth in 30
	 * chose max_depth = 30
	 * searching n_estimators in 500
	 * chose n_estimators = 500
	 * searching subsample in 0.5
	 * chose subsample = 0.5
	 * searching learning_rate in 0.01
	 * chose learning_rate = 0.01
	 * using custom_precision_15
* imputation strategy: median plus dummies
* scaling strategy: robust

### Features Used
* demographics
	 * ethnicity
	 * gender
* snapshots
	 * gifted_gr_9
	 * status_gr_9
	 * discipline_incidents_gr_9
	 * district_gr_9
	 * disability_gr_9
	 * days_absent_gr_9
	 * iss_gr_9
	 * special_ed_gr_9
	 * limited_english_gr_9
	 * disadvantagement_gr_9
	 * oss_gr_9
	 * days_absent_unexcused_gr_9

### Performance Metrics
on average, model run in 117.59 seconds (1 times) <br/>precision on top 15%: 0.1225 <br/>precision on top 10%: 0.1095 <br/>precision on top 5%: 0.09901 <br/>recall on top 15%: 0.2891 <br/>recall on top 10%: 0.1719 <br/>recall on top 5%: 0.07812 <br/>AUC value is: 0.6806 <br/>