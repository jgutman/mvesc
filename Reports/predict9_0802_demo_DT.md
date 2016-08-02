# Report for predict9 0802 demo DT
predict at end of 9th for weekly update ZZ

### Model Options
* label used: definite
* initial cohort grade: 9
* test cohorts: 2011
	 * 128 positive examples, 1881 negative examples
* train cohorts: 2008, 2009, 2010
	 * 96 postive examples, 3046 negative examples
* cross-validation scheme: k fold, with 10 folds
	 * searching max_depth in 1, 5, 10, 20, 50, 100
	 * chose max_depth = 1
	 * searching max_features in sqrt, log2
	 * chose max_features = log2
	 * searching min_samples_split in 2, 5, 10
	 * chose min_samples_split = 10
	 * searching criterion in gini, entropy
	 * chose criterion = entropy
	 * using average_precision
* imputation strategy: median plus dummies
* scaling strategy: robust

### Features Used
* grades
	 * gpa_gr_7
	 * gpa_gr_8

### Performance Metrics
on average, model run in 0.15 seconds (72 times) <br/>precision on top 15%: 0.06371 <br/>precision on top 10%: 0.06371 <br/>precision on top 5%: 0.06371 <br/>recall on top 15%: 1.0 <br/>recall on top 10%: 1.0 <br/>recall on top 5%: 1.0 <br/>AUC value is: 0.5314 <br/>top features: gpa_gr_7 (1.0), gpa_gr_7_isnull (0.0), gpa_gr_8_isnull (0.0)
