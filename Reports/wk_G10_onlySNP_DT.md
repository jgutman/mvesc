# Report for wk G10 onlySNP DT
weekly update Grade 10 model (xc)

### Model Options
* label used: definite
* initial cohort grade: 9
* test cohorts: 2011
	 * 128 positive examples, 1881 negative examples
* train cohorts: 2008, 2009, 2010
	 * 96 postive examples, 3046 negative examples
* cross-validation scheme: leave cohort out
	 * searching criterion in entropy
	 * chose criterion = entropy
	 * searching max_depth in 5
	 * chose max_depth = 5
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
on average, model run in 0.07 seconds (1 times) <br/>precision on top 15%: 0.1646 <br/>precision on top 10%: 0.1789 <br/>precision on top 5%: 0.1976 <br/>recall on top 15%: 0.4141 <br/>recall on top 10%: 0.3438 <br/>recall on top 5%: 0.2578 <br/>AUC value is: 0.6182 <br/>top features: days_absent_gr_9 (0.27), discipline_incidents_gr_9 (0.13), status_gr_9_inactive (0.1)
