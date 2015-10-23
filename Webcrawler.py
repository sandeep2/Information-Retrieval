## The given crawler uses BFS algorithm.
## The crawlingLink is a queue which has all the links at a purticular depth and removes the first link when it is crawled
## outlinks are the child links of a given link.
## seen are "set" of links. This is used to keep a track of all the lists that we have seen. We use set because we need to remove all the duplicate links.



from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch 
import urllib2
import re
import sys
import time
from collections import deque
f=open('outputs.txt','w+')
f.close()
depth = 1
crawlinglink =[]
outlinks = []
seen = set()
total = 0
es = Elasticsearch("localhost:9200",timeout = 600,max_retries = 10,revival_delay = 0)
## focusedcrawler: URL KEYPHRASE -> CrawledLinks
## Given: We feed the url and a keyphrase to the function.
## Results: The below function crawls all the links which has the specific keyphrase in it.
def focusedcrawler(url,word):
    global depth, crawlinglink, outlinks, seen,total
    crawlinglink = [url]
    seen = set(url)
    crawled = []
    count = 0 # to keep track of no of url's crawled having keyphrase
    total = 0 # to keep track of all the url's checked
    while len(crawlinglink) > 0 and depth <=5 and count<=1000:
        try:
            time.sleep(0.1)
            readlink = urllib2.urlopen(crawlinglink[0]).read()
        except:
            print("Error in URL",crawlinglink[0]) # Error when unable to open a purticular url
        soup = BeautifulSoup(readlink,"html.parser")
        wordcase = re.compile(word,re.IGNORECASE)
        if word != "" and wordcase.search(soup.get_text()) is None:
            print("This link "+crawlinglink[0]+" doesn't have the word "+word)
            nthelement(crawlinglink,0)
            total+=1
            if not zerolist(crawlinglink):
                continue
            if zerolist(crawlinglink):
                crawlinglink = outlinks
                outlinks = []
                depth+=1
                continue
        nthelement(crawlinglink,0)
        getlink = soup.find("link", rel = "canonical")
        getref = getlink['href']
        crawled.append(getref)
        crawled = uniquelist(crawled)
        total +=1
        if "#" in getref:
            getref= getref.rpartition('#')[0]
        print("Crawled link is "+str(getref)+" and the number of links left at this depth is "+str(len(crawlinglink)))
        count+=1
        findanchor = soup.findAll('a',href= True)
        for anchor in findanchor:
            refanc = anchor['href']
            if re.compile(re.escape('/wiki/')).match(refanc) and ':' not in refanc and "/wiki/Main_Page" not in refanc and "https://en.wikipedia.org/wiki/Hugh_of_Saint-Cher" not in refanc:
                refancc = "http://en.wikipedia.org" + refanc
                if refancc not in seen:
		    es.index(index="test_index_skpr", doc_type="document", id=refancc, body=contents)	
                    seen.add(refancc)
                    outlinks.append(refancc)

        if zerolist(crawlinglink):
            crawlinglink = outlinks
            outlinks = []
            depth += 1
            print("Depth "+str(depth - 1)+" is done and "+" Number of crawled links at this depth is "+str(len(crawlinglink)))
            print ("Number of Links till now are "+str(total))
    return set(crawled)

def zerolist(list):
    if len(list) == 0:
        return True
    else:
        return False

def uniquelist(list):
  unik = []
  for i in list:
    if i not in unik:
      unik.append(i)
  return unik

def nthelement(list,num):
    del list[num]

typecrawling = raw_input("Type f for focused and u for unfocused\n")
if typecrawling == 'f':
    unique_links = focusedcrawler("http://en.wikipedia.org/wiki/Hugh_of_Saint-Cher","concordance")
else:
    unique_links = focusedcrawler("http://en.wikipedia.org/wiki/Hugh_of_Saint-Cher","")
f = open("outputs.txt","w+")
serial = 1
print str(total)
for link in unique_links:
    print(str(serial)+". "+link)
    f.write(str(serial)+". "+link)
    f.write('\n')
    serial+=1