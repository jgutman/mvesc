### Upload raw data (csv/excel files) to postgres

The scripts in this directory are to upload the raw data in `/mnt/data/mvesc/PartnerData/` to postgres.

#### Data sets to upload
- excel files in `/mnt/data/mvesc/PartnerData/`
- csv/txt files in `/mnt/data/mvesc/PartnerData/`
- NO `bak` files handled here; (`bak` files imported manually to postgres)

#### How to reproduce everything
- the only script to re-run: `./upload_raw_data_to_postgres.sh`
- `csv2postgres_mvesc.py` and `excel2postgres_mvesc.py` called in `./upload_raw_data_to_postgres.sh`
- `csv2postgres_mvesc.py` is to upload csv/txt files
- `excel2postgres_mvesc.py` is to upload excel files
