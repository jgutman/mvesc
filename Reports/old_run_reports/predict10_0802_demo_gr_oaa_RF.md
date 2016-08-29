# Report for predict10 0802 demo gr oaa RF
predict at begin of 10th for weekly update ZZ

### Model Options
* label used: definite
* initial cohort grade: 9
* test cohorts: 2011
	 * 128 positive examples, 1881 negative examples
* train cohorts: 2008, 2009, 2010
	 * 96 postive examples, 3046 negative examples
* cross-validation scheme: leave cohort out
	 * searching max_features in sqrt
	 * chose max_features = sqrt
	 * searching min_samples_split in 5, 10
	 * chose min_samples_split = 5
	 * searching n_estimators in 500
	 * chose n_estimators = 500
	 * searching max_depth in 10, 50
	 * chose max_depth = 10
	 * using custom_precision_10
* imputation strategy: median plus dummies
* scaling strategy: robust

### Features Used
* grades
	 * gpa_gr_8
	 * gpa_gr_9
	 * gpa_gr_7
* oaa_normalized
	 * seventh_read_normalized
	 * sixth_math_percentile
	 * fifth_socstudies_pl
	 * seventh_read_percentile
	 * sixth_read_pl
	 * fifth_science_normalized
	 * fourth_read_percentile
	 * eighth_science_percentile
	 * sixth_read_normalized
	 * fourth_math_percentile
	 * fourth_read_pl
	 * eighth_read_pl
	 * fourth_math_pl
	 * fifth_math_normalized
	 * fourth_math_normalized
	 * sixth_math_normalized
	 * fifth_math_percentile
	 * seventh_math_normalized
	 * fifth_read_normalized
	 * third_read_pl
	 * fifth_science_pl
	 * eighth_science_normalized
	 * third_read_percentile
	 * sixth_math_pl
	 * seventh_math_percentile
	 * eighth_read_percentile
	 * third_read_normalized
	 * sixth_read_percentile
	 * eighth_math_normalized
	 * eighth_read_normalized
	 * third_math_normalized
	 * eighth_science_p
	 * fourth_read_normalized
	 * third_math_pl
	 * fifth_socstudies_normalized
	 * seventh_math_pl
	 * fifth_read_pl
	 * third_math_percentile
	 * seventh_read_pl
	 * fifth_math_pl
	 * eighth_math_pl
	 * fifth_science_percentile
	 * fifth_read_percentile
	 * eighth_math_percentile

### Performance Metrics
on average, model run in 10.74 seconds (4 times) <br/>precision on top 15%: 0.1987 <br/>precision on top 10%: 0.2488 <br/>precision on top 5%: 0.3465 <br/>recall on top 15%: 0.4688 <br/>recall on top 10%: 0.3906 <br/>recall on top 5%: 0.2734 <br/>AUC value is: 0.7943 <br/>![predict10_0802_demo_gr_oaa_snap_RF_confusion_mat_0.3.png](figs/predict10_0802_demo_gr_oaa_snap_RF_confusion_mat_0.3.png)
![predict10_0802_demo_gr_oaa_snap_mob_RF_score_dist.png](figs/predict10_0802_demo_gr_oaa_snap_mob_RF_score_dist.png)
![predict10_0802_demo_gr_oaa_RF_score_dist.png](figs/predict10_0802_demo_gr_oaa_RF_score_dist.png)
![predict10_0802_demo_gr_oaa_RF_pr_vs_threshold.png](figs/predict10_0802_demo_gr_oaa_RF_pr_vs_threshold.png)
![predict10_0802_demo_gr_oaa_snap_RF_score_dist.png](figs/predict10_0802_demo_gr_oaa_snap_RF_score_dist.png)
![predict10_0802_demo_gr_oaa_RF_confusion_mat_0.3.png](figs/predict10_0802_demo_gr_oaa_RF_confusion_mat_0.3.png)
![predict10_0802_demo_gr_oaa_snap_RF_precision_recall_at_k.png](figs/predict10_0802_demo_gr_oaa_snap_RF_precision_recall_at_k.png)
![predict10_0802_demo_gr_oaa_snap_mob_RF_precision_recall_at_k.png](figs/predict10_0802_demo_gr_oaa_snap_mob_RF_precision_recall_at_k.png)
![predict10_0802_demo_gr_oaa_snap_mob_RF_confusion_mat_0.3.png](figs/predict10_0802_demo_gr_oaa_snap_mob_RF_confusion_mat_0.3.png)
![predict10_0802_demo_gr_oaa_RF_precision_recall_at_k.png](figs/predict10_0802_demo_gr_oaa_RF_precision_recall_at_k.png)
![predict10_0802_demo_gr_oaa_snap_RF_pr_vs_threshold.png](figs/predict10_0802_demo_gr_oaa_snap_RF_pr_vs_threshold.png)
![predict10_0802_demo_gr_oaa_snap_mob_RF_pr_vs_threshold.png](figs/predict10_0802_demo_gr_oaa_snap_mob_RF_pr_vs_threshold.png)
