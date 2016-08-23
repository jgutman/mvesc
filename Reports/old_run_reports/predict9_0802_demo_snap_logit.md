# Report for predict9 0802 demo snap logit
predict at end of 9th for weekly update ZZ

### Model Options
* label used: definite
* initial cohort grade: 9
* test cohorts: 2011
	 * 128 positive examples, 1881 negative examples
* train cohorts: 2008, 2009, 2010
	 * 96 postive examples, 3046 negative examples
* cross-validation scheme: leave cohort out
	 * searching C in 0.001, 0.01, 0.1, 1.0, 10.0, 100, 1000
	 * chose C = 0.001
	 * searching penalty in l1, l2
	 * chose penalty = l1
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
on average, model run in 0.09 seconds (14 times) <br/>precision on top 15%: 0.06371 <br/>precision on top 10%: 0.06371 <br/>precision on top 5%: 0.06371 <br/>recall on top 15%: 1.0 <br/>recall on top 10%: 1.0 <br/>recall on top 5%: 1.0 <br/>AUC value is: 0.5 <br/>top features: disability_gr_7_autism (0.0), disability_gr_7_cognitive disability (0.0), disability_gr_7_deafness (0.0)
![predict9_0802_demo_snap_logit_score_dist.png](figs/predict9_0802_demo_snap_logit_score_dist.png)
![predict9_0802_demo_snap_logit_pr_vs_threshold.png](figs/predict9_0802_demo_snap_logit_pr_vs_threshold.png)
![predict9_0802_demo_snap_logit_confusion_mat_0.3.png](figs/predict9_0802_demo_snap_logit_confusion_mat_0.3.png)
![predict9_0802_demo_snap_logit_precision_recall_at_k.png](figs/predict9_0802_demo_snap_logit_precision_recall_at_k.png)
