# Overview of Folder Structure

(see the README inside individual folders for more details)

*ETL*

This folder contains scripts to process our original raw data (e.g. SQL server backups, individual files). The output of this folder is transforming raw data into a cleaned and standardized format in our database -- ready for feature extraction and generation.

*Descriptives*

This folder contains subfolders for different subjects, such as attendance or test scores. Within each folder are images, tables, reports, and the code used to generate those summaries. This is useful for user understanding of the domain.

*Features*

This folder contains scripts that can be called to create various specifications of features.  
The output of this folder is the creation of multiple feature category tables in the database (e.g. absences, grades, demographics). The modeling can then draw directly from these feature tables.

*Model_Results*

This folder contains scripts to estimate a predictive model. It takes in a human-made options file as input. The output is a record of all the inputs / parameters / results of each particular iteration. 

*Reports*

This folder contains more human-readable reports of the estimated models. Many of these use data automatically derived from the results of the `Model_Results/results` folder.

Tested in python 3.4.3
