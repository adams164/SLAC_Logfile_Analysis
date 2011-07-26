import parsing
import processing
import analysis
import os,cPickle

base_dir="/scratch/logfile_data/"

def fullPipeline(filename,force_processing=False,force_read=False,search_data=True,result_data=True,
                IP_data=True,session_data=True,term_data=True):
    """Completely process a logfile
    
    Goes through all the steps of processing and
    analyzing a logfile, saving data at key points
    to allow easy manipulation of specific steps
    """
    spires_log=(raw_input("SPIRES style logfile(y/n)? ")!="n")
    processed_file_exists=os.path.isdir(base_dir+"proc/"+filename)
    if force_read or not processed_file_exists:
        parsing.readLogFile(base_dir+"logs/"+filename, base_dir+"proc/"+filename+"/log", spires_log)
    
    
    log_data_exists=os.path.isdir(base_dir+"data/"+filename)
    if force_processing or not log_data_exists:
        raw_data=processing.getProcessedLogs(base_dir+"proc/"+filename+"/log")
        log_data=processing.extractData(raw_data, search_data, result_data,
                                        IP_data, session_data, term_data)
        cPickle.dump(log_data,open(base_dir+"data/"+filename+"/log_data",'wb'))
    else:
        log_data=cPickle.load(open(base_dir+"data/"+filename+"/log_data",'rb'))
    
    search_data,result_data,term_data,IP_data,raw_session_data=log_data
    session_data=processing.processSessionData(raw_session_data)
    
    save_dir=base_dir+"proc_data/"+filename+"/"
    analysis.analyzeResultData(result_data, save_dir) # Broken
    analysis.analyzeIPData(IP_data, save_dir) # Broken
    analysis.analyzeSearchData(search_data, save_dir) # Processing Broken
    analysis.analyzeSessionData(session_data, save_dir)
    analysis.analyzeSpiresTermData(term_data, save_dir)
    

def main():
    """yay"""