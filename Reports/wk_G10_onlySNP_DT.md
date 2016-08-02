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
	 * searching criterion in gini, entropy
	 * chose criterion = gini
	 * searching min_samples_split in 2, 5, 10
	 * chose min_samples_split = 2
	 * searching max_features in sqrt, log2
	 * chose max_features = sqrt
	 * searching max_depth in 1, 5, 10, 20, 50, 100
	 * chose max_depth = 1
	 * using custom_recall_15
* imputation strategy: median plus dummies
* scaling strategy: robust

### Features Used
* snapshots
	 * district_gr_9
	 * limited_english_gr_9
	 * days_absent_gr_9
	 * iss_gr_9
	 * discipline_incidents_gr_9
	 * oss_gr_9
	 * disability_gr_9
	 * days_absent_unexcused_gr_9
	 * gifted_gr_9
	 * special_ed_gr_9
	 * status_gr_9
	 * disadvantagement_gr_9
* demographics
	 * ethnicity
	 * gender

### Performance Metrics
on average, model run in 0.04 seconds (72 times) <br/>precision on top 15%: 0.06371 <br/>precision on top 10%: 0.06371 <br/>precision on top 5%: 0.06371 <br/>recall on top 15%: 1.0 <br/>recall on top 10%: 1.0 <br/>recall on top 5%: 1.0 <br/>AUC value is: 0.5075 <br/>top features: status_gr_9_esc (1.0), district_gr_9_Coshocton (0.0), district_gr_9_Crooksville (0.0)
