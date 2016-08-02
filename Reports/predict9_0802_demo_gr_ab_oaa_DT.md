# Report for predict9 0802 demo gr ab oaa DT
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
	 * searching min_samples_split in 2, 5, 10
	 * chose min_samples_split = 10
	 * searching criterion in gini, entropy
	 * chose criterion = entropy
	 * searching max_features in sqrt, log2
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
on average, model run in 0.19 seconds (72 times) <br/>precision on top 15%: 0.126 <br/>precision on top 10%: 0.126 <br/>precision on top 5%: 0.126 <br/>recall on top 15%: 0.5078 <br/>recall on top 10%: 0.5078 <br/>recall on top 5%: 0.5078 <br/>AUC value is: 0.634 <br/>top features: eighth_read_percentile (1.0), sixth_math_pl_Accelerated (0.0), sixth_math_pl_Basic (0.0)
