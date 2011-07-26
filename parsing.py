import urllib,re,random,cPickle,urlparse,cgi,datetime,time
from invenio.search_engine import perform_request_search
from invenio.websearch_webinterface import wash_search_urlargd

def getQueryResults(url):
    """Run a search url to get search results"""
    #return random.randint(0,50)
    url_split=urlparse.urlparse(url)[4]
    #print url_split
    argd = wash_search_urlargd(cgi.parse_qs(url_split))
    argd['of']="id"
    #print argd
    try:
        num=len(perform_request_search(None, **argd))
    except:
        num=0
    return num

def readLogFile(filename,write_to,spires_log=False,alldata=False):
    """Extract search queries from a logfile
    
    Can handle both SPIRES style and INSPIRE style logs.
    The data is printed directly to a pickle file to avoid
    memory issues associated with large lists.
    """
    if spires_log:
        HEP = re.compile('\( in hep')
        SEARCH_LEAD = re.compile('GET /search?')
        SEARCH = re.compile('(p|p1|p2)=(?P<term>.*?)(&| )')
        TIME_STAMP = re.compile('\d{8} \d\d:\d\d:\d\d')
        GOOGLEBOT = re.compile('ooglebot')
        f = open(filename)
        data=[]
        num_records=0
        dumps=1
        for line in f:
            url = urllib.unquote(line.split('"')[3].lower().replace('+', ' '))
            if not HEP.search(url) or GOOGLEBOT.search(line):
                continue
            time_stamp = TIME_STAMP.search(line).group()
            date = datetime.datetime(*(time.strptime(time_stamp,"%Y%m%d %H:%M:%S")[0:6]))
            if (date.month==6 and date.day>1) or alldata:
                num_records+=1
                referrer = ''
                search_term = url
                #query_url = 'https://inspire.slac.stanford.edu'+line.split('"')[1].split(' ')[1]
                results = -1#getQueryResults(query_url)
                ip_address = line.split()[2]
                #print str(time_stamp)+"-"+str(results)
                data.append([ip_address,search_term,results,time_stamp,referrer])
                if num_records==100000:
                    cPickle.dump(data,open(write_to+".part"+str(dumps),'wb'))
                    dumps+=1
                    num_records=0
                    data=[]
                    print "Writing..."
        
        if dumps==1:
            cPickle.dump(data,open(write_to,'wb'))
        else:
            cPickle.dump(data,open(write_to+".part"+str(dumps),'wb'))
        
        print "done -- wrote " +str(dumps)+ " parts"
    else:
        SEARCH_LEAD = re.compile('GET /search?')
        SEARCH = re.compile('(p|p1|p2)=(?P<term>.*?)(&| )')
        TIME_STAMP = re.compile('\[(?P<time>.*?)( .*?)\]')
        GOOGLEBOT = re.compile('ooglebot')
        f = open(filename)
        data=[]
        num_records=0
        dumps=1
        for line in f:
            if not SEARCH_LEAD.search(line) or not SEARCH.search(line) or GOOGLEBOT.search(line):
                continue
            time_stamp = TIME_STAMP.search(line).group('time')
            date = datetime.datetime(*(time.strptime(time_stamp,"%d/%b/%Y:%H:%M:%S")[0:6]))
            if date.month==6 and date.day>1:
                num_records+=1
                referrer = line.split('"')[3]
                search_term = urllib.unquote(SEARCH.search(line).group('term').lower().replace('+', ' '))
                query_url = 'https://inspire.slac.stanford.edu'+line.split('"')[1].split(' ')[1]
                results = -1#getQueryResults(query_url)
                ip_address = line.split()[0]
                #print str(time_stamp)+"-"+str(results)
                data.append([ip_address,search_term,results,time_stamp,referrer])
                if num_records==100000:
                    cPickle.dump(data,open(write_to+".part"+str(dumps),'wb'))
                    dumps+=1
                    num_records=0
                    data=[]
                    print "Writing..."
        
        if dumps==1:
            cPickle.dump(data,open(write_to,'wb'))
        else:
            cPickle.dump(data,open(write_to+".part"+str(dumps),'wb'))
        
        print "done -- wrote " +str(dumps)+ " parts"