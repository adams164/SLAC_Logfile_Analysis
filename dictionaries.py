import cPickle,socket,os

def buildInstIPMap(ip_listing,existing_mapping={}):
    total=0
    mapping=existing_mapping
    for ip in ip_listing:
        if ip_listing[ip]>=50:
            host = socket.getfqdn(ip)
            #location_log[host]=ip_listing[ip]
            total+=1
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
    
            ip_block=ip.split('.')[0]+'.'+ip.split('.')[1]+"."
            if name!='':
                if ip_block in mapping:
                    if not name == mapping[ip_block]:
                        print "oh snap!"
                else:
                    mapping[ip_block]=name
            if total%100 == 0:
                print total
    return mapping

def getInstIPMap(ip_listing,force_new=False):
    if os.path.isfile("inst.dict"):
        mapping=cPickle.load(open("inst.dict",'rb'))
        if force_new:
            mapping=buildInstIPMap(ip_listing,mapping)
            cPickle.dump(mapping,open("inst.dict",'wb'))
    else:
        mapping=buildInstIPMap(ip_listing)
        cPickle.dump(mapping, open("inst.dict",'wb'))
    return mapping

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
StI = {
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
