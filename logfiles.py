import parsing
import processing
import analysis
from analysisFunctions import *
import os,cPickle
import dictionaries
import sys

base_dir="/scratch/logfile_data/"


def fullPipeline(filename,force_processing=False,force_read=False,search_data=True,result_data=True,
                IP_data=True,session_data=True,term_data=True,usage_data=True,new_mapping=False,
                timescale="Days",date_start="",date_end="",ffp=False,ffr=False):
    """Completely process a logfile
    
    Goes through all the steps of processing and
    analyzing a logfile, saving data at key points
    to allow easy manipulation of specific steps
    """
    force_full_processing=ffp
    force_full_read=ffr
    print "Reading Log: "+filename
    
    file_hold = filename
    
    if filename=="SPIRES" and date_start=="20110601":
        date_start="20110602"
    
    if filename=="INSPIRE" or filename=="SPIRES":
        start_file_exists=os.path.isfile(base_dir+"proc/"+filename+"/log."+date_start)
        end_file_exists=os.path.isfile(base_dir+"proc/"+filename+"/log."+date_end)
        processed_file_exists=start_file_exists and end_file_exists
        if force_read or not processed_file_exists:
            if not os.path.isdir(base_dir+"proc/"+filename):
                os.makedirs(base_dir+"proc/"+filename)
            parsing.readLogFileByDay(filename,base_dir+"logs/",
                                     base_dir+"proc/"+filename+"/log",
                                     date_start,date_end,force_full_read)
    else:
        processed_file_exists=os.path.isdir(base_dir+"proc/"+filename)
        if force_read or not processed_file_exists:
            spires_log=(raw_input("SPIRES style logfile(y/n)? ")=="y")
            if not processed_file_exists:
                os.makedirs(base_dir+"proc/"+filename)
            parsing.readLogFile(base_dir+"logs/"+filename+".log", base_dir+"proc/"+filename+"/log", spires_log)
    
    print "Processing Log"
    if filename=="INSPIRE" or filename=="SPIRES":
        start_file_exists=os.path.isfile(base_dir+"data/"+filename+"/log_data."+date_start)
        end_file_exists=os.path.isfile(base_dir+"data/"+filename+"/log_data."+date_end)
        log_data_exists=start_file_exists and end_file_exists
        file_count=0
        if force_processing or not log_data_exists:
            if not os.path.isdir(base_dir+"data/"+filename):
                os.makedirs(base_dir+"data/"+filename)
            log_data=[]
            file_listing=sorted(os.listdir(base_dir+"proc/"+filename))
            for log_file in file_listing:
                if log_file>="log."+date_start and log_file<="log."+date_end:
                    file_count+=1
                    file_date=log_file[4:]
                    if file_count%15==0:
                        print "Loaded "+str(file_count)+" files"
                    if force_full_processing or not os.path.isfile(base_dir+"data/"+filename+"/log_data."+file_date):
                        raw_data=processing.readDataFile(base_dir+"proc/"+filename+"/"+log_file)
                        data_out = (processing.extractData(raw_data,base_dir+"data/"+filename+"/log_data."+file_date,
                                                        search_data,result_data,IP_data,
                                                        session_data,term_data,True))
                        cPickle.dump(data_out,open(base_dir+"data/"+filename+"/log_data."+file_date,'wb'))
                    else:
                        data_out = log_data.append(cPickle.load(open(base_dir+"data/"+filename+"/"+log_file,'rb')))
                    log_data.append(data_out)
                    #processing.writeDataParts(log_data,base_dir+"data/"+filename+"/log_data")
        else:
            log_data=[]
            file_listing=sorted(os.listdir(base_dir+"data/"+filename))
            for log_file in file_listing:
                if log_file>="log_data."+date_start and log_file<="log_data."+date_end:
                    file_count+=1
                    if file_count%15==0:
                        print "Loaded "+str(file_count)+" files"
                    log_data.append(cPickle.load(open(base_dir+"data/"+filename+"/"+log_file,'rb')))
        log_data=flattenTwoDeep(log_data)
        search_data_p=log_data[0]
        result_data_p=log_data[1]
        term_data_p=log_data[2]
        IP_data_p=log_data[3]
        session_data_p=log_data[4][0]
        num_days=log_data[4][1]
        print num_days
        #session_data=processing.processSessionData(raw_session_data)
        #session_data_p=[session for part in session_data_parts for session in part]
        
    else:
        log_data_exists=os.path.isdir(base_dir+"data/"+filename)
        if force_processing or not log_data_exists:
            if not log_data_exists:
                os.makedirs(base_dir+"data/"+filename)
            raw_data=processing.readDataFile(base_dir+"proc/"+filename+"/log")
            log_data=processing.extractData(raw_data,base_dir+"data/"+filename+"/log_data",
                                            search_data,result_data,IP_data,
                                            session_data,term_data)
            #cPickle.dump(log_data,open(base_dir+"data/"+filename+"/log_data",'wb'))
            processing.writeDataParts(log_data,base_dir+"data/"+filename+"/log_data")
        else:
            log_data=processing.readDataFile(base_dir+"data/"+filename+"/log_data")

        
    
        search_data_p=log_data[0]
        result_data_p=log_data[1]
        term_data_p=log_data[2]
        IP_data_p=log_data[3]
        session_data_parts=log_data[4:]
        #session_data=processing.processSessionData(raw_session_data)
        session_data_p=[session for part in session_data_parts for session in part]
        
    
    print "Building Institution Map"
    dictionaries.getInstIPMap(IP_data_p[0], new_mapping)
    
    print "Analyzing Data"
    if not os.path.isdir(base_dir+"proc_data/"+filename):
        os.makedirs(base_dir+"proc_data/"+filename)
    save_dir=base_dir+"proc_data/"+filename+"/"
    search_ret,result_ret,term_ret,IP_ret,session_ret,usage_ret=[],[],[],[],[],[]
    #analysis.analyzeResultData(result_data_p, save_dir) # Broken
    if IP_data:
        IP_ret = analysis.analyzeIPData(IP_data_p, save_dir) # Broken
    #analysis.analyzeSearchData(search_data_p, save_dir) # Processing Broken
    if session_data:
        session_ret = analysis.analyzeSessionData(session_data_p, save_dir)
    if term_data:
        term_ret = analysis.analyzeSpiresTermData(term_data_p, save_dir)
    if usage_data:
        usage_ret = analysis.analyzeUsage(session_data_p, save_dir,timescale)
    print "Done"
    return (search_ret,result_ret,term_ret,IP_ret,session_ret,usage_ret)

def compareIPAnalysis(log1,log2):
    IP_log_1_ret = fullPipeline(log1, search_data=False, result_data=False,
                                session_data=False, term_data=False)[3]
    IP_log_2_ret = fullPipeline(log2, search_data=False, result_data=False,
                                session_data=False, term_data=False)[3]
    save_dir1=base_dir+"proc_data/"+log1+"/"
    save_dir2=base_dir+"proc_data/"+log2+"/"
    analysis.analyzeIPDataCompare(IP_log_1_ret, IP_log_2_ret, save_dir1, save_dir2)

def compareUsageAnalysis(log1,log2,timescale,date_start='',date_end=''):
    usage_log_1_ret = fullPipeline(log1, IP_data=False, search_data=False, result_data=False,
                                session_data=False, term_data=False,timescale=timescale,
                                date_start=date_start,date_end=date_end)[5]
    usage_log_2_ret = fullPipeline(log2, IP_data=False, search_data=False, result_data=False,
                                session_data=False, term_data=False,timescale=timescale,
                                date_start=date_start,date_end=date_end)[5]
    save_dir1=base_dir+"proc_data/"+log1+"/"
    save_dir2=base_dir+"proc_data/"+log2+"/"
    analysis.compareUsage(usage_log_1_ret,usage_log_2_ret,
                          save_dir1, save_dir2, timescale)

def compare(filename1,filename2,force_processing,
            force_read,search_data,result_data,IP_data,
            session_data,term_data,usage_data,new_mapping,timescale,
            date_start,date_end,force_full_processing,force_full_read,
            usage,IP):
    log_1_data = fullPipeline(filename1, force_processing, force_read,
                              search_data, result_data, IP_data,
                              session_data, term_data, usage_data,
                              new_mapping, timescale, date_start,
                              date_end, force_full_processing, force_full_read)
    log_2_data = fullPipeline(filename2, force_processing, force_read,
                              search_data, result_data, IP_data,
                              session_data, term_data, usage_data,
                              new_mapping, timescale, date_start,
                              date_end, force_full_processing, force_full_read)
    save_dir1=base_dir+"proc_data/"+filename1+"/"
    save_dir2=base_dir+"proc_data/"+filename2+"/"
    if usage:
        analysis.compareUsage(log_1_data[5],log_2_data[5],
                              save_dir1, save_dir2, timescale)
    if IP: 
        analysis.analyzeIPDataCompare(log_1_data[3], log_2_data[3],
                                      save_dir1, save_dir2)
    analysis.compareSessionData(log_1_data[4], log_2_data[4],
                                save_dir1, save_dir2)

def evalArgs(segments):
        force_processing=False
        force_read=False
        force_full_processing=False
        force_full_read=False
        search_data=False
        result_data=False
        IP_data=False
        usage_data=False
        session_data=False
        term_data=False
        new_mapping=False
        data_set=False
        date_start="19910416"
        date_end="21640101"
        timescale="Weeks"
        if "-date-start" in segments:
            date_start=segments[segments.index("-date-start")+1]
        if "-date-end" in segments:
            date_end=segments[segments.index("-date-end")+1]
        if "-timescale" in segments:
            timescale=segments[segments.index("-timescale")+1]
        if "-fr" in segments:
            force_read=True
        if "-fp" in segments:
            force_processing=True
        if "-ffr" in segments:
            force_full_read=True
            force_read=True
        if "-ffp" in segments:
            force_processing=True
            force_full_processing=True
        if "-s" in segments:
            search_data=True
            data_set=True
        if "-r" in segments:
            result_data=True
            data_set=True
        if "-i" in segments:
            IP_data=True
            data_set=True
        if "-u" in segments:
            usage_data=True
            data_set=True
        if "-e" in segments:
            session_data=True
            data_set=True
        if "-t" in segments:
            term_data=True
            data_set=True
        if "-n" in segments:
            new_mapping=True
        if segments[0]=="compareIP":
            compareIPAnalysis(segments[1], segments[2])
        elif segments[0]=="compareUsage":
            compareUsageAnalysis(segments[1],segments[2],timescale,date_start,date_end)
        elif segments[0]=="compare":
            if not data_set:
                search_data,result_data,IP_data,session_data,term_data,usage_data=True,True,True,True,True,True
            compare(segments[1],segments[2],force_processing,
                    force_read,search_data,result_data,IP_data,
                    session_data,term_data,usage_data,new_mapping,timescale,
                    date_start,date_end,force_full_processing,force_full_read,
                    usage_data,IP_data)
        elif segments[0]=="INSPIRE" or segments[0]=="SPIRES":
            if not data_set:
                search_data=result_data=IP_data=session_data=term_data=usage_data=True
            fullPipeline(segments[0],force_processing,
                         force_read,search_data,result_data,IP_data,
                         session_data,term_data,usage_data,new_mapping,timescale,
                         date_start,date_end,force_full_processing,force_full_read)                
        elif data_set:
            for logname in segments:
                if '-'!=logname[0]:
                    fullPipeline(logname,force_processing,
                                 force_read,search_data,result_data,IP_data,
                                 session_data,term_data,usage_data,new_mapping,
                                 ffp=force_full_processing,ffr=force_full_read)
        else:
            for logname in segments:
                if '-'!=logname[0]:
                    fullPipeline(logname,force_processing=force_processing,
                                 force_read=force_read,new_mapping=new_mapping,
                                 ffp=force_full_processing,ffr=force_full_read)

def main(val=False):
    """Main control loop"""
    input_stream=raw_input("> ")
    while(input_stream):
        segments=input_stream.split(' ')
        evalArgs(segments)
        input_stream=raw_input("> ")
        
segments = sys.argv[1:]
if segments:
    evalArgs(segments)
else:
    main()