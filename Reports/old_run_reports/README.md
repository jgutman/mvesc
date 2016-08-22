# Output of Prediction Performance Reports

This folder contains automatically created, human readable reports from each time we estimate a predictive model. Here, we output a general summary of prediction performance and the inputs/parameters used.

This folder also contains a meta-report, which summarizes each of the individual reports too, for ease of understanding. Each individual run will be given a text summary description, which will be placed in this document for easy readability.

### Individual Report

* Plot Precision-Recall curve
* Plot ROC curve
* Depending on the model, estimate feature importance or top overall features
	* perhaps split them into subgroups, so not dominated by rare features
* Output the top 50 student IDs
* Compare to a baseline prediction using just demographic information
* Look for students with biggest difference from demographic baseline

### Meta Report

* Gather the AUROC of each model and the text description