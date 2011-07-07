import urllib, re, time
from BeautifulSoup import BeautifulSoup

def sanitize_html(value):
    soup = BeautifulSoup(value)
    for tag in soup.findAll(True):
        tag.hidden = True
    return soup.renderContents()

hexentityMassage = [(re.compile('&#x([^;]+);'), lambda m: '&#%d' % int(m.group(1), 16))]

def convert(html):
    return BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES, markupMassage=hexentityMassage).contents[0].string



def scrape(userID):
    allcomments = []
    allpostID = []
    result = []
    nexturl = 'http://news.ycombinator.com/threads?id=' + userID
    commentfieldre = re.compile('<a href="user\?id=' + userID + '">' + userID + '<(.*?)></td>', re.DOTALL)
    commentre = re.compile('class="comment"><font color=.......>(.*?)</fo', re.DOTALL)
    postIDre = re.compile('<a href="item\?id=(.*)">parent</a> \| on: <a href="item\?id=(\\1)">')
    nexturlre = re.compile('class="title"><a href="(.*)" rel')

    while (nexturl and len(result) < 10):
        content = urllib.urlopen(nexturl).read()
        allcommentfield = commentfieldre.findall(content)
        for currfield in allcommentfield:
            postIDmatch = postIDre.search(currfield)
            if postIDmatch:
                postID = postIDmatch.group(1)
                commentmatch = commentre.search(currfield)
                comment = convert(sanitize_html(commentmatch.group(1)))
                result.append([postID, comment])        
            nexturlmatch = nexturlre.search(content)
            if nexturlmatch:
                nexturlappend = nexturlmatch.group(1)
                nexturl = 'http://news.ycombinator.com/' + nexturlappend[1:]
            else:
                nexturl = []
            time.sleep(.05)
    return result


#commentIdStructure = scrape("pg")
#for elt in commentIdStructure:
#    print elt
#print len(commentIdStructure)
