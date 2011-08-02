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
    
    processed_file_exists=os.path.isdir(base_dir+"proc/"+filename)
    if force_read or not processed_file_exists:
        spires_log=(raw_input("SPIRES style logfile(y/n)? ")=="y")
        if not processed_file_exists:
            os.makedirs(base_dir+"proc/"+filename)
        parsing.readLogFile(base_dir+"logs/"+filename+".log", base_dir+"proc/"+filename+"/log", spires_log,True)
    
    print "Processing Log"
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
    search_ret,result_ret,term_ret,IP_ret,session_ret=[],[],[],[],[]
    #analysis.analyzeResultData(result_data_p, save_dir) # Broken
    if IP_data:
        IP_ret = analysis.analyzeIPData(IP_data_p, save_dir) # Broken
    #analysis.analyzeSearchData(search_data_p, save_dir) # Processing Broken
    if session_data:
        session_ret = analysis.analyzeSessionData(session_data_p, save_dir)
    if term_data:
        term_ret = analysis.analyzeSpiresTermData(term_data_p, save_dir)
    analysis.analyzeUsage(session_data_p, save_dir)
    print "Done"
    return (search_ret,result_ret,term_ret,IP_ret,session_ret)

def compareIPAnalysis(log1,log2):
    IP_log_1_ret = fullPipeline(log1, search_data=False, result_data=False,
                                session_data=False, term_data=False)[3]
    IP_log_2_ret = fullPipeline(log2, search_data=False, result_data=False,
                                session_data=False, term_data=False)[3]
    save_dir1=base_dir+"proc_data/"+log1+"/"
    save_dir2=base_dir+"proc_data/"+log2+"/"                            
    analysis.analyzeIPDataCompare(IP_log_1_ret, IP_log_2_ret, save_dir1, save_dir2)

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
            if segments[0]=="compareIP":
                compareIPAnalysis(segments[1], segments[2])
            elif data_set:
                for logname in segments:
                    if '-'!=logname[0]:
                        fullPipeline(logname,force_processing,
                                     force_read,search_data,result_data,IP_data,
                                     session_data,term_data,new_mapping)
            else:
                for logname in segments:
                    if '-'!=logname[0]:
                        fullPipeline(logname,force_processing=force_processing,
                                     force_read=force_read,new_mapping=new_mapping)
        input_stream=raw_input("> ")
        
        
main()