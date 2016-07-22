# Report for test reporting SVM
testing the reporting functions

### Model Options
* label used: definite
* initial cohort grade: 9
* test cohorts: 2011
	 * 130 positive examples, 1883 negative examples
* train cohorts: 2006, 2007, 2008, 2009, 2010
	 * 152 postive examples, 5045 negative examples
* cross-validation scheme: leave cohort out
	 * using average_precision
* imputation strategy: median plus dummies

### Features Used
* grades
	 * gpa_gr_9
* demographics
	 * ethnicity
	 * gender

### Performance Metrics
![test_reporting_SVM_pr_vs_threshold.png](test_reporting_SVM_pr_vs_threshold.png)
![test_reporting_SVM_confusion_mat_0.5.png](test_reporting_SVM_confusion_mat_0.5.png)
![test_reporting_SVM_precision_recall.png](test_reporting_SVM_precision_recall.png)
![test_reporting_SVM_confusion_mat_0.3.png](test_reporting_SVM_confusion_mat_0.3.png)
![test_reporting_SVM_score_dist.png](test_reporting_SVM_score_dist.png)
