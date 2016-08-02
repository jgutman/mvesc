# Report for predict9 0802 demo RF
predict at end of 9th for weekly update ZZ

### Model Options
* label used: definite
* initial cohort grade: 9
* test cohorts: 2011
	 * 128 positive examples, 1881 negative examples
* train cohorts: 2008, 2009, 2010
	 * 96 postive examples, 3046 negative examples
* cross-validation scheme: k fold, with 10 folds
	 * searching max_depth in 10, 50
	 * chose max_depth = 10
	 * searching max_features in sqrt
	 * chose max_features = sqrt
	 * searching min_samples_split in 5, 10
	 * chose min_samples_split = 5
	 * searching n_estimators in 500
	 * chose n_estimators = 500
	 * using average_precision
* imputation strategy: median plus dummies
* scaling strategy: robust

### Features Used
* grades
	 * gpa_gr_7
	 * gpa_gr_8

### Performance Metrics
on average, model run in 27.28 seconds (4 times) <br/>precision on top 15%: 0.08522 <br/>precision on top 10%: 0.08522 <br/>precision on top 5%: 0.1683 <br/>recall on top 15%: 0.7344 <br/>recall on top 10%: 0.7344 <br/>recall on top 5%: 0.1328 <br/>AUC value is: 0.6435 <br/>