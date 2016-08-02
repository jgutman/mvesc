# Report for wk G10 onlyGRDs logit
weekly update Grade 10 model (xc)

### Model Options
* label used: definite
* initial cohort grade: 9
* test cohorts: 2011
	 * 128 positive examples, 1881 negative examples
* train cohorts: 2008, 2009, 2010
	 * 96 postive examples, 3046 negative examples
* cross-validation scheme: leave cohort out
	 * searching penalty in l1
	 * chose penalty = l1
	 * searching C in 1.0
	 * chose C = 1.0
	 * using custom_recall_15
* imputation strategy: median plus dummies
* scaling strategy: robust

### Features Used
* demographics
	 * gender
	 * ethnicity

### Performance Metrics
on average, model run in 0.06 seconds (1 times) <br/>precision on top 15%: 0.0746 <br/>precision on top 10%: 0.0746 <br/>precision on top 5%: 0.0746 <br/>recall on top 15%: 0.6172 <br/>recall on top 10%: 0.6172 <br/>recall on top 5%: 0.6172 <br/>AUC value is: 0.5481 <br/>top features: ethnicity_A (0.0), ethnicity_B (0.0), ethnicity_H (0.0)
