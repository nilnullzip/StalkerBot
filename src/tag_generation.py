#!/usr/bin/python

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


import json, urllib2
from urllib import quote

def articleApiRequest( url, key ):
    tag_list = []
    if url==None: 
        return tag_list
    api_base = 'http://www.diffbot.com/api/article?token=' + key + '&url='
    api_key = api_base + quote(url, '') + '&tags'
    #print 'api key : ' + api_key
    req = urllib2.Request(api_key)
    try:
        response = urllib2.urlopen(req)
    except urllib2.HTTPError, e:
        return []
    
    json_response = response.read()
    objs = json.loads(json_response)
    
    return objs

def test():
    # DAS Note: No Longer need tests on non-article links. Earlier function omits those
    # from being passed to generateTags
#    
#    # Test out your program
#    # 2082625 is a poll thread
#    tag_list = generateTags( "http://news.ycombinator.com/item?id=2082625" )
#    print 'poll thread'
#    for i in tag_list:
#        print i
#    print
#    
#    # 2696937 is a link
#    tag_list =  generateTags( "http://news.ycombinator.com/item?id=2696937" )
#    print 'link'
#    for i in tag_list:
#        print i
#    print
#    
#    # 2654788 is a tell HN
#    tag_list = generateTags( "http://news.ycombinator.com/item?id=2654788" )
#    print 'tell HN'
#    for i in tag_list:
#        print i
#    print
    
    tag_list = articleApiRequest( "http://www.amazon.com/b/ref=amb_link_355091782_4?ie=UTF8&node=2658409011&pf_rd_m=ATVPDKIKX0DER&pf_rd_s=center-2&pf_rd_r=1XCE7Q7BHQQA2C69H0SW&pf_rd_t=101&pf_rd_p=1291940422&pf_rd_i=163856011" )
    print '4th test'
    for i in tag_list:
        print i
    print
    
    url = 'http://www.huffingtonpost.com/2011/03/04/frozen-smoke-energy-storage_n_830894.html'
    print 'url used : ' + url
    tag_list = articleApiRequest(url)
    print 'Test for tag generation'
    for i in tag_list:
        print i
    print

#test()
