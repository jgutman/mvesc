# Overview of Folder Structure

(see the README inside individual folders for more details)

*Installation*

On a new AWS EC2 instance that runs Ubuntu 14.04 (and that has security groups that allow you to SSH into it), you should first install a few packages:
```
sudo apt-get update
sudo apt-get install python-virtualenv libcairo2-dev libjpeg8-dev libpango1.0-dev libgif-dev build-essential g++ python-dev python3-dev
```

Then make a Python3 virtual envirovnment and activate it: `virtualenv -p /usr/bin/python3.4 env` and `source env/bin/activate`.

Install all other dependencies using `pip install -r requirements.txt`. Note that `pycairo` is installed directly from `git+http://git.cairographics.org/git/pycairo`. If you encounter difficulties, try installing pycairo separately with `pip install git+http://git.cairographics.org/git/pycairo`.

The code requires a file located at `/mnt/data/mvesc/pgpass`, which lists the credentials to a Postgres database in the standard format `hostname:port:database:username:password`.

*ETL*

This folder contains scripts to process and clean our original raw data (e.g. SQL server backups, individual files). The scripts in this folder transform raw data into a cleaned and standardized format in our database (the `clean` schema)-- ready for feature extraction and generation.

*Descriptives*

This folder contains subfolders for different subjects, such as attendance or test scores. Within each folder are images, tables, reports, and the code used to generate those summaries. This is useful for user understanding of the domain.

*Features*

This folder contains scripts that can be called to create various specifications of features.  
The output of this folder is the creation of multiple feature category tables in the database (e.g. absences, grades, demographics). The modeling can then draw directly from these feature tables.

*Model_Results*

This folder contains scripts to estimate a predictive model. It takes in a human-made options file as input. The output is a record of all the inputs / parameters / results of each particular iteration.

*Reports*

This folder contains more human-readable reports of the estimated models.

Tested in python 3.4.3
