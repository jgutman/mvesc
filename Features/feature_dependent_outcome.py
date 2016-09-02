import os, sys

pathname = os.path.dirname(sys.argv[0])
full_pathname = os.path.abspath(pathname)
split_pathname = full_pathname.split(sep="mvesc")
base_pathname = os.path.join(split_pathname[0], "mvesc")
parentdir = os.path.join(base_pathname, "ETL")
sys.path.insert(0,parentdir)
from mvesc_utility_functions import *

def add_outcome(clean_schema, model_schema):
    schema, table = argv[1], "outcome"
    source_schema, source_table = argv[0], "wrk_tracking_students"
    snapshots = "all_snapshots"
    current_year = argv[2]
    prediction_grade_range = list(range(5,10))
    prediction_outcome_name = 'future'
    # add definite_plus_ogt outcome                                     
    
    with postgres_pgconnection_generator() as connection:
        with connection.cursor() as cursor:

            cursor.execute("""                                                  
            drop table if exists ogt_temp;                                      
            create temp table ogt_temp as (                                     
            select student_lookup,                                              
              case                                                              
                when ogt_read_ss in ('DNA', 'INV', 'DNS', '99', 'TOG')          
                then null                                                       
                else cast(ogt_read_ss as int)                                   
              end,                                                              
              case                                                              
                when ogt_math_ss in ('DNA', 'INV', 'DNS', '99', 'TOG')          
                then null                                                       
                else cast(ogt_math_ss as int)                                   
              end,                                                              
              case                                                              
                when ogt_write_ss in ('DNA', 'INV', 'DNS', '99', 'TOG')         
                then null                                                       
                else cast(ogt_write_ss as int)                                  
              end,                                                              
              case                                                              
                when ogt_science_ss in ('DNA', 'INV', 'DNS', '99', 'TOG')       
                then null                                                       
                else cast(ogt_science_ss as int)                                
              end,                                                              
              case                                                              
                when ogt_socstudies_ss in ('DNA', 'INV', 'DNS', '99', 'TOG')    
                then null                                                       
                else cast(ogt_socstudies_ss as int)                             
              end                                                               
            from {s}.oaaogt                                                     
            );""".format(s=clean_schema))
            cursor.execute("""                                                  
            drop table if exists ogt_pass_temp;                                 
            create temp table ogt_pass_temp as (                                
            select student_lookup,                                              
                case                                                            
                        when ogt_read_ss > 399 then 1                           
                        else 0                                                  
                        end as ogt_read_pass,                                   
                case                                                            
                        when ogt_math_ss > 399 then 1                           
                        else 0                                                  
                        end as ogt_math_pass,                                   
                case                                                            
                        when ogt_write_ss > 399 then 1                          
                        else 0                                                  
                        end as ogt_write_pass,                                  
                case                                                            
                        when ogt_science_ss > 399 then 1                        
                        else 0                                                  
                        end as ogt_science_pass,                                
                case                                                            
                        when ogt_socstudies_ss > 399 then 1                     
                        else 0                                                  
                        end as ogt_socstudies_pass,                             
                case                                                            
                        when ogt_read_ss is not null then 1                     
                        else 0                                                  
                        end as ogt_read_took,                                   
                case                                                            
                        when ogt_math_ss is not null then 1                     
                        else 0                                                  
                        end as ogt_math_took,                                   
                case                                                            
                        when ogt_write_ss is not null then 1                    
                        else 0                                                  
                        end as ogt_write_took,                                  
                case                                                            
                        when ogt_science_ss is not null then 1                  
                        else 0                                                  
                        end as ogt_science_took,                                
                case                                                            
                        when ogt_socstudies_ss is not null then 1               
                        else 0                                                  
                        end as ogt_socstudies_took                             
            from ogt_temp);""")

            cursor.execute("""                                                  
            alter table ogt_pass_temp add num_ogt_passed int;                   
            update ogt_pass_temp set                                            
            num_ogt_passed = ogt_read_pass + ogt_math_pass + ogt_write_pass +   
            ogt_science_pass + ogt_socstudies_pass;                             
            alter table ogt_pass_temp add num_ogt_took int;                     
            update ogt_pass_temp set                                            
            num_ogt_took = ogt_read_took + ogt_math_took + ogt_write_took +     
            ogt_science_took + ogt_socstudies_took;                             
                                                                                
            -- Add passfail table to model folder                             
            
            drop table if exists {m}.ogt_passfail;                              
            create table {m}.ogt_passfail as (                                  
            select student_lookup, num_ogt_passed, num_ogt_took                 
            from ogt_pass_temp                                                  
            );""".format(m=model_schema))
            cursor.execute("""                                                  
            drop table if exists {m}.outcome_old;                               
            alter table {m}.outcome rename to outcome_old;                      
                                                                                
            create table {m}.outcome as                                         
            (select * from                                                      
            (       select *                                                    
            from {m}.outcome_old                                                
            ) as orig_outcomes                                                  
            -- ogt test info                                                    
            left join                                                           
            (   select student_lookup, max(num_ogt_passed) as num_ogt_passed,   
            max(num_ogt_took) as num_ogt_took                                   
            from {m}.ogt_passfail                                               
            group by student_lookup                                             
            ) as ogt_info                                                       
            using(student_lookup)                                               
            -- absence info                                                     
            left join                                                           
            (   select student_lookup,                                          
            max(absence_unexcused_gr_11) as absence_unexcused_gr_11,            
            max(absence_unexcused_gr_12) as absence_unexcused_gr_12             
            from {m}.absence                                                    
            group by student_lookup                                             
            ) as absence_unexcused                                              
            using(student_lookup)                                               
            -- gpa info                                                         
            left join                                                           
            (   select student_lookup, max(gpa_gr_10) as gpa_gr_10,             
            max(gpa_gr_11) as gpa_gr_11,                                        
            max(gpa_gr_12) as gpa_gr_12                                         
            from {m}.grades                                                     
            group by student_lookup                                             
            ) as grades_10_12                                                   
            using(student_lookup)                                               
            );""".format(m=model_schema))
            
            cursor.execute("""                                                  
            alter table {m}.outcome drop column if exists definite_plus_ogt;    
            alter table {m}.outcome add column definite_plus_ogt int;           
            update {m}.outcome                                                  
            set definite_plus_ogt = case                                        
                when definite = 1 then 1                                        
                when definite = 0 then 0                                        
                when outcome_category = 'uncertain' and                         
                        ((num_ogt_passed < 4 and num_ogt_took > 0) or           
                                absence_unexcused_gr_11 > 15 or                 
                                absence_unexcused_gr_12 > 15 or                 
                                gpa_gr_10 < 2 or                                
                                gpa_gr_11 < 2 or                                
                                gpa_gr_12 < 2                                   
                        ) then 1                                                
                when outcome_bucket = 'JVSD/career tech' then 1                 
                end;                                                            
                                                                                
            -- drop old outcome table                                           
            drop table {m}.outcome_old;                                         
            """.format(m=model_schema))

        connection.commit()
