# Report for wk G10 onlySNP SVM
weekly update Grade 10 model (xc)

### Model Options
* label used: definite
* initial cohort grade: 9
* test cohorts: 2011
	 * 128 positive examples, 1881 negative examples
* train cohorts: 2008, 2009, 2010
	 * 96 postive examples, 3046 negative examples
* cross-validation scheme: leave cohort out
	 * searching C in 0.0001, 0.001, 0.01, 0.1, 1, 10
	 * chose C = 0.0001
	 * searching kernel in linear
	 * chose kernel = linear
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
on average, model run in 0.89 seconds (6 times) <br/>precision on top 15%: 0.1623 <br/>precision on top 10%: 0.1923 <br/>precision on top 5%: 0.2673 <br/>recall on top 15%: 0.3828 <br/>recall on top 10%: 0.3125 <br/>recall on top 5%: 0.2109 <br/>AUC value is: 0.6547 <br/>top features: status_gr_9_esc (0.00013), disability_gr_9_other major (0.0001), disadvantagement_gr_9_academic (0.0001)
