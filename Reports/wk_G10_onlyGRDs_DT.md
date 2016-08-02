# Report for wk G10 onlyGRDs DT
weekly update Grade 10 model (xc)

### Model Options
* label used: definite
* initial cohort grade: 9
* test cohorts: 2011
	 * 128 positive examples, 1881 negative examples
* train cohorts: 2008, 2009, 2010
	 * 96 postive examples, 3046 negative examples
* cross-validation scheme: leave cohort out
	 * searching max_depth in 5
	 * chose max_depth = 5
	 * searching criterion in entropy
	 * chose criterion = entropy
	 * using custom_recall_15
* imputation strategy: median plus dummies
* scaling strategy: robust

### Features Used
* demographics
	 * gender
	 * ethnicity

### Performance Metrics
on average, model run in 0.04 seconds (1 times) <br/>precision on top 15%: 0.07467 <br/>precision on top 10%: 0.07467 <br/>precision on top 5%: 0.07467 <br/>recall on top 15%: 0.6172 <br/>recall on top 10%: 0.6172 <br/>recall on top 5%: 0.6172 <br/>AUC value is: 0.5389 <br/>top features: gender_F (0.7), ethnicity_H (0.17), ethnicity_M (0.066)
