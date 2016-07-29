# Report for test gender ethnicity not on time logit
initial_skeleton_pipeline_test

### Model Options
* label used: not_on_time
* initial cohort grade: 9
* test cohorts: 2011
	 * 654 positive examples, 1864 negative examples
* train cohorts: 2006, 2007, 2008, 2009, 2010
	 * 1593 postive examples, 4966 negative examples
* cross-validation scheme: leave cohort out
	 * searching penalty in l1
	 * chose penalty = l1
	 * searching C in 1.0
	 * chose C = 1.0
	 * using accuracy
* imputation strategy: median plus dummies
* scaling strategy: robust

### Features Used
* demographics
	 * ethnicity
	 * gender

### Performance Metrics
on average, model run in 0.15 seconds (1 times) <br/>precision on top 10%: 0.448 <br/>precision on top 5%: 0.424 <br/>top features: ethnicity_B (1.1), ethnicity_M (0.96), ethnicity_H (0.89)
![test_gender_ethnicity_not_on_time_logit_confusion_mat_0.3.png](test_gender_ethnicity_not_on_time_logit_confusion_mat_0.3.png)
![test_gender_ethnicity_not_on_time_logit_pr_vs_threshold.png](test_gender_ethnicity_not_on_time_logit_pr_vs_threshold.png)
![test_gender_ethnicity_not_on_time_logit_precision_recall_at_k.png](test_gender_ethnicity_not_on_time_logit_precision_recall_at_k.png)
![test_gender_ethnicity_not_on_time_logit_score_dist.png](test_gender_ethnicity_not_on_time_logit_score_dist.png)
