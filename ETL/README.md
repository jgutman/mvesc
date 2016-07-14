# ETL Documentation

This is the order of operations used for preparing and transforming the tables from raw data provided by MVESC. The ordered exact steps are summarized at the end.

## 1. Raw Data Types Received

There are 14 districts that MVESC works with. Of those, we have complete longitudinal data for 7 of those districts going back to 2006-2007 school year (except Ridgewood county that starts in 2007 actually). In the rest of this ETL, we are discussing the data for those 7 districts. In a later section of this README, we discuss the data from the other districts.

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

* For the Excel files which has various structures and irregular headers, we have to handle each Excel file and its sheets one by one. A separate Python script `upload_mvesc_excel_files.py` is written to upload all the relevant Excel files one by one. We only need to run the script to upload all the excel files. Since all the excel data is very small, the default option is to replace the original tables in the database. The table names are eithe the Excel file name or the sheet name in the file.

#### Python Script Operation Details

Uses pd.read_csv with the appropriate options.

#### Utility Module Functions

missing description about individual function names & brief summary of operations

## 3. Consolidating the Raw Tables in Public & Into the 'clean' Schema

### Consolidating Tables

(consolidating_tables.py + snapshot_column_names.json, grade_column_names.json, and absence_column_names)
This is a Python script used to consolidate the yearly snapshots into clean.all_snapshots, all provided grades into clean.all_grades, and all fine-grained absence data into clean.all_absences. It relies on the handmade JSON files, which maps various different spellings of raw column names to the preferred clean column names.

Output = `clean.all_snapshots`, `clean.all_grades`, `clean.all_absences`

## Cleaning & Standardizing the Consolidated Tables

(`clean_absences.sql`)
This script details the choices made in cleaning and standardizing the absence data so that it's able to be used.
(`all_absences_generate_mm_day_wkd.sql`)
This script adds useful columns processing the dates from absences

(`clean_grades.sql`)
This script details the choices made in cleaning the student individual class marks.

(`clean_oaaogt.sql`)
This script cleans the test score data of Ohio Achievement Assessment and Ohio Graduation Tests.

(`cleaning_all_snapshots.sql`, `student_status.json`)
This script cleans most of the columns of all_snapshots, with an additional call to the utility function clean_column necessary for the student_status column.

## 4. Creation of Helpful Additional Tables

Finally, the last step of our ETL is creating some other tables to be of help going forward.

(`ETL\build_graduates_table_from_snapshots.sql`)
This is a simple table keeping only students that have a graduation date from the all_snapshots table

(`ETL\build_student_tracking.py`)
This builds a table tracking (`clean.wrk_tracking_students`) the yearly (longitudinal) progress for each student. It is important to note here some choices made to deal with duplicate information.

(`ETL\build_cohort_tree_counts.py`)
This adds to the table built in `build_student_tracking.py` (`clean.wrk_tracking_students`) in order to get
coarse (`outcome_category`) and fine-grained outcome categories (`outcome_bucket`) for the students who are old enough to have outcomes. (This may get moved into the `generate_features` part of the pipeline)


## 5. Future Work To Do

- make the utility functions into a module

## Summarized Order of Operations

1. Manually import backup files into separate, temporary SQL server; convert to a PostgreSQL database (public schema)
	- [missing] Use SQL code to automatically back these up into 'raw' schema

2. Run `csv2postgres_mvesc.py` on all the directories or files of received data
	- default options: `schema=raw`, `replace=False`, `nrows=-1` (uploading all rows), `header=True`;
	- those files without headers are named with headers "col0", "col1", etc which need to be changed later;
	- this automatically updates `file_to_table_name.json`;

3. Run Excel file import process
	- Run Python script `excel2postres_mvesc.py`
	- defult option is replacing existing table because all excel files are small and easy to upload

4. Run `clean_and_consolidate.py`
        - This script will execute all necessary scripts to take care of steps 3 and 4 above.

5. * Run `build_student_tracking.py` (this can eventually just be called
	directly from `clean_and_consolidate` -- currently commented out)

6. * Run `build_cohort_tree_counts` (this can eventually just be called
	directly from `clean_and_consolidate` -- currently commented out)
	Unless we want to add this part of outcomes assignments into pipeline instead?
