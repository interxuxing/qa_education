# -*- coding:utf-8 -*-
import urllib2
import re
import sys
from pre2mid import *
reload(sys)
sys.setdefaultencoding('utf-8')


def Spider():
    response = urllib2.urlopen('http://jzb.com/?cookie=no').read()
    p_url_city = re.compile(r'<a.*?href="http://jzb.com/bbs/[a-z][a-z].*?".*?<\/a>')
    url_and_cities = p_url_city.findall(response)
    
    urls = []
    cities = []

    p_city = re.compile(r'>.*<')
    p_url = re.compile(r'http://jzb.com/bbs/[a-z]+/')


    for url_and_city in url_and_cities:
        url = p_url.findall(url_and_city)[0]
        urls.append(url.strip())
        city = p_city.findall(url_and_city)
        cities.append(city[0][1:len(city[0])-1].strip())
    return urls,cities


def main():
    #end = time.time()
    p = Pool()
    urls,cities = Spider()
    print 'Run task %s (%s)...' %(name, os.getpid())
    for i in range(len(urls)):
        p.apply_async(long_time_task, args = (i,))
    
    print 'Waiting for all subprocess done...'
    p.close()
    p.join()
    print 'All subprocesses done'


if __name__ == '__main__':
    main()


