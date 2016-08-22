#!/bin/bash
echo "execute bash script to upload csv/excel data sets in /mnt/data/mvesc/PartnerData..."

echo "--bash: uploading /PartnerData/teacherList06_16/"
#/home/jgutman/env/bin/python csv2postgres_mvesc.py -d /mnt/data/mvesc/PartnerData/teacherList06_16/ -s raw
/home/jgutman/env/bin/python csv2postgres_mvesc.py -d /mnt/data/mvesc/PartnerData/teacherList06_16/ -s public

echo "--bash: uploading /PartnerData/06_16Membership/"
#/home/jgutman/env/bin/python csv2postgres_mvesc.py -d /mnt/data/mvesc/PartnerData/06_16Membership/ -s raw
/home/jgutman/env/bin/python csv2postgres_mvesc.py -d /mnt/data/mvesc/PartnerData/06_16Membership/ -s public

echo "--bash: uploading /PartnerData/AbsenceDaysDetail/"
#/home/jgutman/env/bin/python csv2postgres_mvesc.py -d /mnt/data/mvesc/PartnerData/AbsenceDaysDetail/ -s raw
/home/jgutman/env/bin/python csv2postgres_mvesc.py -d /mnt/data/mvesc/PartnerData/AbsenceDaysDetail/ -s public

echo "--bash: uploading /PartnerData/Submittal2_712016/"
#/home/jgutman/env/bin/python csv2postgres_mvesc.py -d /mnt/data/mvesc/PartnerData/Submittal2_712016/ -s raw
/home/jgutman/env/bin/python csv2postgres_mvesc.py -d /mnt/data/mvesc/PartnerData/Submittal2_712016/ -s public


echo "--bash: uploading excel files"
/home/jgutman/env/bin/python excel2postgres_mvesc.py



