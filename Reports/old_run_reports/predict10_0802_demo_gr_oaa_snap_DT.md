# Report for predict10 0802 demo gr oaa snap DT
predict at begin of 10th for weekly update ZZ

### Model Options
* label used: definite
* initial cohort grade: 9
* test cohorts: 2011
	 * 128 positive examples, 1881 negative examples
* train cohorts: 2008, 2009, 2010
	 * 96 postive examples, 3046 negative examples
* cross-validation scheme: leave cohort out
	 * searching max_features in sqrt, log2
	 * chose max_features = sqrt
	 * searching max_depth in 1, 5, 10, 20, 50, 100
	 * chose max_depth = 1
	 * searching criterion in gini, entropy
	 * chose criterion = gini
	 * searching min_samples_split in 2, 5, 10
	 * chose min_samples_split = 2
	 * using custom_precision_10
* imputation strategy: median plus dummies
* scaling strategy: robust

### Features Used
* snapshots
	 * iss_gr_8
	 * disability_gr_9
	 * district_gr_8
	 * district_gr_9
	 * special_ed_gr_7
	 * days_absent_gr_8
	 * limited_english_gr_9
	 * discipline_incidents_gr_9
	 * discipline_incidents_gr_7
	 * gifted_gr_9
	 * gifted_gr_8
	 * days_absent_unexcused_gr_7
	 * gifted_gr_7
	 * limited_english_gr_7
	 * days_absent_unexcused_gr_9
	 * iss_gr_7
	 * disadvantagement_gr_8
	 * oss_gr_9
	 * iss_gr_9
	 * oss_gr_7
	 * disability_gr_7
	 * disadvantagement_gr_9
	 * special_ed_gr_9
	 * special_ed_gr_8
	 * days_absent_unexcused_gr_8
	 * discipline_incidents_gr_8
	 * oss_gr_8
	 * disadvantagement_gr_7
	 * days_absent_gr_7
	 * limited_english_gr_8
	 * days_absent_gr_9
	 * district_gr_7
	 * disability_gr_8
* grades
	 * gpa_gr_7
	 * gpa_gr_8
	 * gpa_gr_9
* oaa_normalized
	 * sixth_read_normalized
	 * third_math_pl
	 * seventh_read_pl
	 * third_math_normalized
	 * eighth_read_percentile
	 * third_math_percentile
	 * seventh_math_pl
	 * sixth_math_normalized
	 * sixth_math_percentile
	 * eighth_read_normalized
	 * fifth_math_normalized
	 * sixth_math_pl
	 * fourth_read_percentile
	 * fourth_read_normalized
	 * fifth_science_pl
	 * fifth_read_normalized
	 * fourth_math_normalized
	 * sixth_read_pl
	 * eighth_math_normalized
	 * fourth_math_pl
	 * eighth_math_pl
	 * seventh_math_percentile
	 * fifth_math_pl
	 * fourth_math_percentile
	 * eighth_science_p
	 * eighth_math_percentile
	 * eighth_science_normalized
	 * third_read_pl
	 * fifth_socstudies_pl
	 * seventh_read_normalized
	 * eighth_read_pl
	 * fifth_read_percentile
	 * eighth_science_percentile
	 * third_read_percentile
	 * fifth_socstudies_normalized
	 * sixth_read_percentile
	 * fifth_math_percentile
	 * seventh_math_normalized
	 * fourth_read_pl
	 * third_read_normalized
	 * fifth_science_normalized
	 * seventh_read_percentile
	 * fifth_science_percentile
	 * fifth_read_pl

### Performance Metrics
on average, model run in 0.06 seconds (72 times) <br/>precision on top 15%: 0.06371 <br/>precision on top 10%: 0.06371 <br/>precision on top 5%: 0.06371 <br/>recall on top 15%: 1.0 <br/>recall on top 10%: 1.0 <br/>recall on top 5%: 1.0 <br/>AUC value is: 0.5571 <br/>top features: gpa_gr_9 (1.0), disability_gr_9_autism (0.0), disability_gr_9_cognitive disability (0.0)
![predict10_0802_demo_gr_oaa_snap_DT_pr_vs_threshold.png](figs/predict10_0802_demo_gr_oaa_snap_DT_pr_vs_threshold.png)
![predict10_0802_demo_gr_oaa_snap_mob_DT_precision_recall_at_k.png](figs/predict10_0802_demo_gr_oaa_snap_mob_DT_precision_recall_at_k.png)
![predict10_0802_demo_gr_oaa_snap_mob_DT_confusion_mat_0.3.png](figs/predict10_0802_demo_gr_oaa_snap_mob_DT_confusion_mat_0.3.png)
![predict10_0802_demo_gr_oaa_snap_mob_DT_pr_vs_threshold.png](figs/predict10_0802_demo_gr_oaa_snap_mob_DT_pr_vs_threshold.png)
![predict10_0802_demo_gr_oaa_snap_DT_confusion_mat_0.3.png](figs/predict10_0802_demo_gr_oaa_snap_DT_confusion_mat_0.3.png)
![predict10_0802_demo_gr_oaa_snap_mob_DT_score_dist.png](figs/predict10_0802_demo_gr_oaa_snap_mob_DT_score_dist.png)
![predict10_0802_demo_gr_oaa_snap_DT_score_dist.png](figs/predict10_0802_demo_gr_oaa_snap_DT_score_dist.png)
![predict10_0802_demo_gr_oaa_snap_DT_precision_recall_at_k.png](figs/predict10_0802_demo_gr_oaa_snap_DT_precision_recall_at_k.png)
