# Descriptive Analysis

This directory contains codes, scripts, and figures for specific useful pieces of descriptive stats listed below. None of this code is necessary to run models, but may be useful to gather a better understanding of the data.

Many of these jupyter notebooks and R scripts rely on the raw data being in the `public` schema, the clean data being in the `clean` schema, and the features, outcomes, and modeling results being in the `model` schema.

* Exploratory analysis (Python)
 - initial exploration of the data 

* Absence analysis (Python)
 - using both aggregated and daily absence data
 - absence pattern by month, week, day
 - consecutive absence
 - graduate vs dropout comparison
 
* Cohort analysis (Python)
 - the goal is to better label the outcomes
 - withdrawal types for different cohorts
 - automatically draw trees to label outcomes

* General summary (R)
 - disability
 - economic disadvantage
 - status, etc

* Grades analysis (Python)
 - GPA distribution
 - comparison of graduates and dropout
 - comparison of graduates and no IRN

* Outcome analysis (Python)
 - label students to different buckets
 - buckets comparison in terms of absence, GPA, etc

* Test scores (Python & SQL)
 - Ohio Achievement Accessments and Ohio Graduation Tests Analysis
 - Distributions
 - Correlations

* Model results (Python)
 - models: random forest, logit
 - model performance: precision, recall
 - model predictions 
