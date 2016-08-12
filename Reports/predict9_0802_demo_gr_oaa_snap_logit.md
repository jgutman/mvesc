# Report for predict9 0802 demo gr oaa snap logit
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
	 * chose C = 1.0
	 * using custom_precision_10
* imputation strategy: median plus dummies
* scaling strategy: robust

### Features Used
* snapshots
	 * disability_gr_7
	 * iss_gr_8
	 * gifted_gr_8
	 * iss_gr_7
	 * days_absent_unexcused_gr_8
	 * special_ed_gr_7
	 * district_gr_7
	 * discipline_incidents_gr_8
	 * oss_gr_7
	 * special_ed_gr_8
	 * disability_gr_8
	 * days_absent_gr_8
	 * limited_english_gr_7
	 * disadvantagement_gr_7
	 * days_absent_gr_7
	 * days_absent_unexcused_gr_7
	 * district_gr_8
	 * disadvantagement_gr_8
	 * limited_english_gr_8
	 * gifted_gr_7
	 * oss_gr_8
	 * discipline_incidents_gr_7
* oaa_normalized
	 * seventh_math_pl
	 * fifth_read_normalized
	 * eighth_math_normalized
	 * fourth_math_pl
	 * third_read_normalized
	 * fifth_science_percentile
	 * eighth_science_percentile
	 * third_read_percentile
	 * fifth_read_percentile
	 * third_read_pl
	 * eighth_read_normalized
	 * third_math_normalized
	 * eighth_read_percentile
	 * fourth_read_normalized
	 * eighth_math_percentile
	 * sixth_read_percentile
	 * fifth_math_percentile
	 * eighth_math_pl
	 * eighth_science_normalized
	 * sixth_math_percentile
	 * sixth_read_pl
	 * third_math_percentile
	 * third_math_pl
	 * seventh_read_pl
	 * fourth_read_percentile
	 * fifth_read_pl
	 * fifth_math_normalized
	 * sixth_math_pl
	 * fourth_math_percentile
	 * fourth_math_normalized
	 * seventh_math_normalized
	 * eighth_science_p
	 * fifth_science_pl
	 * seventh_read_percentile
	 * seventh_math_percentile
	 * fifth_socstudies_normalized
	 * sixth_read_normalized
	 * fourth_read_pl
	 * sixth_math_normalized
	 * seventh_read_normalized
	 * fifth_math_pl
	 * eighth_read_pl
	 * fifth_science_normalized
	 * fifth_socstudies_pl
* grades
	 * gpa_gr_8
	 * gpa_gr_7

### Performance Metrics
on average, model run in 2.04 seconds (18 times) <br/>precision on top 15%: 0.1555 <br/>precision on top 10%: 0.1891 <br/>precision on top 5%: 0.2376 <br/>recall on top 15%: 0.3984 <br/>recall on top 10%: 0.2969 <br/>recall on top 5%: 0.1875 <br/>AUC value is: 0.748 <br/>top features: eighth_read_pl_nan (1.8), gpa_gr_7_isnull (1.8), fourth_math_pl_Passed (0.93)
![predict9_0802_demo_gr_oaa_snap_logit_pr_vs_threshold.png](figs/predict9_0802_demo_gr_oaa_snap_logit_pr_vs_threshold.png)
![predict9_0802_demo_gr_oaa_snap_logit_score_dist.png](figs/predict9_0802_demo_gr_oaa_snap_logit_score_dist.png)
![predict9_0802_demo_gr_oaa_snap_logit_precision_recall_at_k.png](figs/predict9_0802_demo_gr_oaa_snap_logit_precision_recall_at_k.png)
![predict9_0802_demo_gr_oaa_snap_logit_confusion_mat_0.3.png](figs/predict9_0802_demo_gr_oaa_snap_logit_confusion_mat_0.3.png)
