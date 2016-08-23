# Report for 08 17 2016 grade 9 param set 22 logit
fourth pass for grade 9

### Model Options
* label used: definite_plus_ogt
* prediction grade: 9
* validation cohorts: 2011
* test cohorts: 2012
	 * 281 positive examples, 2037 negative examples
* train cohorts: 2007, 2008, 2009, 2010
	 * 450 postive examples, 4067 negative examples
* parameter choices
	 * penalty = l1
	 * C = 1.0
* cross-validation scores: k fold, with 5 folds
	 * custom_precision_5_15 score: 0.3
	 * custom_recall_5_15 score: 0.32
* imputation strategy: median plus dummies
* scaling strategy: robust

### Features Used
* absence
	 * absence_unexcused_gr_8
	 * tardy_gr_8
	 * absence_gr_8
	 * tardy_unexcused_gr_8
* demographics
	 * gender
	 * ethnicity
* oaa_normalized
	 * science_normalized_gr_5
	 * math_normalized_gr_7
	 * math_normalized_gr_5
	 * math_normalized_gr_8
	 * read_normalized_gr_6
	 * socstudies_normalized_gr_5
	 * read_normalized_gr_4
	 * science_normalized_gr_8
	 * math_normalized_gr_4
	 * read_normalized_gr_5
	 * read_normalized_gr_3
	 * math_normalized_gr_3
	 * math_normalized_gr_6
	 * read_normalized_gr_7
	 * read_normalized_gr_8
* snapshots
	 * iss_gr_8
	 * district_gr_8
	 * disadvantagement_gr_8
	 * status_gr_8
	 * section_504_plan_gr_8
	 * oss_gr_8
	 * special_ed_gr_8
	 * discipline_incidents_gr_8
	 * limited_english_gr_8
	 * gifted_gr_8
	 * disability_gr_8
* grades
	 * gpa_gr_8
	 * gpa_district_gr_8

### Performance Metrics
on average, model run in 0.11 seconds (12 times) <br/><br/>metrics on the test set: <br/>precision on top 15%: 0.389 <br/>precision on top 10%: 0.4416 <br/>precision on top 5%: 0.4783 <br/>recall on top 15%: 0.4804 <br/>recall on top 10%: 0.363 <br/>recall on top 5%: 0.1957 <br/><br/>metrics on the validation set: <br/>precision on top 15%: 0.3437 <br/>precision on top 10%: 0.3953 <br/>precision on top 5%: 0.4579 <br/>recall on top 15%: 0.4022 <br/>recall on top 10%: 0.308 <br/>recall on top 5%: 0.1775 <br/>AUC value is: 0.8432 <br/>top features: ethnicity_nan (3.3), special_ed_gr_8_100 (-0.92), read_normalized_gr_8_isnull (0.87)
![08_17_2016_grade_9_param_set_22_logit_score_dist.png](figs/08_17_2016_grade_9_param_set_22_logit_score_dist.png)
![08_17_2016_grade_9_param_set_22_logit_pr.png](figs/08_17_2016_grade_9_param_set_22_logit_pr.png)
![08_17_2016_grade_9_param_set_22_logit_confusion_mat_0.3.png](figs/08_17_2016_grade_9_param_set_22_logit_confusion_mat_0.3.png)
![08_17_2016_grade_9_param_set_22_logit_precision_recall_at_k.png](figs/08_17_2016_grade_9_param_set_22_logit_precision_recall_at_k.png)
