import numpy

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
    hist[40:80]=hist[40:80]/2
    hist[80:100]=hist[80:100]/5
    hist[100:108]=hist[100:108]/10
    hist[108:113]=hist[108:113]/20
    hist[113:]=hist[113:]/100
    return hist, bin_edge

def similarQueries(query1, query2):
    if query1 and query2:
        if query1!=query2:
            if abs(len(query1.split(" "))-len(query2.split(" ")))<3:
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
