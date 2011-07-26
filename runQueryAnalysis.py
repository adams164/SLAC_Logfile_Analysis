import re, cPickle, operator, numpy, Gnuplot, time, datetime, os
from invenio.bibindex_engine_tokenizer import BibIndexFuzzyNameTokenizer as FNT
import GeoIP,socket

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
_SPIRES_TO_INVENIO_KEYWORDS_MATCHINGS = {
    'find' : 'find',
    'fin' : 'find',
    'f' : 'find',
        # address
        'address' : 'address:',
        # affiliation
        'affiliation' : 'affiliation:',
        'affil' : 'affiliation:',
        'aff' : 'affiliation:',
        'af' : 'affiliation:',
        'institution' : 'affiliation:',
        'inst' : 'affiliation:',
        # any field
        'any' : 'anyfield:',
        # bulletin
        'bb' : 'reportnumber:',
        'bbn' : 'reportnumber:',
        'bull' : 'reportnumber:',
        'bulletin-bd' : 'reportnumber:',
        'bulletin-bd-no' : 'reportnumber:',
        'eprint' : 'reportnumber:',
        # citation / reference
        'c' : 'reference:',
        'citation' : 'reference:',
        'cited' : 'reference:',
        'jour-vol-page' : 'reference:',
        'jvp' : 'reference:',
        # collaboration
        'collaboration' : 'collaboration:',
        'collab-name' : 'collaboration:',
        'cn' : 'collaboration:',
        # conference number
        'conf-number' : '111__g:',
        'cnum' : '773__w:',
        # country
        'cc' : '044__a:',
        'country' : '044__a:',
        # date
        'date': 'date',
        'd': 'date',
        # date added
        'date-added': 'date-added',
        'dadd': 'date-added',
        'da': 'date-added',
        # date updated
        'date-updated': 'date-modified',
        'dupd': 'date-modified',
        'du': 'date-modified',
        # first author
        'fa' : 'firstauthor:',
        'first-author' : 'firstauthor:',
        # author
        'a' : 'author:',
        'au' : 'author:',
        'author' : 'author:',
        'name' : 'author:',
        # exact author
        # this is not a real keyword match. It is pseudo keyword that
        # will be replaced later with author search
        'ea' : 'exactauthor:',
        'exact-author' : 'exactauthor:',
        # experiment
        'exp' : 'experiment:',
        'experiment' : 'experiment:',
        'expno' : 'experiment:',
        'sd' : 'experiment:',
        'se' : 'experiment:',
        # journal
        'journal' : 'journal:',
        'j' : 'journal:',
        'published_in' : 'journal:',
        'spicite' : 'journal:',
        'vol' : 'journal:',
        # journal page
        'journal-page' : '773__c:',
        'jp' : '773__c:',
        # journal year
        'journal-year' : '773__y:',
        'jy' : '773__y:',
        # key
        'key' : '970__a:',
        'irn' : '970__a:',
        'record' : '970__a:',
        'document' : '970__a:',
        'documents' : '970__a:',
        # keywords
        'k' : 'keyword:',
        'keywords' : 'keyword:',
        'kw' : 'keyword:',
        # note
        'note' : '500__a:',
        'n' : '500__a:',
        # old title
        'old-title' : '246__a:',
        'old-t' : '246__a:',
        'ex-ti' : '246__a:',
        'et' : '246__a:',
        #postal code
        'postalcode' : 'postalcode:',
        'zip' : 'postalcode:',
        'cc' : 'postalcode:',
        # ppf subject
        'ppf-subject' : '650__a:',
        'ps' : '650__a:',
        'scl' : '650__a:',
        'status' : '650__a:',
        # recid
        'recid' : 'recid:',
        # report number
        'r' : 'reportnumber:',
        'rn' : 'reportnumber:',
        'rept' : 'reportnumber:',
        'report' : 'reportnumber:',
        'report-num' : 'reportnumber:',
        # title
        't' : 'title:',
        'ti' : 'title:',
        'title' : 'title:',
        'with-language' : 'title:',
        # fulltext
        'fulltext' : 'fulltext:',
        'ft' : 'fulltext:',
        # topic
        'topic' : '695__a:',
        'tp' : '695__a:',
        'hep-topic' : '695__a:',
        'desy-keyword' : '695__a:',
        'dk' : '695__a:',

        # topcite
        'topcite' : 'cited:',

        # captions
        'caption' : 'caption:',

        # replace all the keywords without match with empty string
        # this will remove the noise from the unknown keywrds in the search
        # and will in all fields for the words following the keywords

        # category
        'arx' : '037__c:',
        'category' : '037__c:',
        # primarch
        'parx' : '037__c:',
        'primarch' : '037__c:',
        # texkey
        'texkey' : '035__z:',
        # type code
        'tc' : '690C_a:',
        'ty' : '690C_a:',
        'type' : '690C_a:',
        'type-code' : '690C_a',
        # field code
        'f' : '65017a:',
        'fc' : '65017a:',
        'field' : '65017a:',
        'field-code' : '65017a:',
        # coden
        'bc' : 'coden',
        'browse-only-indx' : 'coden',
        'coden' : 'coden',
        'journal-coden' : 'coden',
        # energy
        'e' : 'energy',
        'energy' : 'energy',
        'energyrange-code' : 'energy',
        # exact experiment number
        'ee' : 'exact-experiment',
        'exact-exp' : 'exact-experiment',
        'exact-expno' : 'exact-experiment',
        # hidden note
        'hidden-note' : 'hidden-note',
        'hn' : 'hidden-note',
        # ppf
        'ppf' : 'ppf',
        'ppflist' : 'ppf',
        # slac topics
        'ppfa' : 'slac-topics',
        'slac-topics' : 'slac-topics',
        'special-topics' : 'slac-topics',
        'stp' : 'slac-topics',
        # test index
        'test' : 'test',
        'testindex' : 'test',
    }

eprint_dict={}
authors_dict={}
title_dict={}

result_list=[]
author_result_list=[]
title_result_list=[]
eprint_result_list=[]
data_list=[]

read_from = raw_input("Read Data From: ")
single_file = os.path.isfile(read_from)
file_read_from=os.path.split(read_from)[1]
if single_file:
    data_list.append(cPickle.load(open(read_from, 'rb')))
else:
    file_parts=os.path.split(read_from)
    list_files=os.listdir(file_parts[0])
    for filename in list_files:
        if filename.find(file_parts[1]+'.') == 0:
            print "reading "+filename
            data_list.append(cPickle.load(open(file_parts[0]+'/'+filename,'rb')))

ip_listing={}
searches=0
country_dict={}
country_dict_unique={}
unique_ip_searches=0
ip_listpair=[]
ip_active={}
number=1
timeout=5
spires_terms={}
spires_term_count=0
session_timeout=datetime.timedelta(minutes=timeout)
ip_ignore=[
'137.138.124.253',   
'209.85.238.209',
'134.79.166.8',
'209.85.238.179',
'209.85.238.241',
'140.180.16.88',
'128.84.158.119',
'192.107.175.11',
'220.181.51.75',
'192.107.175.132',   
'220.181.51.78',
'220.181.51.74',
'220.181.51.76',
'220.181.51.77',
    ]
#session_list=[]
#Session format: [ip,start_time,[(query,time),(query,time),...],end_time]
    
for data in data_list:
    print "running file " +str(number)
    number+=1
    for entry in data:
        searches+=1
        ip = entry[0]
        if ip in ip_ignore:
            continue
        search_term = entry[1]
        bits = search_term.split('( in hep')[0].split(' ')
        for word in bits:
            if word in _SPIRES_TO_INVENIO_KEYWORDS_MATCHINGS:
                spires_term_count+=1
                term=_SPIRES_TO_INVENIO_KEYWORDS_MATCHINGS[word]
                if term in spires_terms:
                    spires_terms[term]+=1
                else:
                    spires_terms[term]=1
            #else:
                #print word
        referrer = entry[4]
        try:
            date = datetime.datetime(*(time.strptime(entry[3],"%d/%b/%Y:%H:%M:%S")[0:6]))
        except ValueError:
            date = datetime.datetime(*(time.strptime(entry[3],"%Y%m%d %H:%M:%S")[0:6]))
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

        ip=entry[0]
        if not ip in ip_listing:
            ip_listing[ip]=1
        else:
            ip_listing[ip]+=1

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

        
"""
zeros = 0
a_zeros = 0
t_zeros = 0
e_zeros = 0
ones = 0
a_ones = 0
t_ones = 0
e_ones = 0
mores = 0
a_mores = 0
t_mores = 0
e_mores = 0
negatives = 0
for entry in data:
    results = int(entry[2])
    if results==0:
        zeros+=1
    elif results==1:
        ones+=1
    else:
        mores+=1
    result_list.append(results)
    search_term = entry[1]
    
    if AUTH_NAME.search(search_term):
        if results==0:
            a_zeros+=1
        elif results==1:
            a_ones+=1
        else:
            a_mores+=1
        author_result_list.append(results)

    if TITLE_NAME.search(search_term):
        if results==0:
            t_zeros+=1
        elif results==1:
            t_ones+=1
        else:
            t_mores+=1
        title_result_list.append(results)

    if EPRINT.search(search_term):
        if results==0:
            e_zeros+=1
        elif results==1:
            e_ones+=1
        else:
            e_mores+=1
        eprint_result_list.append(results)


hist_results, bin_edge= numpy.histogram(result_list,bins)
hist_a_results, bin_edge= numpy.histogram(author_result_list, bins)
hist_t_results, bin_edge= numpy.histogram(title_result_list, bins)
hist_e_results, bin_edge= numpy.histogram(eprint_result_list, bins)
"""
def generateHistogram(data,linear=0):
    if linear==0:
        bins=numpy.arange(0,40,1)
        bins=numpy.append(bins,numpy.arange(40,120,2))
        bins=numpy.append(bins,numpy.arange(120,220,5))
        bins=numpy.append(bins,numpy.arange(220,300,10))
        bins=numpy.append(bins,numpy.arange(300,500,20))
        bins=numpy.append(bins,numpy.arange(500,5000,100))
    else:
        bins=numpy.arange(0,linear,1)
    hist, bin_edge = numpy.histogram(data,bins)
    hist[40:80]=hist[40:80]/2
    hist[80:100]=hist[80:100]/5
    hist[100:108]=hist[100:108]/10
    hist[108:113]=hist[108:113]/20
    hist[113:]=hist[113:]/100
    return hist, bin_edge

hist_st_main, bin_edge = generateHistogram(st_from_main)
hist_ss_main, bin_edge_ss = generateHistogram(ss_from_main,100)
hist_st_other, bin_edge = generateHistogram(st_from_others)
hist_ss_other, bin_edge_ss = generateHistogram(ss_from_others,100)
hist_session_time, bin_edge = generateHistogram(session_time)
hist_session_searches, bin_edge_ss = generateHistogram(session_searches,100)
print "Number of sessions: " + str(num_sessions)
print "Number of single search sessions: " + str(num_single_sessions)
#print "Number of total hits: " +str(searches)


def stringTicsFromKeys(keys):
    str_res=')'
    str_res='('
    loop_num=1
    for item in keys:
        str_res+='"'+item+'" '+str(loop_num)+', '
        loop_num+=1
    str_res=str_res[:-2]+')'
    return str_res

print searches
print spires_terms
print spires_term_count
#cPickle.dump([country_dict,country_dict_unique],open('runQueryAnalysisResults','wb'))
cPickle.dump([spires_terms,spires_term_count,searches],open('runQueryAnalysisResultsSpiresTerms.'+file_read_from,'wb'))

location_log={}
total=0
for ip in ip_listing:
    if ip_listing[ip]>=50:
        total+=1

print total
loc_log_alt={}
'''for ip in ip_listing:
    if ip_listing[ip]>=50:
        host = socket.getfqdn(ip)
        location_log[host]=ip_listing[ip]
        total-=1
        loc_bits = host.split('.')
        name=''
        if loc_bits[-1]=="edu":
            name = loc_bits[-2]
        elif loc_bits.count("ac")>=1:
            name = loc_bits[loc_bits.index("ac")-1]
        elif "cern.ch" in host:
            name ="cern"
        elif "fnal.gov" in host:
            name = "fnal"

        if name!='':
            if name in loc_log_alt:
                loc_log_alt[name].append(ip)
            else:
                loc_log_alt[name]=[ip]
        if total%100 == 0:
            print total

for name, ip in loc_log_alt.iteritems():
    if len(ip)>5:
        print name +"  ----  "+str(ip)'''
cPickle.dump(ip_listing,open('runQueryAnalysisResultsUIP.'+file_read_from,'wb'))


'''sorted_c=sorted(country_dict.iteritems(),key=operator.itemgetter(1))
sorted_c_u=sorted(country_dict_unique.iteritems(),key=operator.itemgetter(1))
c_k=[]
c_v=[]
c_u_k=[]
c_u_v=[]
for key,value in sorted_c:
    c_k.append(key)
    c_v.append(value)

for key,value in sorted_c_u:
    c_u_k.append(key)
    c_u_v.append(value)
    
g_c=Gnuplot.Gnuplot()
data_country=Gnuplot.Data(1+numpy.array(range(len(country_dict))),c_v,title='Number of hits',with='boxes')
data_country_unique=Gnuplot.Data(1+numpy.array(range(len(country_dict_unique))),c_u_v,title='Number of unique user hits',with='boxes')
g_c('set xtics '+stringTicsFromKeys(c_u_k))
g_c('set xtics rotate')
g_c('set style fill solid 0.5')
g_c('set logscale y')
g_c.plot(data_country,data_country_unique)
print "???"
raw_input("please?")
#for key, value in country_dict.iteritems():
#    print key+" has "+str(value)+" hits"
print "number of total unique user hits: " +str(unique_ip_searches)
#for key, value in country_dict_unique.iteritems():
#    print key+" has "+str(value)+" unique user hits"
'''
"""
hist_results = normalizeHistogram(hist_results)
hist_a_results = normalizeHistogram(hist_a_results)
hist_t_results = normalizeHistogram(hist_t_results)
hist_e_results = normalizeHistogram(hist_e_results)

print "Zeros: " + str(zeros)
print "Ones: " + str(ones)
print "Mores: " + str(mores)
print "Author Zeros: " + str(a_zeros)
print "Author Ones: " + str(a_ones)
print "Author Mores: " + str(a_mores)
print "Title Zeros: " + str(t_zeros)
print "Title Ones: " + str(t_ones)
print "Title Mores: " + str(t_mores)
print "Eprint Zeros: " + str(e_zeros)
print "Eprint Ones: " + str(e_ones)
print "Eprint Mores: " + str(e_mores)
bin_edge=bin_edge[:-1]+1
g=Gnuplot.Gnuplot()
g_a=Gnuplot.Gnuplot()
g_t=Gnuplot.Gnuplot()
g_e=Gnuplot.Gnuplot()
data=Gnuplot.Data(bin_edge,hist_results)
data_a=Gnuplot.Data(bin_edge,hist_a_results)
data_t=Gnuplot.Data(bin_edge,hist_t_results)
data_e=Gnuplot.Data(bin_edge,hist_e_results)
g('set logscale xy')
g.plot(data)
g_a('set logscale xy')
g_a.plot(data_a)
g_t('set logscale xy')
g_t.plot(data_t)
g_e('set logscale xy')
g_e.plot(data_e)
ans=raw_input('Enter to quit')
if ans == 's':
    g.hardcopy('data_query.png',terminal = 'png')
g.reset()
"""
session_final=[]
import matplotlib.pyplot as plt
from pylab import *
#axes([.2,.2,.7,.7])
plt.hist(session_metric)
plt.show()
'''for searches,time in zip(session_searches,session_time):
    if not [searches,time] in session_final:
        session_final.append((searches,time))
        session_numbers.append(1)
    else:
        index=session_final.index([searches,time])
'''       

#g_svs=Gnuplot.Gnuplot()
#data_svs=Gnuplot.Data(session_time,session_searches)
#g_svs("set logscale xy")
#g_svs.plot(data_svs)
#ans=raw_input("pause")
bin_edge=bin_edge[:-1]
bin_edge_ss=bin_edge_ss[:-1]
g_s_t=Gnuplot.Gnuplot()
g_s_s=Gnuplot.Gnuplot()
data_s_t=Gnuplot.Data(bin_edge,hist_session_time,title="Session Time")
data_s_s=Gnuplot.Data(bin_edge_ss,hist_session_searches,title="Session Searches")
data_s_t_m=Gnuplot.Data(bin_edge,hist_st_main,title="Session Time (from Main)")
data_s_s_m=Gnuplot.Data(bin_edge_ss,hist_ss_main,title="Session Searches (from Main)")
data_s_t_o=Gnuplot.Data(bin_edge,hist_st_other,title="Session Time (from Other)")
data_s_s_o=Gnuplot.Data(bin_edge_ss,hist_ss_other,title="Session Searches (from Other)")
g_s_t('set logscale xy')
g_s_s('set logscale y')
g_s_t.plot(data_s_t,data_s_t_m,data_s_t_o)
g_s_s.plot(data_s_s,data_s_s_m,data_s_s_o)
ans=raw_input('Enter to quit ("save" to save plots): ')
if ans == 'save':
    g_s_t.hardcopy('data_session_time_'+file_read_from+'.png',terminal='png')
    g_s_s.hardcopy('data_session_searches_'+file_read_from+'.png',terminal='png')
    #g_c.hardcopy('data_country_bars.png',terminal='png')
#g_s_t.reset()
#g_s_s.reset()
#g_c.reset()
