import numpy
import dictionaries
import Levenshtein
import re
import GeoIP

DIGIT = re.compile('[0-9]')

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
    hist, bin_edge = numpy.histogram(data,bins,new=True)
    if linear==0:
        hist[40:80]=hist[40:80]/2
        hist[80:100]=hist[80:100]/5
        hist[100:108]=hist[100:108]/10
        hist[108:113]=hist[108:113]/20
        hist[113:]=hist[113:]/100
    return hist, bin_edge

def averageList(av_list):
    total=sum(av_list)
    count=0
    for item in av_list:
        if item>0:
            count+=1
    if count>0:
        return (float(total)/float(count))
    else:
        return 0

def sumValues(dict):
    sum=0
    for value in dict.itervalues():
        sum+=value
    return sum


def flattenTwoDeep(list_in):
    temp = zip(*list_in)
    final_out=[]
    for item in temp:
        temp_2=zip(*item)
        list_out=[]
        for flattenable in temp_2:
            if type(flattenable[0]) is list or type(flattenable[0]) is tuple:
                element_out=flattenList(flattenable)
            elif type(flattenable[0]) is dict:
                element_out=flattenDict(flattenable)
            else:
                element_out=flattenInt(flattenable)
            list_out.append(element_out)
        final_out.append(list_out)
    return final_out

def flattenList(list_in):
    list_out=[]
    for item in list_in:
        list_out.extend(item)
    return list_out

def flattenInt(list_in):
    try:
        result = sum(list_in)
    except TypeError:
        print type(list_in)
        print list_in
        raise Exception
    return result 

def flattenDict(list_in):
    dict_out={}
    for item in list_in:
        for entry in item:
            if entry in dict_out:
                dict_out[entry]+=item[entry]
            else:
                dict_out[entry]=item[entry]
    return dict_out

def reduceToSet(dict_in,reduction_set):
    dict_out={'Others':0}
    for country in dict_in:
        if country in reduction_set:
            dict_out[country]=dict_in[country]
        else:
            dict_out['Others']+=dict_in[country]
    return dict_out

def reduceFractions(dict_enter,cutoff):
    dict_out = {}
    total=sumValues(dict_enter)
    dict_out['Others']=0
    for country in dict_enter:
        if float(dict_enter[country])/float(total)<cutoff:
            dict_out['Others']+=dict_enter[country]
        else:
            dict_out[country]=dict_enter[country]
    return dict_out

def IPToCountry(ip_listing):
    location_log={}
    gi=GeoIP.open("/usr/share/GeoIP/GeoLiteCity.dat",GeoIP.GEOIP_STANDARD)
    for ip in ip_listing:
        data = gi.record_by_addr(ip)
        if data:
            country = data['country_name']
            if country in location_log:
                location_log[country]+=ip_listing[ip]
            else:
                location_log[country]=ip_listing[ip]
    return location_log
    
def getSessionKeywords(search_term_list):
    keywords_found={}
    for search_tuple in search_term_list:
        search_term = search_tuple[0]
        for term in search_term.split(" "):
            term_key=False
            if term in dictionaries.StI and term!="find":
                term_key=dictionaries.StI[term]
            elif ":" in term:
                term_key=term.split(":")[0]+":"
            if term_key:
                if term_key in keywords_found:
                    keywords_found[term_key]+=1
                else:
                    keywords_found[term_key]=1
    return keywords_found
            

def getKeywordValues(search_term):
    keywords_found=[]
    index=0
    full_terms=search_term.split(" ")
    while index<len(full_terms):
        term=full_terms[index]
        if term!="find":
            if term in dictionaries.StI:
                cur_pos=1
                value_term=[]
                while cur_pos+index<len(full_terms):
                    cur_term = full_terms[cur_pos+index]
                    if not cur_term in dictionaries.dividers:
                        value_term.append(cur_term)
                    else:
                        break
                    cur_pos+=1
                index+=cur_pos-1
                keywords_found.append((dictionaries.StI[term]," ".join(value_term)))
            elif ":" in term:
                keywords_found.append((term.split(":")[0]+":",term.split(":")[1]))
            else:
                keywords_found.append(('',term))
        index+=1
    return keywords_found

def digitPercent(string):
    num=0
    for char in string:
        if char.isdigit():
            num+=1
    if len(string)>0:
        return float(num)/float(len(string))
    else:
        return 0

def compareTermDict(term1, term2):
    if len(term1)==len(term2):
        final_return=False
        for kv1,kv2 in zip(term1,term2):
            if Levenshtein.ratio(kv1[1],kv2[1])<.6:
                final_return=False
            else:
                value1=DIGIT.sub('',kv1[1])
                value2=DIGIT.sub('',kv2[1])
                if kv1[0]==kv2[0] and value1==value2:
                    continue
                final_return=True
        return final_return
    else:
        return False

def similarQueries(query1, query2):
    if query1 and query2:
        if query1!=query2 and not("recid:" in query1 or "recid:" in query2):
            if compareTermDict(getKeywordValues(query1),getKeywordValues(query2)):
                return True
            else:
                return False
        else:
            return False
    else:
        return False

def stringTicsFromKeys(keys):
    str_res='('
    loop_num=1
    for item in keys:
        str_res+='"'+item+'" '+str(loop_num)+', '
        loop_num+=1
    str_res=str_res[:-2]+')'
    return str_res
