# Report for test SGD
testing all options by looping through with a just 500 students

### Model Options
* label used: not_on_time
* initial cohort grade: 9
* test cohorts: 2011, 2012
	 * 46 positive examples, 172 negative examples
* train cohorts: 2007, 2008, 2009, 2010
	 * 64 postive examples, 166 negative examples
* cross-validation scheme: k fold, with 10 folds
	 * searching loss in hinge
	 * chose loss = hinge
	 * searching penalty in l2
	 * chose penalty = l2
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
on average, model run in 0.08 seconds (1 times) <br/>precision on top 15%: 0.303 <br/>precision on top 10%: 0.3182 <br/>precision on top 5%: 0.4545 <br/>recall on top 15%: 0.2174 <br/>recall on top 10%: 0.1522 <br/>recall on top 5%: 0.1087 <br/>AUC value is: 0.513 <br/>top features: medical_gr_8 (2.8e+01), absence_unexcused_gr_8 (1.2e+01), absence_consec_gr_8 (4.7)
![test_SGD_pr_vs_threshold.png](figs/test_SGD_pr_vs_threshold.png)
![test_SGD_score_dist.png](figs/test_SGD_score_dist.png)
![test_SGD_confusion_mat_0.3.png](figs/test_SGD_confusion_mat_0.3.png)
![test_SGD_precision_recall_at_k.png](figs/test_SGD_precision_recall_at_k.png)
