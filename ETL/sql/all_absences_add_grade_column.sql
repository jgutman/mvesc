/* Add column `grade` for the convenience of generating features */
---- clean.all_absences has 1.3 million rows; 
---- all_snapshots has 260 thousands rows; 
---- wrk_tracking has 12 thousand rows;
---- we don't want to join these 3 tables together!!!
 
----- alter and update temp table of all_absences
alter table clean.all_absences add column grade int default null;
update only clean.all_absences t1
	set grade = 
	(	select grade from clean.all_snapshots t2
		where grade is not null and t1.student_lookup=t2.student_lookup and 
		( 
		  (extract(year from t1.date)=t2.school_year and month>7) 
	  	  or (extract(year from t1.date)=t2.school_year+1 and month<8) 
		)
		order by grade limit 1
	);

