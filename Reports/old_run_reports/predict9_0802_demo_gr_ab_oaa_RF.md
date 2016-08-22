# Report for predict9 0802 demo gr ab oaa RF
predict at end of 9th for weekly update ZZ

### Model Options
* label used: definite
* initial cohort grade: 9
* test cohorts: 2011
	 * 128 positive examples, 1881 negative examples
* train cohorts: 2008, 2009, 2010
	 * 96 postive examples, 3046 negative examples
* cross-validation scheme: k fold, with 10 folds
	 * searching n_estimators in 500
	 * chose n_estimators = 500
	 * searching max_depth in 10, 50
	 * chose max_depth = 50
	 * searching min_samples_split in 5, 10
	 * chose min_samples_split = 10
	 * searching max_features in sqrt
	 * chose max_features = sqrt
	 * using average_precision
* imputation strategy: median plus dummies
* scaling strategy: robust

### Features Used
* grades
	 * gpa_gr_8
	 * gpa_gr_7
* oaa_normalized
	 * fourth_read_normalized
	 * seventh_math_percentile
	 * sixth_math_pl
	 * fourth_read_pl
	 * sixth_read_pl
	 * seventh_read_pl
	 * third_read_normalized
	 * fifth_math_percentile
	 * fourth_read_percentile
	 * seventh_math_pl
	 * eighth_science_p
	 * sixth_math_percentile
	 * fourth_math_normalized
	 * eighth_math_percentile
	 * sixth_math_normalized
	 * fifth_math_normalized
	 * fifth_read_normalized
	 * eighth_math_pl
	 * eighth_read_pl
	 * seventh_read_normalized
	 * eighth_math_normalized
	 * third_read_percentile
	 * fifth_science_normalized
	 * fifth_read_pl
	 * sixth_read_percentile
	 * eighth_science_percentile
	 * third_math_pl
	 * seventh_read_percentile
	 * fifth_science_pl
	 * fourth_math_percentile
	 * third_math_normalized
	 * fifth_read_percentile
	 * fifth_math_pl
	 * eighth_read_normalized
	 * fifth_science_percentile
	 * seventh_math_normalized
	 * third_read_pl
	 * eighth_read_percentile
	 * fourth_math_pl
	 * sixth_read_normalized
	 * fifth_socstudies_normalized
	 * eighth_science_normalized
	 * third_math_percentile
	 * fifth_socstudies_pl

### Performance Metrics
on average, model run in 43.21 seconds (4 times) <br/>precision on top 15%: 0.1887 <br/>precision on top 10%: 0.2388 <br/>precision on top 5%: 0.3039 <br/>recall on top 15%: 0.4453 <br/>recall on top 10%: 0.375 <br/>recall on top 5%: 0.2422 <br/>AUC value is: 0.7732 <br/>