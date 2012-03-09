# Copyright (C) 2011 by Kevin Nam Truong, Daniel Steinberg, Debasish Das, Juan Pineda, Melissa Miranda, and Victoria Pan

# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# `THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import urllib
import urllib2
import sys, base64, re, json
from read_key import readKey

def getSentiment(content, key) :
  url = "http://effectcheck.com/RestApi/Score"
  username = 'team12'
  pwd = key

  req = urllib2.Request(url)

  base64string = base64.encodestring('%s:%s' % (username, pwd)).replace('\n', '')
  authheader =  "Basic %s" % base64string
  req.add_header("Authorization", authheader)

  params = urllib.urlencode({
    # No longer works
    # 'Category' : 'HackerNews Comments (Large)',
    'Category' : 'Generic',
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
