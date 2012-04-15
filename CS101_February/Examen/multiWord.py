#Multi-word Queries

#Triple Gold Star

#For this question, your goal is to modify the search engine to be able to
#handle multi-word queries.  To do this, we need to make two main changes:

#    1. Modify the index to keep track of not only the URL, but the position
#    within that page where a word appears.

#    2. Make a version of the lookup procedure that takes a list of target
#    words, and only counts a URL as a match if it contains all of the target
#    words, adjacent to each other, in the order they are given in the input.
 
#For example, if the search input is "Monty Python", it should match a page that
#contains, "Monty Python is funny!", but should not match a page containing
#"Monty likes the Python programming language."  The words must appear in the
#same order, and the next word must start right after the end of the previous
#word.

#Modify the search engine code to support multi-word queries. Your modified code
#should define these two procedures:

#    crawl_web(seed) => index, graph
#        A modified version of crawl_web that produces an index that includes
#        positional information.  It is up to you to figure out how to represent
#        positions in your index and you can do this any way you want.  Whatever
#        index you produce is the one we will pass into your multi_lookup(index,
#        keyword) procedure.

#    multi_lookup(index, list of keywords) => list of URLs
#        A URL should be included in the output list, only if it contains all of
#        the keywords in the input list, next to each other.


def multi_lookup(index, query):
    if len(query) == 0: return []
    elif len(query) == 1: return getLinks( index[query[0]] ) 
    else:
        if query[0] not in index: return []
        workingLinks = getWorkingLinks(index,index[query[0]],query[1:])
        
        finalLinks = []
        for link in workingLinks:
            firstWordPos = getWordPosInLink(index,query[0],link)
            for position in firstWordPos:
                valid = False
                pos = position + len(query[0]) + 1
                for w in query[1:]:
                    wordPos = getWordPosInLink(index,w,link)
                    if pos in wordPos: ##Si esta a la par
                        valid = True
                        pos = pos + len(w) + 1
                    else:
                        valid = False
                        break
                if valid:
                    if link not in finalLinks:
                        finalLinks.append(link)
        return finalLinks

def getWordPosInLink(index,word,link):
    for t in index[word]:
        if t[0] == link:
            return t[1]
    return [] 

def getWorkingLinks(index,linksWordOne,words):
    workingLinks = []
    for link in linksWordOne:
        valid = False
        for word in words:
            if word not in index: return []
            else:
                if containsLink( getLinks( index[word] ),link ):
                    valid = True
                else:
                    valid = False
                    break
        if valid:
            workingLinks.append(link[0])
    return workingLinks

def getLinks(place):
    r = []
    for reg in place:
        r.append(reg[0])
    return r

def containsLink(links,link):
    for l in links:
        if link[0] == l:
            return True
    return False

def get_keyword_indexes(pageContent,keyword):
    indexes = []
    index = pageContent.find(keyword)
    while index != -1:
        indexes.append(index)
        index = pageContent.find(keyword,index+1)
    return indexes

def add_to_index(index, keyword, url,content):
    if keyword in index:
        index[keyword].append([url,get_keyword_indexes(content,keyword)])
    else:
        index[keyword] = [ [url, get_keyword_indexes(content,keyword)   ] ]

def crawl_web(seed): # returns index, graph of inlinks
    tocrawl = [seed]
    crawled = []
    graph = {}  # <url>, [list of pages it links to]
    index = {} 
    while tocrawl: 
        page = tocrawl.pop()
        if page not in crawled:
            content = get_page(page)
            #print "CONTENT"
            #print content
            add_page_to_index(index, page, content)
            #print "INDEX"
            #print index
            outlinks = get_all_links(content)
            #print "OUTLINKS"
            #print outlinks
            graph[page] = outlinks
            #print "TO CRAWL"
            #print tocrawl
            union(tocrawl, outlinks)
            #print "PAGE"
            #print page
            crawled.append(page)
           
    return index, graph


def get_next_target(page):
    start_link = page.find('<a href=')
    if start_link == -1: 
        return None, 0
    start_quote = page.find('"', start_link)
    end_quote = page.find('"', start_quote + 1)
    url = page[start_quote + 1:end_quote]
    return url, end_quote

def get_all_links(page):
    links = []
    while True:
        url, endpos = get_next_target(page)
        if url:
            links.append(url)
            page = page[endpos:]
        else:
            break
    return links


def union(a, b):
    for e in b:
        if e not in a:
            a.append(e)

def add_page_to_index(index, url, content):
    words = content.split()
    for word in words:
        add_to_index(index, word, url,content)
        
def lookup(index, keyword):
    if keyword in index:
        return index[keyword]
    else:
        return None
    



cache = {
   'http://www.udacity.com/cs101x/final/multi.html': """<html> <html>
<body>

<a href="http://www.udacity.com/cs101x/final/a.html">A</a><br>
<a href="http://www.udacity.com/cs101x/final/b.html">B</a><br>

</body>
""", 
   'http://www.udacity.com/cs101x/final/b.html': """<html>
<body>

Monty likes the Python programming language
Thomas Jefferson founded the University of Virginia
When Mandela was in London, he visited Nelson's Column.

</body>
</html>
""", 
   'http://www.udacity.com/cs101x/final/a.html': """<html>
<body>

Monty Python is not about a programming language
Udacity was not founded by Thomas Jefferson
Nelson Mandela said "Education is the most powerful weapon which you can
use to change the world."
</body>
</html>
""", 
}

def get_page(url):
    if url in cache:
        return cache[url]
    else:
        print "Page not in cache: " + url
        return None
    

#Here are a few examples from the test site:

index, graph = crawl_web('http://www.udacity.com/cs101x/final/multi.html')

#print index

#print getWordPosInLink(index,'Monty',"http://www.udacity.com/cs101x/final/a.html")

#print multi_lookup(index, ['Python'])
#>>> ['http://www.udacity.com/cs101x/final/b.html', 'http://www.udacity.com/cs101x/final/a.html']

print multi_lookup(index, ['Monty', 'Python'])
#>>> ['http://www.udacity.com/cs101x/final/a.html']

#print multi_lookup(index, ['Python', 'programming', 'language'])
#>>> ['http://www.udacity.com/cs101x/final/b.html']

#print multi_lookup(index, ['Thomas', 'Jefferson'])
#>>> ['http://www.udacity.com/cs101x/final/b.html', 'http://www.udacity.com/cs101x/final/a.html']

#print multi_lookup(index, ['most', 'powerful', 'weapon'])
#>>> ['http://www.udacity.com/cs101x/final/a.html']
