# Report for test DT
testing all options by looping through with a just 500 students

### Model Options
* label used: not_on_time
* initial cohort grade: 9
* test cohorts: 2011, 2012
	 * 46 positive examples, 172 negative examples
* train cohorts: 2007, 2008, 2009, 2010
	 * 64 postive examples, 166 negative examples
* cross-validation scheme: k fold, with 10 folds
	 * searching max_depth in 5
	 * chose max_depth = 5
	 * searching criterion in entropy
	 * chose criterion = entropy
	 * using ['custom_precision_5']
* imputation strategy: median plus dummies
* scaling strategy: robust

### Features Used
* absence
	 * tardy_gr_8
	 * tardy_consec_gr_8
	 * absence_consec_gr_8
	 * absence_unexcused_gr_8
	 * medical_gr_8
	 * tardy_unexcused_gr_8
	 * absence_gr_8

### Performance Metrics
on average, model run in 0.07 seconds (1 times) <br/>precision on top 15%: 0.2206 <br/>precision on top 10%: 0.2206 <br/>precision on top 5%: 0.2206 <br/>recall on top 15%: 0.3261 <br/>recall on top 10%: 0.3261 <br/>recall on top 5%: 0.3261 <br/>AUC value is: 0.5849 <br/>top features: absence_gr_8 (0.83), medical_gr_8 (0.12), absence_unexcused_gr_8 (0.049)
![wk_G10_pkltest_DT_score_dist.png](figs/wk_G10_pkltest_DT_score_dist.png)
![wk_G10_pkltest_DT_precision_recall_at_k.png](figs/wk_G10_pkltest_DT_precision_recall_at_k.png)
![testing_write_to_database_DT_confusion_mat_0.3.png](figs/testing_write_to_database_DT_confusion_mat_0.3.png)
![test_DT_score_dist.png](figs/test_DT_score_dist.png)
![auto_expand_features_test_xc_DT_precision_recall_at_k.png](figs/auto_expand_features_test_xc_DT_precision_recall_at_k.png)
![test_gender_ethnicity_not_on_time_DT_score_dist.png](figs/test_gender_ethnicity_not_on_time_DT_score_dist.png)
![auto_expand_features_test_DT_precision_recall.png](figs/auto_expand_features_test_DT_precision_recall.png)
![test_gender_ethnicity_not_on_time_DT_precision_recall_at_k.png](figs/test_gender_ethnicity_not_on_time_DT_precision_recall_at_k.png)
![test_gender_ethnicity_not_on_time_DT_pr_vs_threshold.png](figs/test_gender_ethnicity_not_on_time_DT_pr_vs_threshold.png)
![testing_write_to_database_DT_precision_recall_at_k.png](figs/testing_write_to_database_DT_precision_recall_at_k.png)
![test_gender_ethnicity_not_on_time_DT_confusion_mat_0.3.png](figs/test_gender_ethnicity_not_on_time_DT_confusion_mat_0.3.png)
![auto_expand_features_test_DT_pr_vs_threshold.png](figs/auto_expand_features_test_DT_pr_vs_threshold.png)
![auto_expand_features_test_xc_DT_score_dist.png](figs/auto_expand_features_test_xc_DT_score_dist.png)
![wk_G10_pkltest_DT_confusion_mat_0.3.png](figs/wk_G10_pkltest_DT_confusion_mat_0.3.png)
![test_DT_confusion_mat_0.3.png](figs/test_DT_confusion_mat_0.3.png)
![test_reporting_DT_precision_recall.png](figs/test_reporting_DT_precision_recall.png)
![test_reporting_DT_pr_vs_threshold.png](figs/test_reporting_DT_pr_vs_threshold.png)
![test_xc_DT_confusion_mat_0.3.png](figs/test_xc_DT_confusion_mat_0.3.png)
![test_xc_DT_pr_vs_threshold.png](figs/test_xc_DT_pr_vs_threshold.png)
![test_reporting_DT_score_dist.png](figs/test_reporting_DT_score_dist.png)
![auto_expand_features_test_xc_DT_pr_vs_threshold.png](figs/auto_expand_features_test_xc_DT_pr_vs_threshold.png)
![test_xc_DT_precision_recall_at_k.png](figs/test_xc_DT_precision_recall_at_k.png)
![wk_G10_pkltest_DT_pr_vs_threshold.png](figs/wk_G10_pkltest_DT_pr_vs_threshold.png)
![test_reporting_DT_confusion_mat_0.3.png](figs/test_reporting_DT_confusion_mat_0.3.png)
![auto_expand_features_test_DT_precision_recall_at_k.png](figs/auto_expand_features_test_DT_precision_recall_at_k.png)
![test_reporting_DT_confusion_mat_0.5.png](figs/test_reporting_DT_confusion_mat_0.5.png)
![auto_expand_features_test_DT_score_dist.png](figs/auto_expand_features_test_DT_score_dist.png)
![test_DT_pr_vs_threshold.png](figs/test_DT_pr_vs_threshold.png)
![testing_write_to_database_DT_score_dist.png](figs/testing_write_to_database_DT_score_dist.png)
![test_DT_precision_recall_at_k.png](figs/test_DT_precision_recall_at_k.png)
![testing_write_to_database_DT_pr.png](figs/testing_write_to_database_DT_pr.png)
![auto_expand_features_test_DT_confusion_mat_0.3.png](figs/auto_expand_features_test_DT_confusion_mat_0.3.png)
![auto_expand_features_test_DT_confusion_mat_0.5.png](figs/auto_expand_features_test_DT_confusion_mat_0.5.png)
![test_xc_DT_score_dist.png](figs/test_xc_DT_score_dist.png)
