# ETL Documentation

This folder is contains all the scripts used to transform the raw data provided by MVESC into a few clean tables in the specified `clean` schema. This is all done by python scripts, which are called from the run_all.sh bash script in the top level directory. The sql folder contains many of the initial sql scripts used while determining what values needed to be cleaned in the data, and hence contain many data quality checks and comments. However, none of these sql scripts need to be run in the pipeline. 

This folder also contains the module `mvesc_utility_functions`, which contains a variety of useful functions used throughout this project. They are described in more detail below.

## 1. Raw Data Types Received

There are 14 districts that MVESC works with. Of those, we have complete longitudinal data for 7 of those districts going back to 2006-2007 school year (except Ridgewood county, which starts in 2007). Other districts have varying degrees of completeness. 

Below is a list of the style of the raw data that we received and the information contained in the raw data

* Backup of SQL Server
	* Yearly snapshots for 7 districts of student status and demographics from school years starting in 2006 - 2015

* CSV text files
	* Class grades
	* Absences reported on a daily basis
	* Individualized Education Program (IEP) Accomodations
	* Test scores of standardized tests, such as Star, OAA, OGT, SAT
	* Yearly snapshots of students
	* Intervention Membership

* Excel files for District-specific information
	* Withdrawal Codes
	* IRN of Dropout Recovery Schools
	* Districts Ratings
	* Student Mobilities
	* Joint Vocational Schools
	* Districts Typology

## 2. Importing Raw Data into Our PostgreSQL Database

To address our two types of data, we used two styles to bring our data into our database.

For the SQL server backup, we opened the backup onto a separate, temporary SQL server we create. Then, we transfer that SQL server to our PostgreSQL database.

For the CSV/Excel files, we use a Python script and a JSON file. The general procedure is

 1. load data into Python data frames;
 2. create mappings from file names to table names and update JSON file automatically;
 3. check postgres database whether there is an existing table with the same table name;
 4. upload data frames to postgres server using the table names in JSON file based on function options;

The specific procedure differences of these 2 types of files are described below:

* For the CSV files which are well-structured, the corresponding Python script `csv2postgres_mvesc.py` can takes in a directory or a file as an input. It checks the file(s) and corresponding table name (in the JSON file) to see if they already exist in our database. If it does, unless we specify the option to 'replace' existing tables, the script will not upload the file. If that table name does not exist, the script will upload the table to our 'raw' schema or the specified one in our database.

* For the Excel files which has various structures and irregular headers, we have to handle each Excel file and its sheets one by one. A separate Python script `upload_mvesc_excel_files.py` is written to upload all the relevant Excel files one by one. We only need to run the script to upload all the excel files. Since all the excel data is very small, the default option is to replace the original tables in the database. The table names are either the Excel file name or the sheet name in the file.

#### Python Script Operation Details

Uses pd.read_csv with the appropriate options.

#### Utility Module Functions

* Database connections
  - postgres_engine_generator
  - postgres_pgconnection_generator
  - execute_sql_script

* Data uploading
  - read_csv_no_header
  - csv2postgres_file
  - csv2postgres_dir
  - df2postgres

* Clean data
  - clean_column

* Read from database
  - get_all_table_names
  - get_specific_table_names
  - get column_names
  - read_table_to_df
  - get_column_type

* DataFrame processing
  - df2num

* Exploring results
  - barplot_df
  - read_model_topN_feature_importance
  - barplot_feature_importance

## 3. Consolidating the Raw Tables in Public & Into the 'clean' Schema

(`consolidating_tables.py` + `json\snapshot_column_names.json`, `json\grade_column_names.json`, and `json\absence_column_names.json`)
This is a Python script used to consolidate the yearly snapshots into `clean.all_snapshots`, all provided grades into `clean.all_grades`, all fine-grained absence data into `clean.all_absences`, all accommodations tables into `clean.all_accommodations`, and all teacher data into `clean.all_teachers`. It relies on the handmade JSON files `<tablename>_column_names.json`, which maps various different spellings of raw column names to the preferred clean column names.

Output = `clean.all_snapshots`, `clean.all_grades`, `clean.all_absences`

## 4. Cleaning & Standardizing the Consolidated Tables

For each table in the `clean` schema there is a `clean_<tablename>.py` script which handles the cleaning of all values in that table. Currently the teacher and accomodation tables do not have cleaning scripts, as this data was recieved late in the summer and we did not have time to process it fully. Columns cleaned using the clean_column utility function have an associated json file named after that column mapping various spellings/formats of the same value to a clean value.

## 5. Creation of Helpful Additional Tables

Finally, the last step of our ETL is creating some other tables to be of help going forward.

(`build_graduates.py`)
This is a simple table keeping only students that have a graduation date from the all_snapshots table.

(`build_student_tracking.py`)
This builds a table tracking (`clean.wrk_tracking_students`) with yearly (longitudinal) progress for each student. It is important to note here some choices made to deal with duplicate information, documented in comments in the code.

(`build_cohort_tree_counts.py`)
This adds to the table built in `build_student_tracking.py` (`clean.wrk_tracking_students`) in order to get
coarse (`outcome_category`) and fine-grained outcome categories (`outcome_bucket`) for the students who are old enough to have outcomes.

## Summarized Order of Operations

Only step one needs to be done manually, 2-4 are accomplished by the run_all bash script in the top level directory. If new files are added, follow instructions in 2-4 to make sure all formatting is correct. 

1. Manually import backup files into separate, temporary SQL server; convert to a PostgreSQL database (public schema). These BAK files contain the district snapshot files for seven districts

2. Ensure that all csv files or directories to be uploaded are in filelist.txt -  the run_all bash script will execute `csv2postgres_mvesc.py` on each line of filelist.txt
	- default options: `schema=raw`, `replace=False`, `nrows=-1` (uploading all rows), `header=True`;
	- those files without headers are named with headers "col0", "col1", etc which need to be changed later;
	- this automatically updates `json/file_to_table_name.json`;

3. Ensure that all Excel files are in dealt with in excel2postres_mvesc.py. Because of the variety of headings, sheets, and naming conventions, each excel file is dealt with individually. `raw2postgres/excel2postres_mvesc.py` will be executed by the run_all bash script.
	- defult option is replacing existing table because all excel files are small and easy to upload

4. Ensure that all tables that need to be cleaned have a cleaning script called in `clean_and_consolidate.py`
     	- Currently `consolidating_tables.py` will try to add all tables in the `raw` schema whose name begins with `Districts` and does not contain the word `dates` to the `all_snapshots` table. All tables with names containing `grade`, `absence`, `testingaccom`, or `teacher` will go in `all_grades`, `all_absences`, `all_accomodations`, or `all_teachers`, respectively. `clean_and_consolidate.py` first calls `consolidating_tables.py`, which stacks tables that are split into files vertically. Next, it calls the various `clean_*.py` scripts that standardize values and names (oftentimes using custom JSON files for code standardization).
        - This script takes a while to run because of `build_cohort_tree_counts.py` and `generate_consec_absence_intermediate_tables.py`. Those can be commented out and run separately.
        - Note! The `clean_*.py` scripts do _not_ crash if there are new codes (which should be mapped to standardized codes). Thus, check which codes appear in columns, and make sure you map all of them. If you run into new, unknown codes, the team has assembled [Code Descriptions](https://docs.google.com/document/d/1-bVwTg1hxkULTHtAdAC12S80KjGDE1-B1lr01TksuKY).
