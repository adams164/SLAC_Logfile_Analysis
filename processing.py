import re, cPickle, time, datetime, os
from invenio.bibindex_engine_tokenizer import BibIndexFuzzyNameTokenizer as FNT
import GeoIP

NameScanner = FNT()
SEARCH_LEAD = re.compile('GET /search?')
SEARCH = re.compile('(p|p1)=(?P<term>.*?)(&| )')
ANY_AUTH = re.compile('(a|author|au)(:| )')
TITLE = re.compile('(t|title)(:| )')

GOOGLEBOT = re.compile('ooglebot')
gi=GeoIP.new(GeoIP.GEOIP_MEMORY_CACHE)

AUTHOR_ID = re.compile('(.[.])(.[.])?(?P<lastname>.*?)([.][0-9]+)')

AUTH_NAME = re.compile('([^,] |^)(ea|a|author|au)(:| )(?P<name>.*?)(?= not | or | and |$)')
AUTH_NAME_OLD = re.compile('(a|author|au)(:| )(?P<name>.*?)(?= not | or | and |$)')

TITLE_NAME = re.compile('([^,] |^)(t|title)(:| )(?P<title>.*?)(?= not | or | and |$)')

EPRINT = re.compile('(\d{4}[.]\d{4}|\w+\-\w+\/\d{7})')

#DIRECTORY = re.compile('\/[^\/]+$')
import dictionaries
_SPIRES_TO_INVENIO_KEYWORDS_MATCHINGS = dictionaries.StI

def getProcessedLogs(read_from):
    """Read in the logfile data from pickle files"""
    data_list=[]
    #read_from = raw_input("Read Data From: ")
    single_file = os.path.isfile(read_from)
    #file_read_from=os.path.split(read_from)[1]
    if single_file:
        data_list.append(cPickle.load(open(read_from, 'rb')))
    else:
        file_parts=os.path.split(read_from)
        list_files=os.listdir(file_parts[0])
        for filename in list_files:
            if filename.find(file_parts[1]+'.') == 0:
                print "reading "+filename
                data_list.append(cPickle.load(open(file_parts[0]+'/'+filename,'rb')))
    return data_list



def extractData(data_list,search_data=True,result_data=True,
                IP_data=True,session_data=True,term_data=True):
    """Turn the logfile data into usable formats
    
    The five flags for extractData determine which
    steps of the processing will take place. Search
    data is currently broken--died with country 
    analysis.
    """
    eprint_dict={}
    authors_dict={}
    title_dict={}
    
    result_list=[]
    author_result_list=[]
    title_result_list=[]
    eprint_result_list=[]
    
    ip_listing={}
    searches=0
    ip_listpair=[]
    ip_active={}
    number=1
    timeout=5
    spires_terms={}
    spires_term_count=0
    session_timeout=datetime.timedelta(minutes=timeout)
    ip_ignore = dictionaries.ip_ignore#session_list=[]
    
    for data in data_list:
        print "running file " +str(number)
        number+=1
        for entry in data:
            
            ip = entry[0]
            if ip in ip_ignore:
                continue
            search_term = entry[1]
            results = int(entry[2])
            try:
                date = datetime.datetime(*(time.strptime(entry[3],"%d/%b/%Y:%H:%M:%S")[0:6]))
            except ValueError:
                date = datetime.datetime(*(time.strptime(entry[3],"%Y%m%d %H:%M:%S")[0:6]))
            referrer = entry[4]
            
            
            
            # Search results data recording
            if result_data:
                result_list.append(results)
                            
                if AUTH_NAME.search(search_term):
                    author_result_list.append(results)
                
                if TITLE_NAME.search(search_term):
                    title_result_list.append(results)
            
                if EPRINT.search(search_term):
                    eprint_result_list.append(results)           
                
                searches+=1
            
            
            # SPIRES search terms data recording
            if term_data:
                bits = search_term.split('( in hep')[0].split(' ')
                for word in bits:
                    if word in _SPIRES_TO_INVENIO_KEYWORDS_MATCHINGS:
                        spires_term_count+=1
                        term=_SPIRES_TO_INVENIO_KEYWORDS_MATCHINGS[word]
                        if term in spires_terms:
                            spires_terms[term]+=1
                        else:
                            spires_terms[term]=1
                            
            # Session data recording            
            # Session format: [ip,start_time,[(query,time),(query,time),...],end_time]
            if session_data:
                if ip in ip_active:
                    time_dif = abs(date-ip_active[ip][1])
                    if time_dif > session_timeout:
                        ip_listpair.append((ip,ip_active[ip][0],ip_active[ip][1],ip_active[ip][2],ip_active[ip][3],ip_active[ip][4]))
                        ip_active[ip]=[0,date,date,referrer,[(search_term,date)]]
                    else:
                        ip_active[ip][0]+=1
                        ip_active[ip][1]=date
                        ip_active[ip][4].append((search_term,date))
                else:
                    ip_active[ip]=[0,date,date,referrer,[(search_term,date)]]
            
            # IP data recording
            if IP_data:
                if not ip in ip_listing:
                    ip_listing[ip]=1
                else:
                    ip_listing[ip]+=1
    
    unique_ip_searches=len(ip_listing)
    search_data=(searches,authors_dict,title_dict,eprint_dict)
    result_data=(result_list,author_result_list,title_result_list,eprint_result_list)
    term_data=(spires_terms,spires_term_count)
    IP_data=(ip_listing,unique_ip_searches)
    session_data=ip_listpair
    packaged_data=(search_data,result_data,term_data,IP_data,session_data)
    return packaged_data
    
def processSessionData(ip_listpair):
    session_time=[]
    session_searches=[]
    st_from_main=[]
    ss_from_main=[]
    st_from_others=[]
    ss_from_others=[]
    num_sessions=0
    num_single_sessions=0
    session_metric=[]
    
    MAIN = re.compile("(http:\/\/inspirebeta.net\/)(|\?ln=en)")
    
    for session in ip_listpair:
        session_searches.append(session[1])
        delta=abs(session[2]-session[3])
        session_time.append(delta.seconds)
        num_sessions+=1
        if session[4]!='':
            if MAIN.search(session[4]):
                st_from_main.append(delta.seconds)
                ss_from_main.append(session[1])
            else:
                st_from_others.append(delta.seconds)
                ss_from_others.append(session[1])
        if session[1]==1:
            num_single_sessions+=1
        if delta.seconds>0:
            session_metric.append(session[1]/delta.seconds)
        '''prev_time = session[2]
        for search in session[5]:
            cur_time=search[1]
            time_dif=abs(prev_time-cur_time)
            if time_dif<discriminator:
                quick_searches+=1'''
    packaged_session_data=(st_from_main,ss_from_main,st_from_others,ss_from_others,
                           session_time,session_searches,num_sessions,
                           num_single_sessions,session_metric)
    return packaged_session_data