# ETL Documentation

## Raw Data Types Received

There are 14 districts that MVESC works with. Of those, we have complete longitudinal data for 7 of those districts going back to 2006-2007 school year (except 1 that starts in 2007 actually). In the rest of this ETL, we are discussing the data for those 7 districts. In a later section of this README, we discuss the data from the other districts.

Below is a list of the style of the raw data that we received

* Backup of SQL Server containing
	* yearly snapshots for 7 districts of student status and demographics from school years starting in 2006 - 2015

* CSV and Excel files for District-specific information
	* class grades
	* absences reported on a daily basis

## Importing Raw Data into Our PostgreSQL Database

To address our two types of data, we used two styles to bring our data into our database.

For the SQL server backup, we opened the backup onto a separate, temporary SQL server we create. Then, we transfer that SQL server to our PostgreSQL database.

For the CSV/Excel files, we use a Python script and a JSON file.
The JSON file is automatically created. It looks at the files in a directory and automatically creates a mapping of those file names to table names, where the tables have spaces replaced with '_' (underscores) and the file extension removed.

The Python script takes in a directory or a file as an input. It checks the file(s) and corresponding table name (in the JSON file) to see if they already exist in our database. If it does, unless we specify the option to 'overwrite' existing tables, the script will not upload the file. If that table name does not exist, the script will upload the table to our 'public' schema in our database.

#### Python Script Operation Details

## Cleaning the Input Tables in Public & Output to 'clean' Schema

