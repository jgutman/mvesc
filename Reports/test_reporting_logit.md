# Report for test reporting logit
this run is used to test the reporting functions

### Model Options
* label used: not_on_time
* initial cohort grade: 9
* test cohorts: 2011
* train cohorts: all except test/val
* cross-validation scheme: temporal cohort
	 * using accuracy
* imputations strategy: median_plus_dummies

### Features Used
* demographics
	 * ethnicity
	 * gender
* grades
	 * gpa_gr_9

### Performance Metrics
![test_reporting_logit_precision_recall.png](test_reporting_logit_precision_recall.png)
![test_reporting_logit_score_dist.png](test_reporting_logit_score_dist.png)
![test_reporting_logit_confusion_mat_0.5.png](test_reporting_logit_confusion_mat_0.5.png)
![test_reporting_logit_pr_vs_threshold.png](test_reporting_logit_pr_vs_threshold.png)
