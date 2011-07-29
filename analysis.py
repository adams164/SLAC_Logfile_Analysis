import numpy,re,Gnuplot,operator,copy
from analysisFunctions import *
import matplotlib.pyplot as plt
import GeoIP
import matplotlib
from pylab import *

#read_from = raw_input("Read from:")

#data = cPickle.load(open(read_from,'rb'))
def analyzeSearchData(data,save_dir):
    authors_dict=data[2]
    title_dict=data[1]
    eprint_dict=data[0]
    
    sorted_eprint_dict = sorted(eprint_dict.iteritems(), key=operator.itemgetter(1))
    sorted_author_dict = sorted(authors_dict.iteritems(), key=operator.itemgetter(1))
    sorted_title_dict = sorted(title_dict.iteritems(), key=operator.itemgetter(1))
    
    eprint_count=[count[0] for name,count in eprint_dict.iteritems()]
    avg_eprint_count = numpy.average(eprint_count)
    std_eprint_count = numpy.std(eprint_count)
    max_eprint_count = numpy.amax(eprint_count)
    title_count=[count[0] for name,count in title_dict.iteritems()]
    avg_title_count = numpy.average(title_count)
    std_title_count = numpy.std(title_count)
    max_title_count = numpy.amax(title_count)
    author_count=[count[0] for name,count in authors_dict.iteritems()]
    avg_author_count = numpy.average(author_count)
    std_author_count = numpy.std(author_count)
    max_author_count = numpy.amax(author_count)
    
    total_eprints=0
    total_authors=0
    total_titles=0
    num_ones_eprints=0
    num_ones_authors=0
    num_ones_titles=0
    
    
    for name, list in eprint_dict.iteritems():
        count=list[0]
        total_eprints+=1
        if count==1:
            num_ones_eprints+=1
    for name, list in title_dict.iteritems():
        count=list[0]
        total_titles+=1
        if count==1:
            num_ones_titles+=1
    for name, list in authors_dict.iteritems():
        count=list[0]
        total_authors+=1
        if count==1:
            num_ones_authors+=1
    
    print "================================"
    print "||    EPrint Search Data      ||"
    print "================================"
    print "max eprints:"+str(max_eprint_count)
    print "average eprints:"+str(avg_eprint_count)
    print "standard deviation eprints:"+str(std_eprint_count)
    print "total eprints:"+str(total_eprints)
    print "number of single eprints:"+str(num_ones_eprints)
    print "Top eprints:"
    
    for i in range(10):
        list = sorted_eprint_dict[-1-i]
        print str(list[1][0])+" - "+str(list[0])
    
    
    
    print "================================"
    print "||     Title Search Data      ||"
    print "================================"
    print "max titles:"+str(max_title_count)
    print "average titles:"+str(avg_title_count)
    print "standard deviation titles:"+str(std_title_count)
    print "total titles:"+str(total_titles)
    print "number of single titles:"+str(num_ones_titles)
    print "Top titles:"
    
    for i in range(10):
        list = sorted_title_dict[-1-i]
        print str(list[1][0])+" - "+str(list[0])
    
    print "================================"
    print "||    Author Search Data      ||"
    print "================================"
    print "max authors:"+str(max_author_count)
    print "average authors:"+str(avg_author_count)
    print "standard deviation authors:"+str(std_author_count)
    print "total authors:"+str(total_authors)
    print "number of single authors:"+str(num_ones_authors)
    print "Top authors:"
    
    for i in range(10):
        list = sorted_author_dict[-1-i]
        print str(list[1][0])+" - "+str(list[0])
    
    title_count.sort()
    
    hist_authors,bin_edge = generateHistogram(author_count)
    hist_titles,bin_edge = generateHistogram(title_count)
    hist_eprints,bin_edge = generateHistogram(eprint_count)
    
    #print bin_edge[:-1]
    #print hist
    g1=Gnuplot.Gnuplot()
    g2=Gnuplot.Gnuplot()
    g3=Gnuplot.Gnuplot()
    data_author=Gnuplot.Data(bin_edge[:-1],hist_authors,title='Author Search Counts')
    #data_old=Gnuplot.Data(bin_edge[:-1],hist_old,title='Author Search Counts')
    data_title=Gnuplot.Data(bin_edge[:-1],hist_titles,title='Title Search Counts')
    data_eprint=Gnuplot.Data(bin_edge[:-1],hist_eprints,title='Eprints Search Counts')
    g1('set logscale xy')
    g2('set logscale xy')
    g3('set logscale xy')
    
    g1.xlabel('Number of search counts')
    g1.ylabel('Percentage of searches')
    g1.plot(data_author)
    g2.xlabel('Number of search counts')
    g2.ylabel('Percentage of searches')
    g2.plot(data_title)
    g3.xlabel('Number of search counts')
    g3.ylabel('Percentage of searches')
    g3.plot(data_eprint)
    #ans = raw_input('Enter to quit ("save" to save plots): ')
    #if ans == 'save':
    g1.hardcopy(save_dir+'data_author.png',terminal = 'png')
    g2.hardcopy(save_dir+'data_title.png', terminal = 'png')
    g3.hardcopy(save_dir+'data_eprint.png', terminal = 'png')
    g1.reset()
    g2.reset()
    g3.reset()

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
    frustration_cut_1=0
    frustration_cut_2=0
    sessions_cut_1=0
    sessions_cut_2=0
    higher_count=0
    #discriminator=10
    
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
        #if delta.seconds>0:
            #session_metric.append(session[1]/(delta.seconds/float(60)))
        re_searches=0
        last_search=''
        for search in session[5]:
            term = search[0]
            if similarQueries(last_search,term):
                re_searches+=1
            last_search=term
        if session[1]<250 and session[1]>2:
            if session[1]>5 and ((float(re_searches)/float(session[1])>.5 and re_searches>5) or re_searches>=10):
                if re_searches>=10:
                    frustration_cut_2+=1
                elif re_searches>5:
                    frustration_cut_1+=1
                frustration_info = (session[0],re_searches,session[5])
                #print "IP --- "+session[0]+" --- "+str(re_searches)
                #for search in session[5]:
                #    print str(search[0])
                session_metric.append(frustration_info)
            if session[1]>=20:
                sessions_cut_2+=1
            elif session[1]>10:
                sessions_cut_1+=1
            
        elif session[1]>250:
            higher_count+=1
            
    frustration_counts=(frustration_cut_1,frustration_cut_2,sessions_cut_1,sessions_cut_2,higher_count)
    packaged_session_data=(st_from_main,ss_from_main,st_from_others,ss_from_others,
                           session_time,session_searches,num_sessions,
                           num_single_sessions,session_metric,frustration_counts)
    return packaged_session_data

def analyzeSessionData(raw_data,save_dir):
    data = processSessionData(raw_data)
    st_from_main,ss_from_main,st_from_others,ss_from_others,session_time,\
    session_searches,num_sessions,num_single_sessions,session_metric,frustration_counts=data
    hist_st_main, bin_edge = generateHistogram(st_from_main)
    hist_ss_main, bin_edge_ss = generateHistogram(ss_from_main,100)
    hist_st_other, bin_edge = generateHistogram(st_from_others)
    hist_ss_other, bin_edge_ss = generateHistogram(ss_from_others,100)
    hist_session_time, bin_edge = generateHistogram(session_time)
    hist_session_searches, bin_edge_ss = generateHistogram(session_searches,100)
    print "Number of sessions: " + str(num_sessions)
    print "Number of single search sessions: " + str(num_single_sessions)
    print "Number of multi-search sessions: " + str(num_sessions-num_single_sessions)
    print "Number of frustrated sessions in cut 1: " +str(frustration_counts[0])
    print "Number of sessions above cut 1: " + str(frustration_counts[2])
    print "Number of frustrated sessions in cut 2: " +str(frustration_counts[1])
    print "Number of sessions above cut 2: " + str(frustration_counts[3])
    print "Number above 250 searches: " +str(frustration_counts[4])
    
    term_dict={}
    for session in session_metric:
        keywords = getSessionKeywords(session[2])
        sorted_keywords=sorted(keywords.iteritems(),key=operator.itemgetter(1))
        if sorted_keywords:
            word = sorted_keywords[-1][0]
            if word in term_dict:
                term_dict[word]+=1
            else:
                term_dict[word]=1
    sorted_terms = sorted(term_dict.iteritems(),key=operator.itemgetter(1))
    sorted_terms.reverse()
    count = 5
    if count>len(sorted_terms):
        count = len(sorted_terms)
    for word,count in sorted_terms[:count]:
        print word+" -- "+str((float(count)/float(len(session_metric)))*100)+"%"

    
    #session_final=[]
    #axes([.2,.2,.7,.7])
    #plt.hist(session_metric,50,log=True)
    #print sorted(session_metric)[-10:]
    #plt.show()
    '''for searches,time in zip(session_searches,session_time):
        if not [searches,time] in session_final:
            session_final.append((searches,time))
            session_numbers.append(1)
        else:
            index=session_final.index([searches,time])
    '''       
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
    #ans=raw_input('Enter to quit ("save" to save plots): ')
    #if ans == 'save':
    g_s_t.hardcopy(save_dir+'data_session_time.png',terminal='png')
    g_s_s.hardcopy(save_dir+'data_session_searches.png',terminal='png')
    g_s_t.reset()
    g_s_s.reset()

def analyzeSpiresTermData(data,save_dir):
    spires_terms,spires_term_count,searches=data
    print searches
    print spires_terms
    print spires_term_count
    
def analyzeIPData(data,save_dir):
    ip_listing,unique_ip_searches=data
    location_log={}
    print "Unique IP searches: " + str(unique_ip_searches)
    
    location_log=reduceFractions(IPToCountry(ip_listing))
    
    loc_log_alt=sorted(location_log.iteritems(),key=operator.itemgetter(1))
    loc_log_alt.reverse()
    keys,values=zip(*loc_log_alt)
    
    values=values
    colors=['red','blue','green']
    rows=len(values)
    
    ind = arange(1)+.3
    width=0.4
    yoff=array([0.0])
    for row in xrange(rows):
        bar(ind,values[row],width,bottom=yoff,color=colors[row%3])
        yoff=yoff+values[row]
    show()
            
    return ip_listing
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

def analyzeResultData(data,save_dir):
    result_list,author_result_list,title_result_list,eprint_result_list=data
    hist_results, bin_edge=generateHistogram(result_list)
    hist_a_results, bin_edge=generateHistogram(author_result_list)
    hist_t_results, bin_edge=generateHistogram(title_result_list)
    hist_e_results, bin_edge=generateHistogram(eprint_result_list)
    """
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
    """
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
    #ans=raw_input('Enter to quit')
    #if ans == 's':
    g.hardcopy(save_dir+'data_query_results.png',terminal = 'png')
    g.reset()
    
