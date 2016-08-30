# Report for predict10 0802 demo snap DT
predict at begin of 10th for weekly update ZZ

### Model Options
* label used: definite
* initial cohort grade: 9
* test cohorts: 2011
	 * 128 positive examples, 1881 negative examples
* train cohorts: 2008, 2009, 2010
	 * 96 postive examples, 3046 negative examples
* cross-validation scheme: leave cohort out
	 * searching min_samples_split in 2, 5, 10
	 * chose min_samples_split = 2
	 * searching criterion in gini, entropy
	 * chose criterion = gini
	 * searching max_depth in 1, 5, 10, 20, 50, 100
	 * chose max_depth = 1
	 * searching max_features in sqrt, log2
	 * chose max_features = sqrt
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
on average, model run in 0.04 seconds (72 times) <br/>precision on top 15%: 0.09907 <br/>precision on top 10%: 0.09907 <br/>precision on top 5%: 0.09907 <br/>recall on top 15%: 0.6641 <br/>recall on top 10%: 0.6641 <br/>recall on top 5%: 0.6641 <br/>AUC value is: 0.6266 <br/>top features: disadvantagement_gr_9_economic (1.0), disability_gr_8_autism (0.0), disability_gr_8_cognitive disability (0.0)
![predict10_0802_demo_snap_DT_pr_vs_threshold.png](figs/predict10_0802_demo_snap_DT_pr_vs_threshold.png)
![predict10_0802_demo_snap_DT_score_dist.png](figs/predict10_0802_demo_snap_DT_score_dist.png)
![predict10_0802_demo_snap_DT_confusion_mat_0.3.png](figs/predict10_0802_demo_snap_DT_confusion_mat_0.3.png)
![predict10_0802_demo_snap_DT_precision_recall_at_k.png](figs/predict10_0802_demo_snap_DT_precision_recall_at_k.png)
