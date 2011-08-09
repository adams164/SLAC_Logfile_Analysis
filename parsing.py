import urllib,re,random,cPickle,urlparse,cgi,datetime,time,os
from invenio.search_engine import perform_request_search
from invenio.websearch_webinterface import wash_search_urlargd

def getQueryResults(url):
    """Run a search url to get search results"""
    #return random.randint(0,50)
    argd=urlArgs(url)
    #print argd
    try:
        num=len(perform_request_search(None, **argd))
    except:
        num=0
    return num

def urlArgs(url):
    url_split=urlparse.urlparse(url)[4]
    #print url_split
    argd = wash_search_urlargd(cgi.parse_qs(url_split))
    argd['of']="id"
    return argd

def readLogFileByDay(type,log_dir,write_to,date_start,date_end,force_read):
    print force_read
    start_date=datetime.datetime(*(time.strptime(date_start, "%Y%m%d")[0:6]))
    end_date=datetime.datetime(*(time.strptime(date_end, "%Y%m%d")[0:6]))
    INSPIRE_LOG=re.compile('\d{4}_\w\w\w_inspire.log')
    SPIRES_LOG=re.compile('spiface.\d\d-\w\w\w-\d{4}.log')
    log_file_listing = sorted(os.listdir(log_dir))
    if type == "INSPIRE":
        counts=0
        current_day=None
        for log_file in log_file_listing:
            counts+=1
            if counts%15==0:
                print "Read "+str(counts)+" files"
            if INSPIRE_LOG.match(log_file):
                log_date=datetime.datetime(*(time.strptime(log_file,"%Y_%b_inspire.log")[0:6]))
                month_okay = log_date.month>=start_date.month and log_date.month<=end_date.month
                year_okay = log_date.year>=start_date.year and log_date.year<=end_date.year
                if month_okay and year_okay:
                    readLogFile(log_dir+log_file,write_to,False,
                                date_start,date_end,1,True)
    elif type == "SPIRES":
        counts=0
        for log_file in log_file_listing:
            counts+=1
            if counts%15==0:
                print "Read "+str(counts)+" files"
            if SPIRES_LOG.match(log_file):
                log_date=datetime.datetime(*(time.strptime(log_file,"spiface.%d-%b-%Y.log")[0:6]))
                written_file_exists=os.path.isfile(write_to+'.'+log_date.strftime("%Y%m%d"))
                month_okay = log_date.month>=start_date.month and log_date.month<=end_date.month
                year_okay = log_date.year>=start_date.year and log_date.year<=end_date.year
                day_okay = log_date.day>=start_date.day and log_date.day<=end_date.day
                
                force_okay = (not written_file_exists or force_read)
                #print force_okay
                if month_okay and year_okay and day_okay and force_okay:
                    readLogFile(log_dir+log_file,write_to,True,
                                date_start,date_end,1,True)
    else:
        print "How on earth did you manage this?"
        return

def readLogFile(filename,write_to,spires_log=False,date_start="19910416",
                date_end="21640101",dumps=1,one_day=False):
    """Extract search queries from a logfile
    
    Can handle both SPIRES style and INSPIRE style logs.
    The data is printed directly to many pickle files to avoid
    memory issues associated with pickling large lists.
    """
    start_date=datetime.datetime(*(time.strptime(date_start, "%Y%m%d")[0:6]))
    end_date=datetime.datetime(*(time.strptime(date_end, "%Y%m%d")[0:6]))
    current_day=None
    if spires_log:
        HEP = re.compile('\( in hep')
        SEARCH_LEAD = re.compile('GET /search?')
        SEARCH = re.compile('(p|p1|p2)=(?P<term>.*?)(&| |$)')
        TIME_STAMP = re.compile('\d{8} \d\d:\d\d:\d\d')
        GOOGLEBOT = re.compile('ooglebot')
        f = open(filename)
        data=[]
        num_records=0
        for line in f:
            url = urllib.unquote(line.split('"')[3].lower().replace('+', ' '))
            if not HEP.search(url) or GOOGLEBOT.search(line):
                continue
            time_stamp = TIME_STAMP.search(line).group()
            log_date = datetime.datetime(*(time.strptime(time_stamp,"%Y%m%d %H:%M:%S")[0:6]))
            if one_day and not current_day:
                current_day=log_date
            if one_day:
                if current_day.day<log_date.day and data!=[]:
                    cPickle.dump(data,open(write_to+"."+str(current_day.year)+
                                           str(current_day.month).zfill(2)+str(current_day.day).zfill(2),'wb'))
                    dumps=1
                    num_records=0
                    data=[]
                    current_day=log_date
                    #print "Writing day"
                    if current_day.day>end_date.day:
                        break

            month_okay = log_date.month>=start_date.month and log_date.month<=end_date.month
            year_okay = log_date.year>=start_date.year and log_date.year<=end_date.year
            day_okay = log_date.day>=start_date.day and log_date.day<=end_date.day
            if month_okay and year_okay and day_okay:
                num_records+=1
                referrer = ''
                search_term = url.split('( in hep')[0]
                #query_url = 'https://inspire.slac.stanford.edu'+line.split('"')[1].split(' ')[1]
                results = -1#getQueryResults(query_url)
                ip_address = line.split()[2]
                #print str(time_stamp)+"-"+str(results)
                other_args = None 
                data.append([ip_address,search_term,results,time_stamp,referrer])
                if num_records==100000:
                    cPickle.dump(data,open(write_to+".part"+str(dumps).zfill(3),'wb'))
                    dumps+=1
                    num_records=0
                    data=[]
                    print "Writing..."
        if one_day and data!=[]:
            cPickle.dump(data,open(write_to+"."+str(current_day.year)+
                                   str(current_day.month).zfill(2)+str(current_day.day).zfill(2),'wb'))    
        elif not one_day:
            cPickle.dump(data,open(write_to+".part"+str(dumps).zfill(3),'wb'))
            print "done -- wrote " +str(dumps)+ " parts"
        dumps+=1
    else:
        SEARCH_LEAD = re.compile('GET /search?')
        SEARCH = re.compile('(p|p1|p2)=(?P<term>.*?)(&| |$)')
        TIME_STAMP = re.compile('\[(?P<time>.*?)( .*?)\]')
        GOOGLEBOT = re.compile('ooglebot')
        f = open(filename)
        data=[]
        num_records=0
        for line in f:
            if not SEARCH_LEAD.search(line) or not SEARCH.search(line) or GOOGLEBOT.search(line):
                continue
            time_stamp = TIME_STAMP.search(line).group('time')
            log_date = datetime.datetime(*(time.strptime(time_stamp,"%d/%b/%Y:%H:%M:%S")[0:6]))
            if one_day and not current_day:
                current_day=log_date
            if one_day:
                if current_day.day<log_date.day and data!=[]:
                    cPickle.dump(data,open(write_to+"."+str(current_day.year)+
                                           str(current_day.month).zfill(2)+str(current_day.day).zfill(2),'wb'))
                    dumps+=1
                    num_records=0
                    data=[]
                    current_day=log_date
                    #print "Writing day"
                    if current_day.day>end_date.day:
                        break

            month_okay = log_date.month>=start_date.month and log_date.month<=end_date.month
            year_okay = log_date.year>=start_date.year and log_date.year<=end_date.year
            day_okay = log_date.day>=start_date.day and log_date.day<=end_date.day
            if month_okay and year_okay and day_okay:
                num_records+=1
                referrer = line.split('"')[3]
                search_term = urllib.unquote(SEARCH.search(line).group('term').lower().replace('+', ' '))
                query_url = 'https://inspire.slac.stanford.edu'+line.split('"')[1].split(' ')[1]
                results = -1#getQueryResults(query_url)
                ip_address = line.split()[0]
                #print str(time_stamp)+"-"+str(results)
                other_args = urlArgs(query_url)
                data.append([ip_address,search_term,results,time_stamp,referrer])
                if num_records==100000:
                    cPickle.dump(data,open(write_to+".part"+str(dumps).zfill(3),'wb'))
                    dumps+=1
                    num_records=0
                    data=[]
                    print "Writing..."
        
        if one_day and data!=[]:         
            cPickle.dump(data,open(write_to+"."+str(current_day.year)+
                                   str(current_day.month).zfill(2)+str(current_day.day).zfill(2),'wb'))    
        elif not one_day:
            cPickle.dump(data,open(write_to+".part"+str(dumps).zfill(3),'wb'))
            print "done -- wrote " +str(dumps)+ " parts"
        dumps+=1
        
        