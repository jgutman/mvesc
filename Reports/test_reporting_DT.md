# Report for test reporting DT
this run is used to test the reporting functions

### Model Options
* label used: not_on_time
* initial cohort grade: 9
* test cohorts: 2011
* train cohorts: 2006, 2007, 2008, 2009, 2010
* cross-validation scheme: temporal cohort
	 * using accuracy
* imputation strategy: median plus dummies

### Features Used
* grades
	 * gpa_gr_9
* demographics
	 * ethnicity
	 * gender

### Performance Metrics
![test_reporting_DT_precision_recall.png](test_reporting_DT_precision_recall.png)
![test_reporting_DT_pr_vs_threshold.png](test_reporting_DT_pr_vs_threshold.png)
![test_reporting_DT_score_dist.png](test_reporting_DT_score_dist.png)
![test_reporting_DT_confusion_mat_0.5.png](test_reporting_DT_confusion_mat_0.5.png)
