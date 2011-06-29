import urllib
import urllib2
import sys, base64, re, json

def getSentiment(content) :
  url = "http://effectcheck.com/RestApi/Score"
  username = 'team12'
  pwd = 'bBH3HJ6kW2FerXOazkjmDXha5FGnW8aWl1JMqF2KdXsWD0LtuJmRpdN4Ugy22IEO'

  req = urllib2.Request(url)

  base64string = base64.encodestring('%s:%s' % (username, pwd)).replace('\n', '')
  authheader =  "Basic %s" % base64string
  req.add_header("Authorization", authheader)

  params = urllib.urlencode({
    'Category' : 'HackerNews Comments (Large)',
    'Content'  : content
  })

  try:
    handle = urllib2.urlopen(req, params)
  except IOError, e:
    print e, IOError
    sys.exit(1)

#{"WordCount":270,"Anxiety":{"ChartLevel":2.2276509814971353,"AveragePerWord":0.19},"Hostility":{"ChartLevel":3.2857142857142847,"AveragePerWord":0.14},"Depression":{"ChartLevel":2.6934900542495477,"AveragePerWord":0.14},"Confidence":{"ChartLevel":1.287749287749284,"AveragePerWord":0.51},"Compassion":{"ChartLevel":2.397647578552101,"AveragePerWord":0.19},"Happiness":{"ChartLevel":3.0773279352226726,"AveragePerWord":0.23}}


  response = handle.read()

 # return response

#with open('../Dropbox/Hackathon/user_data/test_comments.txt', 'r') as f:
#  data = f.read()
#  response = getSentiment(data)

  objs = json.loads(response)
  #print objs
  #for o in objs [u'Anxiety:
   # print o

 # for k, v in dict.iteritems();
 # print k, v
  sent = {'Anxiety': 0, 'Hostility' : 0, 'Depression' : 0, 'Confidence' : 0, 'Compassion' : 0, 'Happiness' : 0}

  for k, v in sent.iteritems():
    sent[k] = objs[k]['ChartLevel']

  return sent



def merge(d1, d2, merge=lambda x,y:y):
    """
    Merges two dictionaries, non-destructively, combining 
    values on duplicate keys as defined by the optional merge
    function.  The default behavior replaces the values in d1
    with corresponding values in d2.  (There is no other generally
    applicable merge strategy, but often you'll have homogeneous 
    types in your dicts, so specifying a merge technique can be 
    valuable.)

    Examples:

    >>> d1
    {'a': 1, 'c': 3, 'b': 2}
    >>> merge(d1, d1)
    {'a': 1, 'c': 3, 'b': 2}
    >>> merge(d1, d1, lambda x,y: x+y)
    {'a': 2, 'c': 6, 'b': 4}

    """
    result = dict(d1)
    for k,v in d2.iteritems():
        if k in result:
            result[k] = merge(result[k], v)
        else:
            result[k] = v
    return result