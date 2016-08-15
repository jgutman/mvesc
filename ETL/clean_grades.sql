-- **** -- **** --
-- TERM field -- The fields are either finals, periods 1-4, or semesters
--		problems: there are some empty fields that are hard to understand
--			- '' empty string?
--			- '0' field?
alter table clean.all_grades add column clean_term text;
alter table clean.all_grades alter column clean_term type text using
case
when lower(term) like '%year%final%' or  lower(term) like '%final%' or  lower(term_type) like '%final%' then 'final'
when lower(term) like '%1%sem%' then 'semester 1'
when lower(term) like '%2%sem%' then 'semester 2'
when lower(term) like '%9%week%' or lower(term) like '%nine%week%' or 
     lower(term) like '%quarter%' or lower(term) like '%grad%per%' 
     then case
     	  when lower(term) like '%1%' then 'quarter 1'	
	  when lower(term) like '%2%' then 'quarter 2'
     	  when lower(term) like '%3%' then 'quarter 3'
	  when lower(term) like '%4%' then 'quarter 4'
	  else 'quarter'
     end
when lower(term) like '%6%week%' or lower(term) like '%six%week%' 
     then case
     	  when lower(term) like '%1%' then 'six weeks 1' 
	  when lower(term) like '%2%' then 'six weeks 2' 
	  when lower(term) like '%3%' then 'six weeks 3' 
	  when lower(term) like '%4%' then 'six weeks 4' 
	  when lower(term) like '%5%' then 'six weeks 5' 
	  when lower(term) like '%6%' then 'six weeks 6' 
      end
when lower(term) in ('1st','2nd','3rd','4th') 
     and lower(term_type) = 'term' or lower(term_type) = 'quarter'
      then case 
      when lower(term) like '%1%' then 'quarter 1'
      when lower(term) like '%2%' then 'quarter 2'
      when lower(term) like '%3%' then 'quarter 3'
      when lower(term) like '%4%' then 'quarter 4'
      end
      when lower(term) in ('1st','2nd','3rd','4th') 
          and lower(term_type) = 'interim'
      then case 
 	    when lower(term) like '%1%' then 'mid-quarter 1'
	    when lower(term) like '%2%' then 'mid-quarter 2'
	    when lower(term) like '%3%' then 'mid-quarter 3'
	    when lower(term) like '%4%' then 'mid-quarter 4'
            end
        when lower(term) in ('1st','2nd','3rd','4th') 
  	 and lower(term_type) = 'exam' 
    then case 
    	 when lower(term) like '%1%' then 'exam quarter 1'
	 when lower(term) like '%2%' then 'exam quarter 2'
	 when lower(term) like '%3%' then 'exam quarter 3'
	when lower(term) like '%4%' then 'exam quarter 4'
	end
end 
--select distinct clean_term, count(clean_term) from clean.all_grades group by clean_term;

alter table clean.all_grades add column percent_of_year float;
alter table clean.all_grades alter column percent_of_year type float using
case -- 2 semesters, 4 9-weeks, 6 6-weeks in a year
     when clean_term like 'final' then 0
     when clean_term like 'exam' then 0
     when clean_term like 'semester%' then .5
     when clean_term like 'quarter%' then .25
     when clean_term like 'six weeks%' then 1/6.0
end



-- **** -- **** --
-- GRADE field -- marking what grade the student is in

alter table clean.all_grades alter column grade type int using
      case when grade like '**' then null
      when grade like '13' or grade like '14' then 23
      when grade like 'PS%' or grade like '-2%' then -1
      when grade like 'KG' then 0
      when grade like 'IN' or grade like 'DR' then null -- inactive students
      else grade::int
      end;

-- output distinct values to assess
--select distinct grade, count(grade)
--from clean.all_grades group by grade order by grade;

-- **** -- **** --
-- COURSE_NAME & COURSE_CODE -- Lots of variety here
--		Not a necessary priority currently; can wait until more focused feature creation?
--		Zhe: I think we just need to parse the course_name, the course_code is too difficult
--select distinct course_name from clean.all_grades order by course_name asc limit 150;
--select distinct course_code from clean.all_grades limit 150;

--select course_name,
--	case
--	when course_name ~* '*bio*' then 'bio'
--	when course_name ~* '*chem*' then 'chem'
--	when course_name ~* '*math*' then 'math'
--	when course_name ~* '*engl*' then 'english'
--	when course_name ~* '*chem*' then 'chem'
--	when course_name ~* '*art*' then 'art'
--	when course_name ~* '*music*' then 'music'
--	when course_name ~* '*social studies*' then 'social_studies'
--	when course_name ~* '*writing*' then 'writing'
--	when course_name ~* '*science*' then 'science'
--	when course_name ~* '*%phys ed*' then 'gym'
--	when course_name ~* '*history*' then 'gym'
--	else course_name
--	end
--	as "new_course_name"
--	from clean.all_grades where district = 'Coshocton'
--	limit 500;

-- **** -- **** --
-- MARK field --
--		If no numbers, treat as a big case statement?
--select mark, district, count(mark) from clean.all_grades where mark ~ '^[^0-9]*$' group by mark, district order by count desc;
-- 		If contains only numbers or dots, do a different operation?
--select * from clean.all_grades where mark ~ '^[0-9]*$' limit 100;
-- 		Zhe: finish the exploration in R

-- **** -- **** --
-- YEAR field -- Jackie updated to make the years into a single integer value
-- 		Convert years like 2007-08 to 2007
--alter table clean.all_grades
--	alter column school_year type int using cast(left(nullif(school_year, ''),
--				strpos(nullif(school_year, ''), '-') - 1) as integer) ;

--		Missing? There are 99,455 records with a null year field, why?
--			We need to see what information we can fill in from other sources
--select year, count(*) from clean.all_grades group by year;

alter table clean.all_grades alter column school_year type int using
substring(school_year,1,4)::int;

-- **** -- **** --
-- DISTRICT field --
-- select distinct district from clean.all_grades;
alter table clean.all_grades alter column district type text using
case when district like 'Maysville%' then 'Maysville'
     when district like 'Ridgewood%' then 'Ridgewood'
     when district like 'Franklin%' then 'Franklin'
     else district
     end;
