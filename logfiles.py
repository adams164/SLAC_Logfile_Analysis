import parsing
import processing
import analysis
import os,cPickle
import dictionaries

base_dir="/scratch/logfile_data/"

def fullPipeline(filename,force_processing=False,force_read=False,search_data=True,result_data=True,
                IP_data=True,session_data=True,term_data=True,new_mapping=False):
    """Completely process a logfile
    
    Goes through all the steps of processing and
    analyzing a logfile, saving data at key points
    to allow easy manipulation of specific steps
    """
    print "Reading Log: "+filename+".log"
    spires_log=(raw_input("SPIRES style logfile(y/n)? ")=="y")
    processed_file_exists=os.path.isdir(base_dir+"proc/"+filename)
    if force_read or not processed_file_exists:
        if not processed_file_exists:
            os.makedirs(base_dir+"proc/"+filename)
        parsing.readLogFile(base_dir+"logs/"+filename+".log", base_dir+"proc/"+filename+"/log", spires_log,True)
    
    print "Processing Log"
    log_data_exists=os.path.isdir(base_dir+"data/"+filename)
    if force_processing or not log_data_exists:
        if not log_data_exists:
            os.makedirs(base_dir+"data/"+filename)
        raw_data=processing.getProcessedLogs(base_dir+"proc/"+filename+"/log")
        log_data=processing.extractData(raw_data,base_dir+"data/"+filename+"/log_data",
                                        search_data,result_data,IP_data,
                                        session_data,term_data)
        cPickle.dump(log_data,open(base_dir+"data/"+filename+"/log_data",'wb'))
    else:
        log_data=cPickle.load(open(base_dir+"data/"+filename+"/log_data",'rb'))
    
    search_data,result_data,term_data,IP_data,session_data=log_data
    #session_data=processing.processSessionData(raw_session_data)
    
    print "Building Institution Map"
    dictionaries.getInstIPMap(IP_data[0], new_mapping)
    
    print "Analyzing Data"
    if not os.path.isdir(base_dir+"proc_data/"+filename):
        os.makedirs(base_dir+"proc_data/"+filename)
    save_dir=base_dir+"proc_data/"+filename+"/"
    #analysis.analyzeResultData(result_data, save_dir) # Broken
    #analysis.analyzeIPData(IP_data, save_dir) # Broken
    #analysis.analyzeSearchData(search_data, save_dir) # Processing Broken
    analysis.analyzeSessionData(session_data, save_dir)
    analysis.analyzeSpiresTermData(term_data, save_dir)
    print "Done"

def main(val=False):
    """Main control loop"""
    input_stream=raw_input("> ")
    while(input_stream):
        force_processing=False
        force_read=False
        search_data=False
        result_data=False
        IP_data=False
        session_data=False
        term_data=False
        new_mapping=False
        data_set=False
        if input_stream == "run":
            fullPipeline("inspire-june-2011")
        elif input_stream == "force_process":
            fullPipeline("inspire-june-2011",force_processing=True)
        else:
            segments=input_stream.split(' ')
            if "-fr" in segments:
                force_read=True
            if "-fp" in segments:
                force_processing=True
            if "-s" in segments:
                search_data=True
                data_set=True
            if "-r" in segments:
                result_data=True
                data_set=True
            if "-i" in segments:
                IP_data=True
                data_set=True
            if "-e" in segments:
                session_data=True
                data_set=True
            if "-t" in segments:
                term_data=True
                data_set=True
            if "-n" in segments:
                new_mapping=True
            if data_set:
                fullPipeline(segments[0],force_processing,
                             force_read,search_data,result_data,IP_data,
                             session_data,term_data,new_mapping)
            else:
                fullPipeline(segments[0],force_processing=force_processing,
                             force_read=force_read,new_mapping=new_mapping)
        input_stream=raw_input("> ")
        
        
main()