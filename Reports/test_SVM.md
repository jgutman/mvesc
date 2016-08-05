# Report for test SVM
testing all options by looping through with a just 500 students

### Model Options
* label used: not_on_time
* initial cohort grade: 9
* test cohorts: 2011, 2012
	 * 46 positive examples, 172 negative examples
* train cohorts: 2007, 2008, 2009, 2010
	 * 64 postive examples, 166 negative examples
* cross-validation scheme: k fold, with 10 folds
	 * searching kernel in linear
	 * chose kernel = linear
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
on average, model run in 0.10 seconds (1 times) <br/>precision on top 15%: 0.2169 <br/>precision on top 10%: 0.1364 <br/>precision on top 5%: 0.09091 <br/>recall on top 15%: 0.3913 <br/>recall on top 10%: 0.06522 <br/>recall on top 5%: 0.02174 <br/>AUC value is: 0.4122 <br/>top features: medical_gr_8 (0.67), tardy_unexcused_gr_8 (0.5), tardy_gr_8 (-0.5)
![test_reporting_SVM_pr_vs_threshold.png](figs/test_reporting_SVM_pr_vs_threshold.png)
![test_reporting_SVM_confusion_mat_0.5.png](figs/test_reporting_SVM_confusion_mat_0.5.png)
![test_xc_SVM_score_dist.png](figs/test_xc_SVM_score_dist.png)
![test_SVM_pr_vs_threshold.png](figs/test_SVM_pr_vs_threshold.png)
![test_xc_SVM_pr_vs_threshold.png](figs/test_xc_SVM_pr_vs_threshold.png)
![wk_G10_pkltest_SVM_precision_recall_at_k.png](figs/wk_G10_pkltest_SVM_precision_recall_at_k.png)
![wk_G10_pkltest_SVM_pr_vs_threshold.png](figs/wk_G10_pkltest_SVM_pr_vs_threshold.png)
![test_SVM_confusion_mat_0.3.png](figs/test_SVM_confusion_mat_0.3.png)
![test_reporting_SVM_precision_recall.png](figs/test_reporting_SVM_precision_recall.png)
![test_xc_SVM_confusion_mat_0.3.png](figs/test_xc_SVM_confusion_mat_0.3.png)
![test_SVM_score_dist.png](figs/test_SVM_score_dist.png)
![test_reporting_SVM_confusion_mat_0.3.png](figs/test_reporting_SVM_confusion_mat_0.3.png)
![auto_expand_features_test_xc_SVM_score_dist.png](figs/auto_expand_features_test_xc_SVM_score_dist.png)
![wk_G10_pkltest_SVM_confusion_mat_0.3.png](figs/wk_G10_pkltest_SVM_confusion_mat_0.3.png)
![wk_G10_pkltest_SVM_score_dist.png](figs/wk_G10_pkltest_SVM_score_dist.png)
![test_reporting_SVM_score_dist.png](figs/test_reporting_SVM_score_dist.png)
![test_xc_SVM_precision_recall_at_k.png](figs/test_xc_SVM_precision_recall_at_k.png)
![test_SVM_precision_recall_at_k.png](figs/test_SVM_precision_recall_at_k.png)
![auto_expand_features_test_xc_SVM_pr_vs_threshold.png](figs/auto_expand_features_test_xc_SVM_pr_vs_threshold.png)
![auto_expand_features_test_xc_SVM_precision_recall_at_k.png](figs/auto_expand_features_test_xc_SVM_precision_recall_at_k.png)
