library("plyr"); library("dplyr"); library("ggplot2");
library("tidyr"); library("stringr"); library("RPostgreSQL")

# getting postgres database credentials
pgpass = str_split(read.table("/mnt/data/mvesc/pgpass")[1,1], ":")[[1]]
# connecting to db
pg_db = src_postgres(dbname = pgpass[3], host = pgpass[1],
                     port = pgpass[2], user = pgpass[4], password = pgpass[5])

## June 29 2016 - Looking at tracking table ##
all_snap <- tbl(pg_db, dplyr::sql('SELECT * FROM clean.all_snapshots'))

# number of unique districts and schools per district
numSchools <- all_snap %>% group_by(district, school_name) %>% 
  summarise(count = n()) %>% arrange(district, count)

# disadvantagement across districts
perSchoolDis <- all_snap %>% group_by(district, school_year, disadvantagement) %>%
  summarise(count = n())
perSchoolDis <- collect(perSchoolDis)
totStudents <- all_snap %>% group_by(district, school_year) %>% summarise(count = n())
totStudents <- collect(totStudents)
totStudents <- rename(totStudents, totStud = count)
perSchoolDis <- full_join(perSchoolDis, totStudents, by = c("district", 'school_year'), copy = T)
perSchoolDis <- mutate(perSchoolDis, disAdvantagePerCapita = count / totStud)
perSchoolDis <- replace_na(perSchoolDis, replace = list(disadvantagement = 'missing'))
ggplot(filter(perSchoolDis, disadvantagement %in% c('economic', 'academic', 'both', 'none')), 
       aes(x = factor(school_year), y = disAdvantagePerCapita, color = disadvantagement, group = disadvantagement)) +
  geom_line() + geom_point() + facet_wrap(~ district) + ggtitle("Economic & Academic Disadvantagement\nOver Time Per District") + 
  ylab("Percent of Total Students (%)")
  ggsave('mvesc/Descriptives/general_summary/disadvantagement_over_time.png', w = 9, h = 8)

  
# disability across districts
perSchoolDis <- all_snap %>% group_by(district, school_year, disability) %>%
  summarise(count = n())
perSchoolDis <- collect(perSchoolDis)
perSchoolDis <- full_join(perSchoolDis, totStudents, by = c("district", 'school_year'), copy = T)
perSchoolDis <- mutate(perSchoolDis, disabilityPerCap = count / totStud)
perSchoolDis <- replace_na(perSchoolDis, replace = list(disability = 'missing'))
ggplot(filter(perSchoolDis, ! disability %in% c('missing', 'none') & disabilityPerCap >= 0.02),
       aes(x = factor(school_year), y = disabilityPerCap, color = disability, group = disability)) +
  geom_line() + geom_point() + facet_wrap(~ district) + ggtitle("Disability Over Time Per District") + 
  ylab("Percent of Total Students (%)")
ggsave('mvesc/Descriptives/general_summary/disability_over_time.png', w = 9, h = 8)

# student statuses across districts
studentStatuses <- all_snap %>% group_by(district, school_year, status) %>%
  summarise(count = n())
studentStatuses <- collect(studentStatuses)
studentStatuses <- full_join(studentStatuses, totStudents, by = c("district", 'school_year'), copy = T)

studentStatuses <- mutate(studentStatuses, perCapita = count / totStud)
studentStatuses <- replace_na(studentStatuses, replace = list(status = 'missing'))

ggplot(filter(studentStatuses, perCapita > 0.02),
       aes(x = factor(school_year), y = perCapita, color = status, group = status)) +
  geom_line() + geom_point() + facet_wrap(~ district) + ggtitle("Student Status Over Time Per District (>2% occurrence)") + 
  ylab("Percent of Total Students (%)")
ggsave('mvesc/Descriptives/general_summary/status_over_time.png', w = 9, h = 8)

