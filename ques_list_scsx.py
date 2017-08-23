# -*- coding:utf-8 -*-

import urllib2
import re
import time
import random
import codecs
import lxml.html as Html
import lxml.etree as etree
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import cookielib
httpHandler = urllib2.HTTPHandler(debuglevel=1)
httpsHandler = urllib2.HTTPSHandler(debuglevel=1)
cookie = cookielib.CookieJar()
cookieHandler = urllib2.HTTPCookieProcessor(cookie)
opener = urllib2.build_opener(cookieHandler, httpHandler, httpsHandler)
urllib2.install_opener(opener)

loginHeaders = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
    'Referer':'https//www.baidu.com'
}


class Ques_List(object):
    '''
    获取每个问题的具体入口地址
    '''
    def req_load(self, path):
        lists = []
        for line in codecs.open(path,'r','utf-8'):
            lists.append(line.strip())
        return lists

    def __init__(self,requestlist = None, city = None, city_id = None):
        self._reqlist = requestlist
        self._city = city
        self._city_id = city_id
        self._urlslists = []
    
    def Spider(self,request):
        fails = 0
        while(True):
            if fails >= 3:
                break
            try:
                a_request =urllib2.Request(request.strip(),headers=loginHeaders)
                response = urllib2.urlopen(a_request,timeout=20).read()

                #response = urllib2.urlopen(line[0].strip(), timeout = 20).read()
            except:
                fails+=1
            else:
                break
        time.sleep(random.randint(1,2))
        # pattern = re.compile(r'http://jzb.com/bbs/thread-[0-9]+-1-1.html')
        pattern = re.compile(r'http://bbs.scsxks.com/forum.php\?mod=viewthread&amp;tid=[0-9]+&amp;extra=page%\w+')
        urls = pattern.findall(response)
        # remove dulplicate url
        new_urls = set(urls)
        for url in new_urls:
            self._urlslists.append(url.strip())
        print 'parse %d pages in url %s' % (len(new_urls), request)

    def Write(self):
        
        fout = file('D:\\Aaron\\jzb\\data\\'+self._city+'.txt','w')
        lines = []
        for url in self._urlslists:
            lines.append(url.strip()+'\t\n')
        fout.writelines(lines)
        fout.close()
    
    def run(self):
        for i in range(len(self._reqlist)):
            self.Spider(self._reqlist[i])
        #print len(self._urlslists)
        #print len(self._reqlist)
        #self.Write()
        urls = list(set(self._urlslists))
        print '--->num_questions with repeats:',len(self._urlslists)
        print '--->num_questions =:',len(urls)
        return urls
        #return self._urlslists
        print 'Done'


# if __name__ == '__main__':
#     # req_path = 'D:\\Aaron\\sad_3.txt'
#     req_path = ['http://bbs.scsxks.com/forum.php?mod=forumdisplay&fid=68&page=23']
#     city = 'wwww'
#     city_id = 2
#     quelist = Ques_List(req_path,city,city_id)
#     urls = quelist.run()
#     print 'Finished'



