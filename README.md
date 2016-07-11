# Overview of Folder Structure

*ETL*

This folder contains scripts to process our original raw data (e.g. SQL server backups, individual files). This folder transforms raw data into a cleaned and standardized format -- ready for feature generation.

*Descriptives*

This folder contains subfolders for different subjects, such as attendance or test scores. Within each folder are images, tables, reports, and the code used to generate those summaries.

*Features*

This folder contains scripts that can be called to create various categories and specifications of features.

*Model_Results*

This folder contains scripts to estimate a predictive model and record all the inputs / parameters / results of each particular iteration.

*Reports*

This folder contains more human-readable reports of the estimated models. Many of these use data automatically derived from the results of the `Model_Results` folder.