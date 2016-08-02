# Report for wk G10 allFeatures 3 DT
weekly update Grade 10 model (xc)

### Model Options
* label used: definite
* initial cohort grade: 9
* test cohorts: 2011
	 * 128 positive examples, 1881 negative examples
* train cohorts: 2008, 2009, 2010
	 * 96 postive examples, 3046 negative examples
* cross-validation scheme: leave cohort out
	 * searching max_depth in 1, 5, 10, 20, 50, 100
	 * chose max_depth = 20
	 * searching min_samples_split in 2, 5, 10
	 * chose min_samples_split = 2
	 * searching criterion in gini, entropy
	 * chose criterion = gini
	 * searching max_features in sqrt, log2
	 * chose max_features = sqrt
	 * using custom_precision_3
* imputation strategy: median plus dummies
* scaling strategy: robust

### Features Used
* demographics
	 * gender
	 * ethnicity
* grades
	 * gpa_gr_9
* oaa_normalized
	 * eighth_math_normalized
	 * eighth_science_normalized
	 * eighth_read_normalized
* snapshots
	 * days_absent_gr_9
	 * special_ed_gr_9
	 * disadvantagement_gr_9
	 * iss_gr_9
	 * oss_gr_9
	 * status_gr_9
	 * district_gr_9
	 * disability_gr_9
	 * gifted_gr_9
	 * discipline_incidents_gr_9
	 * days_absent_unexcused_gr_9
	 * limited_english_gr_9

### Performance Metrics
on average, model run in 0.04 seconds (72 times) <br/>precision on top 15%: 0.06371 <br/>precision on top 10%: 0.06371 <br/>precision on top 5%: 0.06371 <br/>recall on top 15%: 1.0 <br/>recall on top 10%: 1.0 <br/>recall on top 5%: 1.0 <br/>AUC value is: 0.5484 <br/>top features: gpa_gr_9 (0.15), eighth_read_normalized (0.14), eighth_math_normalized (0.11)
![wk_G10_allFeatures_3_DT_confusion_mat_0.3.png](figs/wk_G10_allFeatures_3_DT_confusion_mat_0.3.png)
![wk_G10_allFeatures_3_DT_pr_vs_threshold.png](figs/wk_G10_allFeatures_3_DT_pr_vs_threshold.png)
![wk_G10_allFeatures_3_DT_score_dist.png](figs/wk_G10_allFeatures_3_DT_score_dist.png)
![wk_G10_allFeatures_3_DT_precision_recall_at_k.png](figs/wk_G10_allFeatures_3_DT_precision_recall_at_k.png)
