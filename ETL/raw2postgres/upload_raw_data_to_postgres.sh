#!/bin/bash
echo "execute bash script ..."

echo "uploading /PartnerData/teacherList06_16/ to raw ..."
/home/jgutman/env/bin/python csv2postgres_mvesc.py -d /mnt/data/mvesc/PartnerData/teacherList06_16/ -s raw

echo "uploading /PartnerData/06_16Membership/ to public ..."
/home/jgutman/env/bin/python csv2postgres_mvesc.py -d /mnt/data/mvesc/PartnerData/06_16Membership/ -s public

echo "uploading /PartnerData/06_16Membership/ to raw ..."
/home/jgutman/env/bin/python csv2postgres_mvesc.py -d /mnt/data/mvesc/PartnerData/06_16Membership/ -s raw
