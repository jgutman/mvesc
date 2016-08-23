#!/bin/bash
echo "execute bash script to upload csv/excel data sets in /mnt/data/mvesc/PartnerData..."


########### Uploading directories #########
echo "--bash: uploading /PartnerData/teacherList06_16/"
/home/jgutman/env/bin/python csv2postgres_mvesc.py -d /mnt/data/mvesc/PartnerData/teacherList06_16/ -s public

echo "--bash: uploading /PartnerData/06_16Membership/"
/home/jgutman/env/bin/python csv2postgres_mvesc.py -d /mnt/data/mvesc/PartnerData/06_16Membership/ -s public

echo "--bash: uploading /PartnerData/AbsenceDaysDetail/"
/home/jgutman/env/bin/python csv2postgres_mvesc.py -d /mnt/data/mvesc/PartnerData/AbsenceDaysDetail/ -s public

echo "--bash: uploading /PartnerData/Submittal2_712016/"
/home/jgutman/env/bin/python csv2postgres_mvesc.py -d /mnt/data/mvesc/PartnerData/Submittal2_712016/ -s public

echo "--bash: uploading /PartnerData/DistrictsNewLexingtonNorthern/"
/home/jgutman/env/bin/python csv2postgres_mvesc.py -d /mnt/data/mvesc/PartnerData/DistrictsNewLexingtonNorthern/ -s public

echo "--bash: uploading /PartnerData/IEPTestingAccomodations/"
/home/jgutman/env/bin/python csv2postgres_mvesc.py -d /mnt/data/mvesc/PartnerData/IEPTestingAccomodations/ -s public

echo "--bash: uploading /PartnerData/Submittal_712016/"
/home/jgutman/env/bin/python csv2postgres_mvesc.py -d /mnt/data/mvesc/PartnerData/Submittal_712016/ -s public

echo "--bash: uploading /PartnerData/DistrictGrades2006_16/"
/home/jgutman/env/bin/python csv2postgres_mvesc.py -d /mnt/data/mvesc/PartnerData/DistrictGrades2006_16/ -s public

echo "--bash: uploading /PartnerData/AbsenceDaysDetail/"
/home/jgutman/env/bin/python csv2postgres_mvesc.py -d /mnt/data/mvesc/PartnerData/AbsenceDaysDetail/ -s public


######### Uploading excel files #########
echo "--bash: uploading excel files"
/home/jgutman/env/bin/python excel2postgres_mvesc.py

######### Final Notes ########
echo "--bash: this script is for demo-purpose; \n        The following files/directories are not included in this base:"
echo " - all single files in /PartnerData/"
echo " - directory and sub-directories: /DASL_AllData2010_16/"

