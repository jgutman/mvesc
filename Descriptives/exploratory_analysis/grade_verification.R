library("plyr"); library("dplyr"); library("ggplot2");
library("tidyr"); library("stringr"); library("RPostgreSQL")

# getting postgres database credentials
pgpass = str_split(read.table("/mnt/data/mvesc/pgpass")[1,1], ":")[[1]]
# connecting to db
pg_db = src_postgres(dbname = pgpass[3], host = pgpass[1],
                     port = pgpass[2], user = pgpass[4], password = pgpass[5])

# Goal: Verify that the grades data we received is valid and doesn't have glaring errors

# get references to each of these districts
csch_grades <- tbl(pg_db, 'CoshoctonGrades2006_16')
frank_grades <- tbl(pg_db, 'Franklingrades2006_16')
mays_grades <- tbl(pg_db, 'Maysvillegrades2006_16')
ridge_grades <- tbl(pg_db, 'Ridgewoodgrades2007_2016')
west_grades <- tbl(pg_db, 'WestMuskingumgrades2006_16')
rv_grades <- tbl(pg_db, 'RiverViewgrades2006_16')
tv_grades <- tbl(pg_db, 'TriValleyGrades2006_16')

# function to verify and get simple summaries of each table
verify_grades <- function(sql_table) {
  # report summary of grade-levels in the district
  agg_grade <- sql_table %>% group_by(Grade) %>% summarise(grade_count = n()) %>%
    arrange(Grade)
  agg_grade <- collect(agg_grade)
  print.data.frame(agg_grade)
  qplot(agg_grade$Grade, agg_grade$grade_count)
  
  # report summary of school years in the district
  agg_year <- sql_table %>% group_by(Schoolyear) %>% summarise(count = n()) %>%
    arrange(Schoolyear)
  agg_year <- collect(agg_year)
  print.data.frame(agg_year)
  qplot(agg_year$Schoolyear, agg_year$count)
  print(min(agg_year$count)); print(max(agg_year$count))
  
  # report summary of terms in the district
  agg_num <- sql_table %>% group_by(term) %>% summarise(count = n()) %>%
    arrange(count)
  agg_num <- collect(agg_num)
  print.data.frame(agg_num)
  
  # Top 25 summary of marks in the district
  agg_num <- sql_table %>% group_by(Mark) %>% summarise(count = n()) %>%
    arrange(desc(count))
  agg_num <- head(agg_num, 25)
  print("Top 25 common marks")
  print.data.frame(agg_num)
  # Top 25 summary of marks in the district
  agg_num <- sql_table %>% group_by(Course) %>% summarise(count = n()) %>%
    arrange(desc(count)) %>% top_n(25)
  print("Top 25 common Course Codes")
  print.data.frame(collect(agg_num))
  # Top 25 summary of marks in the district
  agg_num <- sql_table %>% group_by(Cname) %>% summarise(count = n()) %>%
    arrange(desc(count)) %>% top_n(50)
  print("Top 50 common Course Names")
  print.data.frame(collect(agg_num))
  # Top 25 summary of lookups in the district
  agg_num <- sql_table %>% group_by(StudentLookup) %>% summarise(count = n()) %>%
    arrange(desc(count)) %>% top_n(25)
  print("Top 25 lookups")
  print.data.frame(collect(agg_num))
}

verify_grades(csch_grades)
verify_grades(frank_grades)
verify_grades(mays_grades)
verify_grades(ridge_grades)
verify_grades(west_grades)
verify_grades(rv_grades)
verify_grades(tv_grades)
