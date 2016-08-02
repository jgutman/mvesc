# Report for wk G10 onlyGRDs RF
weekly update Grade 10 model (xc)

### Model Options
* label used: definite
* initial cohort grade: 9
* test cohorts: 2011
	 * 128 positive examples, 1881 negative examples
* train cohorts: 2008, 2009, 2010
	 * 96 postive examples, 3046 negative examples
* cross-validation scheme: leave cohort out
	 * using custom_recall_15
* imputation strategy: median plus dummies
* scaling strategy: robust

### Features Used
* demographics
	 * gender
	 * ethnicity

### Performance Metrics
on average, model run in 0.60 seconds (1 times) <br/>precision on top 15%: 0.07379 <br/>precision on top 10%: 0.07379 <br/>precision on top 5%: 0.07379 <br/>recall on top 15%: 0.6094 <br/>recall on top 10%: 0.6094 <br/>recall on top 5%: 0.6094 <br/>AUC value is: 0.5334 <br/>