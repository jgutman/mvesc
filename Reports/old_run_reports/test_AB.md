# Report for test AB
testing all options by looping through with a just 500 students

### Model Options
* label used: not_on_time
* initial cohort grade: 9
* test cohorts: 2011, 2012
	 * 46 positive examples, 172 negative examples
* train cohorts: 2007, 2008, 2009, 2010
	 * 64 postive examples, 166 negative examples
* cross-validation scheme: k fold, with 10 folds
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
on average, model run in 4.94 seconds (1 times) <br/>precision on top 15%: 0.25 <br/>precision on top 10%: 0.25 <br/>precision on top 5%: 0.25 <br/>recall on top 15%: 0.3696 <br/>recall on top 10%: 0.3696 <br/>recall on top 5%: 0.3696 <br/>AUC value is: 0.5773 <br/>top features: absence_gr_8 (0.35), absence_consec_gr_8 (0.24), absence_unexcused_gr_8 (0.24)
![test_AB_precision_recall_at_k.png](figs/test_AB_precision_recall_at_k.png)
![test_AB_score_dist.png](figs/test_AB_score_dist.png)
![test_AB_pr_vs_threshold.png](figs/test_AB_pr_vs_threshold.png)
![test_AB_confusion_mat_0.3.png](figs/test_AB_confusion_mat_0.3.png)
