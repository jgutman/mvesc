# Report for predict9 0802 demo all logit
predict at end of 9th for weekly update ZZ ALL

### Model Options
* label used: definite
* initial cohort grade: 9
* test cohorts: 2011
	 * 128 positive examples, 1881 negative examples
* train cohorts: 2008, 2009, 2010
	 * 96 postive examples, 3046 negative examples
* cross-validation scheme: leave cohort out
	 * searching penalty in l1, l2
	 * chose penalty = l1
	 * searching C in 1e-05, 0.0001, 0.001, 0.01, 0.1, 1.0, 10.0, 100, 1000
	 * chose C = 100
	 * using custom_precision_10
* imputation strategy: median plus dummies
* scaling strategy: robust

### Features Used
* oaa_normalized
	 * eighth_read_percentile
	 * fifth_math_pl
	 * sixth_read_normalized
	 * fourth_math_pl
	 * fifth_math_percentile
	 * fifth_socstudies_pl
	 * sixth_read_percentile
	 * sixth_math_percentile
	 * fifth_science_pl
	 * eighth_math_percentile
	 * fourth_read_normalized
	 * fourth_read_pl
	 * third_read_percentile
	 * eighth_read_pl
	 * fifth_socstudies_normalized
	 * fifth_read_percentile
	 * fifth_read_pl
	 * eighth_math_pl
	 * third_read_normalized
	 * fifth_math_normalized
	 * eighth_math_normalized
	 * seventh_read_pl
	 * sixth_math_pl
	 * fourth_read_percentile
	 * seventh_read_normalized
	 * fourth_math_normalized
	 * seventh_math_percentile
	 * seventh_math_normalized
	 * third_math_percentile
	 * fifth_read_normalized
	 * third_math_normalized
	 * eighth_read_normalized
	 * eighth_science_percentile
	 * eighth_science_p
	 * seventh_math_pl
	 * eighth_science_normalized
	 * third_math_pl
	 * sixth_read_pl
	 * fifth_science_percentile
	 * fourth_math_percentile
	 * third_read_pl
	 * sixth_math_normalized
	 * fifth_science_normalized
	 * seventh_read_percentile
* grades
	 * gpa_gr_8
	 * gpa_gr_7

### Performance Metrics
on average, model run in 1.95 seconds (18 times) <br/>precision on top 15%: 0.1026 <br/>precision on top 10%: 0.1045 <br/>precision on top 5%: 0.1188 <br/>recall on top 15%: 0.2422 <br/>recall on top 10%: 0.1641 <br/>recall on top 5%: 0.09375 <br/>AUC value is: 0.7018 <br/>top features: fifth_science_percentile (1.2e+01), fourth_math_pl_Limited (7.7), fourth_math_pl_Failed (7.4)
![predict9_0802_demo_all_logit_score_dist.png](figs/predict9_0802_demo_all_logit_score_dist.png)
![predict9_0802_demo_all_logit_pr_vs_threshold.png](figs/predict9_0802_demo_all_logit_pr_vs_threshold.png)
![predict9_0802_demo_all_logit_confusion_mat_0.3.png](figs/predict9_0802_demo_all_logit_confusion_mat_0.3.png)
![predict9_0802_demo_all_logit_precision_recall_at_k.png](figs/predict9_0802_demo_all_logit_precision_recall_at_k.png)
