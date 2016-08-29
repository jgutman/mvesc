library("plyr"); library("dplyr"); library("ggplot2");
library("tidyr"); library("stringr"); library("RPostgreSQL")

# getting postgres database credentials
pgpass = str_split(read.table("/mnt/data/mvesc/pgpass")[1,1], ":")[[1]]
# connecting to db
pg_db = src_postgres(dbname = pgpass[3], host = pgpass[1],
                     port = pgpass[2], user = pgpass[4], password = pgpass[5])

# function to get unique schools available and year-months available
verify_absence_file <- function(sql_tbl_ref) {
  # assumes that the table is not so large that "collecting" the data is costly
  #   thus, we do not worry that we may be "wasting" our data collection within
  #   this function
  #     assumes "School" is the column name in SQL
  schools_only_dat <- select(sql_tbl_ref, School)
  count_schools <- schools_only_dat %>% group_by(School) %>% summarise(obs_count = n()) %>%
    arrange(School)
  # print out result
  print.data.frame(collect(count_schools))
  
  # verify years of data available
  absc_dates <- collect(select(sql_tbl_ref, Date))
  if (length(unique(length(absc_dates))) == 1) {
    yr_mo_absc <- str_sub(absc_dates$Date, 1, 7)
  } else {print("Different Date Formats")}
  
  # aggregate by yr-mo
  agg_yrmo <- data_frame(date = yr_mo_absc) %>% group_by(date) %>% summarise(month_count = n())
  #   plot aggregated yrmo
  print(qplot(agg_yrmo$date, agg_yrmo$month_count) + 
          theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1)))
  # super-aggregate by years to get total count per month
  agg_yrmo <- mutate(agg_yrmo, year = str_sub(date, 1, 4))
  super_agg_yrmo <- agg_yrmo %>% group_by(year) %>% summarise(yr_count = n())
  print.data.frame(super_agg_yrmo)
}

### Verify Quality of CC-FR-RW-RV Absences ###
cc_fr_rw_rv_absences <- tbl(pg_db, "CCFRRWRVabsence09_16")
verify_absence_file(cc_fr_rw_rv_absences)

### Verify Quality of MA-TV-WM Absences ###
ma_tv_wm_absences_1516 <- tbl(pg_db, "MATVWMAbsences1516")
verify_absence_file(ma_tv_wm_absences_1516)

### Verify Quality of MA-TV-WM Absences ###
ma_tv_wm_absences_1415 <- tbl(pg_db, "MATVWMAbsences1415")
verify_absence_file(ma_tv_wm_absences_1415)
