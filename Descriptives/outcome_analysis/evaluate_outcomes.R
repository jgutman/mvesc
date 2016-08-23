library("plyr"); library("dplyr"); library("ggplot2");
library("tidyr"); library("stringr"); library("RPostgreSQL")
library("lazyeval")
# getting postgres database credentials
pgpass = str_split(read.table("/mnt/data/mvesc/pgpass")[1,1], ":")[[1]]
# connecting to db
pg_db = src_postgres(dbname = pgpass[3], host = pgpass[1],
                     port = pgpass[2], user = pgpass[4], password = pgpass[5])

# load db
tracking = tbl(pg_db, dplyr::sql('SELECT * FROM clean.wrk_tracking_students'))

setwd('~/mvesc/Descriptives/outcome_analysis/')

buckets = tracking %>% filter(!is.na(outcome_bucket))
buckets = collect(buckets)

a = buckets %>% group_by(outcome_bucket, outcome_category) %>% summarise(count = n()) %>%
  arrange(desc(count))
print(a, n = 30)


### Compare to OAA scores
oaaogt = tbl(pg_db, dplyr::sql('select * from clean.oaaogt'))
ogt = oaaogt %>% select(one_of('student_lookup'), starts_with('ogt'))
ogt_raw = collect(ogt)
# get list of tests
list_of_ogt_tests = str_sub(colnames(ogt_raw)[-1], 0, -4) %>%
  unique()

# intialize clean ogt table
ogt_clean = data.frame(student_lookup = unique(ogt_raw['student_lookup']))

# convert ogt to numeric
for (test in list_of_ogt_tests){
  print(test)
  ogt_raw[paste0(test, '_ss')] <- as.numeric(mapvalues(ogt_raw[[paste0(test, '_ss')]],
                                                       c('DNA', 'INV', 'DNS', '99', 'TOG'),
                                                       rep(NA, 5)))
}
for (test in list_of_ogt_tests){
  # keep the rows only with the max score by group
  ogt_clean <- ogt_clean %>% left_join(ogt_raw %>% select_(paste0(test, '_ss'),
                                                           paste0(test, '_pl'),
                                                           "student_lookup") %>%
                                         group_by(student_lookup) %>%
                                         slice_(interp(~which.max(v), v = as.name(paste0(test, '_ss')))),
                                       by = 'student_lookup')
}

# keep only ogt that have students in outcomes
ogt = left_join(select(buckets, student_lookup,
                       outcome_bucket,
                       outcome_category), ogt_clean,
                by = 'student_lookup')

# plot bucket by ogt_read_ss
ogt_fewer = filter(ogt, outcome_category %in% c("on-time", "dropout",
                                                "uncertain")) %>%
  select(-ends_with('_pl'))

long_ogt = gather(ogt_fewer, test_name, score, ogt_read_ss:ogt_socstudies_ss)

ggplot(long_ogt, aes(x = score, color = outcome_bucket)) + geom_density() +
  facet_wrap(~test_name, ncol = 1)

ggsave(filename = 'density_of_ogt_scores_by_bucket.pdf', w = 8, h = 8)

# NOTE: 400 is a passing score for each section!
# can we do some sort of separation based on that?

### ACTION
# Count the number of tests passed by the unknown students.
# If this is less than 3 (?), count uncertain students as dropouts?
# Improvement: count the number they took too
###


#### Absences vs Buckets ###
tracking = tbl(pg_db, dplyr::sql('SELECT * FROM clean.wrk_tracking_students'))
buckets = tracking %>% filter(!is.na(outcome_bucket),
                              outcome_category %in% c('on-time',
                                                      'dropout',
                                                      'uncertain',
                                                      'jv')) %>%
  select(student_lookup, outcome_bucket, outcome_category)
# absences
absence_ref = tbl(pg_db, dplyr::sql('SELECT * FROM model.absence'))
absences = absence_ref %>% select(student_lookup, matches('gr_10|gr_11|gr_12'))
# left join the two to get the result
abs = buckets %>% left_join(absences, by = 'student_lookup')
#
abs = collect(abs)
# plot abs
long_abs = abs %>% select(student_lookup:tardy_consec_gr_12) %>%
  gather(type, freq, absence_gr_10:tardy_consec_gr_12)
# split by grade
long_abs_gr = separate(long_abs, type, c('type', 'grade_level'),
                       sep = c(-3))
# plot absences
ggplot(filter(long_abs_gr, freq > 0,
              type %in% c('absence_consec_gr_',
                          'absence_unexcused_gr_',
                          'tardy_consec_gr_',
                          'tardy_unexcused_gr_'),
              grade_level != '10'
              ), aes(x = freq, color = outcome_category, fill = outcome_category)) + 
  geom_density(alpha = 0.15) + theme_bw() + ylim(0, 0.055) +
  facet_grid(grade_level~type, scales = "free_x") + 
  ggtitle("Grade 11/12 Absences w/capped y-axis")

ggsave(filename = 'absences_gr_11_12_by_bucket.pdf', w = 8, h = 8)

# looking by weekdays
weekdays = abs %>% select(student_lookup, outcome_bucket, outcome_category,
                          absence_wkd_1_gr_10:tardy_wkd_1_gr_12) %>%
  gather(type, freq, absence_wkd_1_gr_10:tardy_wkd_1_gr_12)

gr11_g30 = filter(long_abs_gr, freq > 30,
                  type %in% c('absence_consec_gr_',
                              'absence_unexcused_gr_',
                              'tardy_consec_gr_',
                              'tardy_unexcused_gr_'),
                  grade_level == '11')

ggplot(filter(weekdays, freq > 0),
       aes(x = freq, color = outcome_category, fill = outcome_category)) +
  geom_density(alpha = 0.15) + theme_bw() + ylim(0, 0.2) + 
  facet_wrap(~type, scales = 'free_x')

#### GRADES VS BUCKETS ####
# use buckets same as previous
grade_ref = tbl(pg_db, dplyr::sql('SELECT * FROM model.grades'))
grades = grade_ref %>% select(student_lookup, matches('gr_10|gr_11|gr_12')) %>%
  select(student_lookup, starts_with('gpa_'))

grd = buckets %>% left_join(grades, by = 'student_lookup')

grd = collect(grd)

long_grd = gather(grd, grade_level, gpa, gpa_gr_10:gpa_district_gr_12)

ggplot(long_grd,
       aes(x = gpa, color = outcome_bucket)) +
  geom_density(alpha = 0.4) + facet_wrap(~grade_level, scale = "free_x")

ggsave(filename = 'overall_gpa_by_outcome_bucket.pdf', w = 8, h = 8)
