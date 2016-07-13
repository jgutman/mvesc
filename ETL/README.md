# ETL Documentation

This is the order of operations used for preparing and transforming the tables from raw data provided by MVESC. The orderd exact steps are summarized at the end.

The ETL for Excel files are currently not documented. @Xiang, I need your help on this.

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

* Excel files for District-specific information
	* Withdrawal Codes
	* IRN of Dropout Recovery Schools
	* Districts Ratings
	* Student Mobilities
	* Joint Vocational Schools

## 2. Importing Raw Data into Our PostgreSQL Database

To address our two types of data, we used two styles to bring our data into our database.

For the SQL server backup, we opened the backup onto a separate, temporary SQL server we create. Then, we transfer that SQL server to our PostgreSQL database.

For the CSV/Excel files, we use a Python script and a JSON file. The general procedure is

 1. load data into Python data frames;
 2. create mappings from file names to table names and update JSON file automatically;
 3. check postgres database whether there is an existing table with the same table name;
 4. upload data frames to postgres server using the table names in JSON file based on function options;

* For the CSV files which are well-structured, the corresponding Python script `csv2postgres_mvesc.py` can takes in a directory or a file as an input. It checks the file(s) and corresponding table name (in the JSON file) to see if they already exist in our database. If it does, unless we specify the option to 'replace' existing tables, the script will not upload the file. If that table name does not exist, the script will upload the table to our 'raw' schema or the specified one in our database.

* For the Excel files which has various structures and irregular headers, we have to handle each Excel file and its sheets one by one. A separate Python script `upload_mvesc_excel_files.py` is written to upload all the relevant Excel files one by one. We only need to run the script to upload all the excel files. Since all the excel data is very small, the default option is to replace the original tables in the database. The table names are eithe the Excel file name or the sheet name in the file. 

#### Python Script Operation Details

Uses pd.read_csv with the appropriate options. 

#### Utility Module Functions

missing description about individual function names & brief summary of operations

## 3. Consolidating the Raw Tables in Public & Into the 'clean' Schema

### Consolidating Tables

(consolidating_tables.py + snapshots_to_table.json)
This is a Python script used to consolidate and clean all the yearly snapshots provided. It relies on the handmade JSON file, which maps various different spellings of raw column names to the preferred clean column names.
Examples include ... *missing*

Output = `clean.all_snapshots`

(consolidating_tables.py)
Inside this Python script, there is also a command to create and collapse the all_grades and all_absences table.

## Cleaning & Standardizing the Consolidated Tables

(consolidating_tables.py)
This script from the consolidating tables section also performs cleaning of the column values.

(clean_absences.sql)
This script details the choices made in cleaning and standardizing the absence data so that it's able to be used.
(all_absences_generate_mm_day_wkd.sql)
This script adds useful columns processing the dates from absences

(clean_grades.sql)
This script details the choices made in cleaning the student individual class marks.

(clean_oaaogt_0616.sql)
test scores

## 4. Creation of Helpful Additional Tables

Finally, the last step of our ETL is creating some other tables to be of help going forward.

(build_student_tracking.py)
This builds a table tracking the yearly (longitudinal) progress for each student. It is important to note here some choices made to deal with duplicate information.

(`clean.all_graduates` table script)
[script missing]
This is a simple table keeping only students that have a graduation date from the all

## 5. Future Work To Do

- fill_in_missing_years.py is currently empty
- make the utility functions into a module

## Summarized Order of Operations

1. Manually import backup files into separate, temporary SQL server; convert to a PostgreSQL database (public schema)
	- [missing] Use SQL code to automatically back these up into 'raw' schema

2. Run `csv2postgres_mvesc.py` on all the directories or files of received data
	- default options: `schema=raw`, `replace=False`, `nrows=-1` (uploading all rows), `header=True`;
	- those files without headers are named with headers "col0", "col1", etc which will be changed later;
	- this automatically updates `file_to_table_name.json`;

3. Run Excel file import process
	- Run Python script `upload_mvesc_excel_files.py`
	- defult option is replacing existing table

4. Run `consolidating_tables.py` to consolidate all the district yearly snapshot, grade, and absences tables together
5. Run `clean_absences.sql`
6. Run `clean_oaaogt_0616.sql`
7. Run `all_absences_generate_mm_day_wkd.sql`
8. Run `build_tracking_students.py`
