#truerandom v1.0 beta
#sergio@infosegura.net
#www.infosegura.net

#True random numbers are obtained from http://www.random.org/
#If the module fails to obtain the random list it will return -1

#-----------IMPORTS----------------#
from urllib import urlopen
import urllib

#-----------CLASSES--------------#
class myURLopener(urllib.FancyURLopener):

    def http_error_401(self, url, fp, errcode, errmsg, headers, data=None):
        print "Warning: cannot open, site requires authentication"
        return None

#-----------FUNCTIONS--------------#
def getnum(min,max,amount):
    global randlist
    try:
        url_opener = myURLopener()
        data = url_opener.open("http://www.random.org/integers/?num="+str(amount)+"&min="+str(min)+"&max="+str(max)+"&col=1&base=10&format=plain&rnd=new")
        randlist=data.readlines()
        data.close()
        randlist[:] = [line.rstrip('\n') for line in randlist]
        print randlist
        randlist = [int(i) for i in randlist]
        
        return randlist
    
    except:
        randlist=[]
        randlist.append(-1)
        return randlist

def getfloat(amount):
    global randlist
    try:
        url_opener = myURLopener()
        url_addr = "http://www.random.org/decimal-fractions/?num="+str(amount)+"&dec=10"+"&col=1&format=plain&rnd=new"
        data = url_opener.open(url_addr)
        randlist=data.readlines()
        data.close()
        randlist[:] = [float(line.rstrip('\n')) for line in randlist]
        
        return randlist
    
    except:
        randlist=[]
        randlist.append(-1)
        return randlist
