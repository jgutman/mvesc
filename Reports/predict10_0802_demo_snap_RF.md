# Report for predict10 0802 demo snap RF
predict at begin of 10th for weekly update ZZ

### Model Options
* label used: definite
* initial cohort grade: 9
* test cohorts: 2011
	 * 128 positive examples, 1881 negative examples
* train cohorts: 2008, 2009, 2010
	 * 96 postive examples, 3046 negative examples
* cross-validation scheme: leave cohort out
	 * searching max_depth in 10, 50
	 * chose max_depth = 10
	 * searching n_estimators in 500
	 * chose n_estimators = 500
	 * searching max_features in sqrt
	 * chose max_features = sqrt
	 * searching min_samples_split in 5, 10
	 * chose min_samples_split = 5
	 * using custom_precision_10
* imputation strategy: median plus dummies
* scaling strategy: robust

### Features Used
* snapshots
	 * days_absent_gr_9
	 * special_ed_gr_9
	 * discipline_incidents_gr_9
	 * disability_gr_8
	 * gifted_gr_8
	 * special_ed_gr_8
	 * discipline_incidents_gr_7
	 * special_ed_gr_7
	 * days_absent_unexcused_gr_7
	 * days_absent_unexcused_gr_9
	 * gifted_gr_9
	 * disadvantagement_gr_8
	 * oss_gr_8
	 * disadvantagement_gr_7
	 * days_absent_unexcused_gr_8
	 * iss_gr_8
	 * district_gr_9
	 * gifted_gr_7
	 * oss_gr_7
	 * district_gr_8
	 * iss_gr_7
	 * disadvantagement_gr_9
	 * days_absent_gr_7
	 * days_absent_gr_8
	 * district_gr_7
	 * disability_gr_9
	 * oss_gr_9
	 * limited_english_gr_9
	 * discipline_incidents_gr_8
	 * limited_english_gr_8
	 * iss_gr_9
	 * limited_english_gr_7
	 * disability_gr_7

### Performance Metrics
on average, model run in 7.49 seconds (4 times) <br/>precision on top 15%: 0.2119 <br/>precision on top 10%: 0.2139 <br/>precision on top 5%: 0.2673 <br/>recall on top 15%: 0.5 <br/>recall on top 10%: 0.3359 <br/>recall on top 5%: 0.2109 <br/>AUC value is: 0.7647 <br/>![predict10_0802_demo_snap_RF_pr_vs_threshold.png](figs/predict10_0802_demo_snap_RF_pr_vs_threshold.png)
![predict10_0802_demo_snap_RF_precision_recall_at_k.png](figs/predict10_0802_demo_snap_RF_precision_recall_at_k.png)
![predict10_0802_demo_snap_RF_confusion_mat_0.3.png](figs/predict10_0802_demo_snap_RF_confusion_mat_0.3.png)
![predict10_0802_demo_snap_RF_score_dist.png](figs/predict10_0802_demo_snap_RF_score_dist.png)
