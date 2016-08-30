# Report for predict9 0802 demo snap RF
predict at end of 9th for weekly update ZZ

### Model Options
* label used: definite
* initial cohort grade: 9
* test cohorts: 2011
	 * 128 positive examples, 1881 negative examples
* train cohorts: 2008, 2009, 2010
	 * 96 postive examples, 3046 negative examples
* cross-validation scheme: leave cohort out
	 * searching n_estimators in 500
	 * chose n_estimators = 500
	 * searching max_depth in 10, 50
	 * chose max_depth = 10
	 * searching max_features in sqrt
	 * chose max_features = sqrt
	 * searching min_samples_split in 5, 10
	 * chose min_samples_split = 5
	 * using custom_precision_10
* imputation strategy: median plus dummies
* scaling strategy: robust

### Features Used
* snapshots
	 * disability_gr_7
	 * iss_gr_8
	 * special_ed_gr_8
	 * limited_english_gr_8
	 * disability_gr_8
	 * days_absent_gr_7
	 * disadvantagement_gr_8
	 * days_absent_unexcused_gr_7
	 * district_gr_7
	 * oss_gr_8
	 * oss_gr_7
	 * discipline_incidents_gr_8
	 * discipline_incidents_gr_7
	 * gifted_gr_7
	 * limited_english_gr_7
	 * gifted_gr_8
	 * days_absent_gr_8
	 * days_absent_unexcused_gr_8
	 * district_gr_8
	 * special_ed_gr_7
	 * disadvantagement_gr_7
	 * iss_gr_7

### Performance Metrics
on average, model run in 7.00 seconds (4 times) <br/>precision on top 15%: 0.1457 <br/>precision on top 10%: 0.1841 <br/>precision on top 5%: 0.2475 <br/>recall on top 15%: 0.3438 <br/>recall on top 10%: 0.2891 <br/>recall on top 5%: 0.1953 <br/>AUC value is: 0.7139 <br/>![predict9_0802_demo_snap_RF_score_dist.png](figs/predict9_0802_demo_snap_RF_score_dist.png)
![predict9_0802_demo_snap_RF_pr_vs_threshold.png](figs/predict9_0802_demo_snap_RF_pr_vs_threshold.png)
![predict9_0802_demo_snap_RF_precision_recall_at_k.png](figs/predict9_0802_demo_snap_RF_precision_recall_at_k.png)
![predict9_0802_demo_snap_RF_confusion_mat_0.3.png](figs/predict9_0802_demo_snap_RF_confusion_mat_0.3.png)
