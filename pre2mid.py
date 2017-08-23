# -*- coding:utf-8 -*-
import urllib2
import re
import sys
import codecs
import time
from page_url import Page_url
from ques_ans import Ques_ans
from ques_list import Ques_List
import os
from multiprocessing import Pool
import logging
import cookielib

reload(sys)
sys.setdefaultencoding('utf-8')

logging.basicConfig(level = logging.INFO,format = '%(asctime)s %(message)s',datefmt = '%a, %d %b %Y %H:%M:%S', filename = 'log.txt')

httpHandler = urllib2.HTTPHandler(debuglevel=1)
httpsHandler = urllib2.HTTPSHandler(debuglevel=1)
cookie = cookielib.CookieJar()
cookieHandler = urllib2.HTTPCookieProcessor(cookie)
opener = urllib2.build_opener(cookieHandler, httpHandler, httpsHandler)
urllib2.install_opener(opener)

loginHeaders = {
    'User-Agent':'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.0 Chrome/30.0.1599.101 Safari/537.36',
    'Referer':'https//www.baidu.com'
}


def get_city_url():

    request = urllib2.Request('http://jzb.com/?cookie=no',headers=loginHeaders)
    response = urllib2.urlopen(request,timeout=20).read()

    p_url_city = re.compile(r'<a.*?href="http://jzb.com/bbs/[a-z][a-z].*?".*?<\/a>')
    url_and_cities = p_url_city.findall(response)
    urls = []
    cities = []
    p_city = re.compile(r'>.*<')
    p_url = re.compile(r'http://jzb.com/bbs/[a-z]+/')
    for url_and_city in url_and_cities:
        url = p_url.findall(url_and_city)
        urls.append(''.join(url))
        city = p_city.findall(url_and_city)
        cities.append(city[0][1:len(city[0]) - 1])
    results = []
    for i in range(0, len(urls)):
        tmp = []
        tmp.append(urls[i])
        tmp.append(cities[i])
        tmp.append(str(i))
        results.append(tmp)
    return results

def pre2mid(lines):
    p_url_info = re.compile(r'<a.*?href="http://jzb.com/bbs/forum-[0-9]+-1.html.*?".*?<\/a>')
    urls = []
    p_url = re.compile(r'http://jzb.com/bbs/forum-[0-9]+-1.html')
    for line in lines:
        #print line[0].strip()
        #print '*********************8'
        fails = 0
        while(True):
            if fails >= 3:
                break
            try:
                request = urllib2.Request(line[0].strip(),headers=loginHeaders)
                response = urllib2.urlopen(request,timeout=20).read()
                
                #response = urllib2.urlopen(line[0].strip(), timeout = 20).read()
            except:
                fails+=1
            else:
                break
        #print response
        url_infos = p_url_info.findall(response)
        #print len(url_infos)
        tmp = []
        for url_info in url_infos:
            #print url_info
            if url_info.find('小升初') > 0 :
                s = p_url.findall(url_info)
                tmp.append(s[0])
                tmp.append(line[1])
                tmp.append(line[2])
                urls.append(tmp)
                break

    print len(urls)
    print urls[0]
    return urls


def long_time_task(x):
    print 'run %s task (%s)...'%(x[1],os.getpid())
    time.sleep(2)
    page_url = Page_url(x[0], x[1], x[2])
    page_list = page_url.run()

    starttime = time.time()
    ques_list = Ques_List(page_list, x[1], x[2])
    que_list = ques_list.run()
    info = 'task' + x[1] + 'num_questions='+str(len(que_list))
    logging.info(info)
    #print 'task (%s) len(list)=(%s)'%(x[1],len(que_list))
    starttime = time.time()
    q_a = Ques_ans(que_list,x[1],x[2])
    q_a.run()
    info = 'task' + x[1] + 'done\n'
    logging.info(infos)
    #print 'task %s ,(%s) Done' %(x[1],os.getpid())

def main():
    #url_p2m = [['http://jzb.com/bbs/forum-3260-1.html','sad', '1']]
    lines = get_city_url()
    url_p2m = pre2mid(lines)
    
    fout = file('./data/all_city.txt','w')
    for x in url_p2m:
        fout.write(x[0]+'\t'+x[1]+'\t'+x[2]+'\t\n')
    fout.close()


    #p = Pool()
    print len(url_p2m)
    logging.info('----------->'+str(len(url_p2m)))
    for x in url_p2m:
        long_time_task(x)
    logging.info('Waiting for all process Done')
    #p.close()
    #p.join()
    logging.info('\n--(%s)-->All Done<-----\n')

    #break

'''
    x = ['http://jzb.com/bbs/forum-3365-1.html','qqqqq','55']
    page_url = Page_url(x[0], x[1], x[2])
    print '--->Rage_URL'
    starttime = time.time()
    page_list = page_url.run()
    print len(page_list)
    print 'time = :',time.time()-starttime
    print '--->Ques_LIST'

    starttime = time.time()
    ques_list = Ques_List(page_list, x[1], x[2])
    que_list = ques_list.run()
    print len(que_list)
    print 'time = :',time.time()-starttime
    print '--->Ques_ans'
    starttime = time.time()
    q_a = Ques_ans(que_list,x[1],x[2])
    q_a.run()
    print 'time = :',time.time()-starttime
    print 'Done'
'''

if __name__ == '__main__':
    #long_time_task(['http://jzb.com/bbs/forum-3260-1.html','sad', '1'])
    main()




