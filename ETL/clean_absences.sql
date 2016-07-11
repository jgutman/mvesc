/*
 * This series of SQL commands is the ingredients for cleaning up the all_absences table
 * It contains the appropriate case statements and choices
 * It DOES NOT the actual creation of the tables yet though
 * These commands can be copied into a bigger script or transformed into a SQL script
 */

-- StudentLookup Column -- Assume this is fine
--		this is a quick visual check
--		there are no empty student lookup numbers
select count(*) from clean.all_absences where student_lookup is null;

-- Date Column -- This needs a simple date conversion function
ALTER TABLE clean.all_absences
	ALTER COLUMN date type date using to_date(date, 'YYYY-MM-DD');

-- Absence Length -- These only take on 3 distinct and sensible values, so don't need any changes
--		this is a quick visual check
select distinct absence_length from clean.all_absences;

-- Absence Codes -- These are actually being IGNORED because we're using absence descriptions only
--        there is no 1-to-1 mapping between absence codes & descriptions, they vary by school
--select distinct absence_code, absence_desc, school from clean.all_absences sorted order by absence_desc;
	
-- Absence Descriptions -- These provide the information to clean and standardize the descriptions
--		In this code, none of the descriptions repeat, they are all collected in one place and
--		They are attempted to be grouped in groups of similar descriptions
-- 		This list can be aggregated further
--          	Future: Consider using Hanna's JSON format for case statement 
update only clean.all_absences
set
	absence_desc =
		case
		-- ** popular values near the top for speed ** --
		-- > 20k -- general absences or tardies --
		when Lower(absence_desc) in
			('authoried absence', 'authorized absence', 'excused absence',
			'excused absence - formally authorized', 'approved absence') 
			then 'absence_excused'
		when Lower(absence_desc) in 
			('unexcused absence', 'unauthorized', 'unauthorized absence',
			'unexcused absence - formally unauthorized')
			then 'absence_unexcused'
		when Lower(absence_desc) in 
			('all day absent', 'absent') 
			then 'absence_all_day'
			
		when Lower(absence_desc) in 
			('unexcused tardy', 'tardy', 'tardy to school', 'tardy no med.')
			then 'tardy_unexcused'
		when Lower(absence_desc) = 'tardy excu.'
			then 'tardy_excused'
		when Lower(absence_desc) in ('arrive late but not tardy', 'arrive late to school but not tardy')
			then 'arrive_late_not_tardy'
		
		-- 20k to 10k obs --
		when Lower(absence_desc) in ('all day med. ex./legal', 'all day med./leg ex')
			then 'med_legal_all_day'
		when Lower(absence_desc)  in ('am med. ex./legal', 'am med/leg ex', 'ame med/leg excused')
			then 'med_legal_am'
		when Lower(absence_desc)  in ('pm med. ex./legal', 'pm med./legal ex.')
			then 'med_legal_pm'
		when Lower(absence_desc) = 'late arrival to school due to an appt.' 
			then 'tardy_medical'
		-- 		keep medical separate from med_legal because it might send a more specific signal
		when Lower(absence_desc) in ('medical', 'doctor with instruction')
			then 'medical'
		
		when Lower(absence_desc) in ('school related', 'school related/activity', 'sr school related') 
			then 'misc'
		when Lower(absence_desc) = 'not counted absent'
			then 'not_counted_absent'
		
		-- 10k to rest --
				
		-- partial absences
		when Lower(absence_desc) = 'am absent' then 'am_absent'
		when Lower(absence_desc) = 'pm absent' then 'pm_absent'
		when Lower(absence_desc) = 'returned' then 'departed_will_return'
		when Lower(absence_desc) in ('departed/will return')
			then 'departed_will_return'
		when Lower(absence_desc) in ('left early', 'left school early') 
			then 'left_early'
		when absence_code = 'PM T' -- assuming just missing a description 
			then 'left_early'
		
		-- educational
		when Lower(absence_desc) in 
			('alt school', 'attending alternative school/educated', 'alternative school', 'alternate school')
			then 'alternative_school'
		when Lower(absence_desc) in ('home instruction', 'home instruction pm') 
			then 'home_instruction'
		when Lower(absence_desc) = 'testing' then 'testing'
		
		-- early dismissals
		when Lower(absence_desc) = 'approved early dismissal' then 'early_dismiss_approved'
		when Lower(absence_desc) in ('early dis non absence', 'early dis non-absence', 'early dismissal',
			'early dismissal non absence', 'early dismissal non-absence') then 'early_dismiss'
		when absence_code = 'EM' then 'early_dismiss' -- assume this is a typo for 'EN' code
		
		-- non-curricular activities
		when Lower(absence_desc) in ('college day', 'college visit') then 'college_day'
		when Lower(absence_desc) in ('court', 'court with instruction') then 'court'
		when Lower(absence_desc) = 'field trip' then 'field_trip'
		when Lower(absence_desc) = 'religious' then 'religious'
		when Lower(absence_desc) = 'mat/child' then 'mat_child'
		when Lower(absence_desc) = 'no power' then 'no_power'
		when Lower(absence_desc) = 'school transportation' then 'school_transport_issue'
		
		-- disciplinary
		--		suspension
		when Lower(absence_desc) in ('suspension', 'suspension from school') 
			then 'suspension'
		when Lower(absence_desc) in ('educated suspension', 'suspension from school -instructed (board approved)') 
			then 'suspension_educated'
		when Lower(absence_desc) in 
			('in school suspension', 'in-school suspension', 'in school suspension--non absence', 
			'suspension - in school', 'suspension held at the high school') 
			then 'suspension_in_school'
		when Lower(absence_desc) = 'out-school suspension' 
			then 'suspension_out_school'
		when absence_code = 'I' -- assume this based on the common occurrences with most schools
			then 'suspension_in_school' 
		--		explusion
		when Lower(absence_desc) in ('student expulsion', 'expulsion/in-school instruction') 
			then 'expulsion'
		--		detention & jdc
		when Lower(absence_desc) = 'in school detention' 
			then 'detention'
		when Lower(absence_desc) in ('jdc', 'juvenile detention center') 
			then 'jdc'
		
		-- misc
		when Lower(absence_desc) = 'any b115 absent' then 'misc'
		when Lower(absence_desc) = 'not 1 of 10 absences' then 'misc' -- not sure how to interpret this
		when Lower(absence_desc) = 'other placement' then 'misc' -- seems to be miscellany category
		when absence_code = 'N' then 'missing_desc' -- likely 'not counted absent' based on other schools, likely not serious
		
		else 'CANNOT_FIND_CHECK_VALUES'
		end;

-- Show the distinct outcomes to ensure this worked correctly
--		this is a quick visual check
select distinct absence_desc from clean.all_absences;

-- School Abbreviations -- These all look fine, except one school which spread the
--		absence description across these two columns and the school code is missing.
--		We could do a exhaustive search to identify which school this is
--		BUT this hasn't been done yet.
--			Should be investigated if possible
--		this is a quick visual check
select school, count(school) from clean.all_absences group by school order by count asc;
