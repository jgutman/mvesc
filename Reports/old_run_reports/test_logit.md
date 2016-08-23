# Report for test logit
testing all options by looping through with a just 500 students

### Model Options
* label used: not_on_time
* initial cohort grade: 9
* test cohorts: 2011, 2012
	 * 46 positive examples, 172 negative examples
* train cohorts: 2007, 2008, 2009, 2010
	 * 64 postive examples, 166 negative examples
* cross-validation scheme: k fold, with 10 folds
	 * searching penalty in l1
	 * chose penalty = l1
	 * searching C in 1.0
	 * chose C = 1.0
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
on average, model run in 0.08 seconds (1 times) <br/>precision on top 15%: 0.1818 <br/>precision on top 10%: 0.2273 <br/>precision on top 5%: 0.2727 <br/>recall on top 15%: 0.1304 <br/>recall on top 10%: 0.1087 <br/>recall on top 5%: 0.06522 <br/>AUC value is: 0.4617 <br/>top features: medical_gr_8 (0.28), absence_gr_8 (-0.26), tardy_gr_8 (-0.13)
![test_reporting_logit_precision_recall.png](figs/test_reporting_logit_precision_recall.png)
![test_reporting_logit_score_dist.png](figs/test_reporting_logit_score_dist.png)
![auto_expand_features_test_xc_logit_pr_vs_threshold.png](figs/auto_expand_features_test_xc_logit_pr_vs_threshold.png)
![auto_expand_features_test_logit_precision_recall_at_k.png](figs/auto_expand_features_test_logit_precision_recall_at_k.png)
![wk_G10_pkltest_logit_confusion_mat_0.3.png](figs/wk_G10_pkltest_logit_confusion_mat_0.3.png)
![auto_expand_features_test_xc_logit_score_dist.png](figs/auto_expand_features_test_xc_logit_score_dist.png)
![auto_expand_features_test_logit_confusion_mat_0.3.png](figs/auto_expand_features_test_logit_confusion_mat_0.3.png)
![test_xc_logit_precision_recall_at_k.png](figs/test_xc_logit_precision_recall_at_k.png)
![wk_G10_pkltest_logit_score_dist.png](figs/wk_G10_pkltest_logit_score_dist.png)
![auto_expand_features_test_xc_logit_precision_recall_at_k.png](figs/auto_expand_features_test_xc_logit_precision_recall_at_k.png)
![test_logit_score_dist.png](figs/test_logit_score_dist.png)
![test_logit_confusion_mat_0.3.png](figs/test_logit_confusion_mat_0.3.png)
![test_gender_ethnicity_not_on_time_logit_confusion_mat_0.3.png](figs/test_gender_ethnicity_not_on_time_logit_confusion_mat_0.3.png)
![auto_expand_features_test_logit_precision_recall.png](figs/auto_expand_features_test_logit_precision_recall.png)
![test_gender_ethnicity_not_on_time_logit_pr_vs_threshold.png](figs/test_gender_ethnicity_not_on_time_logit_pr_vs_threshold.png)
![wk_G10_pkltest_logit_pr_vs_threshold.png](figs/wk_G10_pkltest_logit_pr_vs_threshold.png)
![testing_write_to_database_logit_precision_recall_at_k.png](figs/testing_write_to_database_logit_precision_recall_at_k.png)
![test_gender_ethnicity_not_on_time_logit_precision_recall_at_k.png](figs/test_gender_ethnicity_not_on_time_logit_precision_recall_at_k.png)
![testing_write_to_database_logit_score_dist.png](figs/testing_write_to_database_logit_score_dist.png)
![test_logit_precision_recall_at_k.png](figs/test_logit_precision_recall_at_k.png)
![test_logit_pr_vs_threshold.png](figs/test_logit_pr_vs_threshold.png)
![test_gender_ethnicity_not_on_time_logit_score_dist.png](figs/test_gender_ethnicity_not_on_time_logit_score_dist.png)
![test_xc_logit_confusion_mat_0.3.png](figs/test_xc_logit_confusion_mat_0.3.png)
![test_reporting_logit_confusion_mat_0.5.png](figs/test_reporting_logit_confusion_mat_0.5.png)
![testing_write_to_database_logit_confusion_mat_0.3.png](figs/testing_write_to_database_logit_confusion_mat_0.3.png)
![wk_G10_pkltest_logit_precision_recall_at_k.png](figs/wk_G10_pkltest_logit_precision_recall_at_k.png)
![test_xc_logit_score_dist.png](figs/test_xc_logit_score_dist.png)
![testing_write_to_database_logit_pr.png](figs/testing_write_to_database_logit_pr.png)
![test_reporting_logit_pr_vs_threshold.png](figs/test_reporting_logit_pr_vs_threshold.png)
![test_reporting_logit_confusion_mat_0.3.png](figs/test_reporting_logit_confusion_mat_0.3.png)
![auto_expand_features_test_logit_confusion_mat_0.5.png](figs/auto_expand_features_test_logit_confusion_mat_0.5.png)
![auto_expand_features_test_logit_score_dist.png](figs/auto_expand_features_test_logit_score_dist.png)
![auto_expand_features_test_logit_pr_vs_threshold.png](figs/auto_expand_features_test_logit_pr_vs_threshold.png)
![test_xc_logit_pr_vs_threshold.png](figs/test_xc_logit_pr_vs_threshold.png)
