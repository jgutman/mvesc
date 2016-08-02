# Report for wk G10 allFeatures GB
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
	 * searching max_depth in 30
	 * chose max_depth = 30
	 * searching n_estimators in 500
	 * chose n_estimators = 500
	 * searching subsample in 0.5
	 * chose subsample = 0.5
	 * using custom_precision_15
* imputation strategy: median plus dummies
* scaling strategy: robust

### Features Used
* demographics
	 * ethnicity
	 * gender
* snapshots
	 * iss_gr_9
	 * status_gr_9
	 * oss_gr_9
	 * disability_gr_9
	 * disadvantagement_gr_9
	 * discipline_incidents_gr_9
	 * gifted_gr_9
	 * special_ed_gr_9
	 * days_absent_unexcused_gr_9
	 * limited_english_gr_9
	 * days_absent_gr_9
	 * district_gr_9
* oaa_normalized
	 * eighth_read_normalized
	 * eighth_math_normalized
	 * eighth_science_normalized
* grades
	 * gpa_gr_9

### Performance Metrics
on average, model run in 103.15 seconds (1 times) <br/>precision on top 15%: 0.1722 <br/>precision on top 10%: 0.2239 <br/>precision on top 5%: 0.297 <br/>recall on top 15%: 0.4062 <br/>recall on top 10%: 0.3516 <br/>recall on top 5%: 0.2344 <br/>AUC value is: 0.7719 <br/>