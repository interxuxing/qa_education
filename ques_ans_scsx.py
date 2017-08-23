# -*- coding:utf-8 -*-
import urllib2
import re
import random
import lxml.html as Html
import lxml.etree as etree
import sys
reload(sys)
import time
sys.setdefaultencoding('utf-8')

import cookielib
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

class Ques_ans(object):
    '''
    抓取每一个帖子里的问题和答案
    '''
    def __init__(self, requestlist = None, city = None, city_id = None):
        self._requestlist = requestlist
        self._city  =city
        self._city_id = city_id
        self._content = []

    def Spider(self, dump=True):
        if dump:
            fout = file('./qa_scsx.txt','w')

        count = 0
        for request in self._requestlist:
            try:
                request = request.replace('amp;', '')
                a_request = urllib2.Request(request.strip(), headers=loginHeaders)
                response = urllib2.urlopen(a_request,timeout=20)
                htree = Html.parse(response)
                response.close()
            except:
	            continue
            else:
                line = []
                question = ''
                # question += str(htree.xpath('//*[@id="thread_subject"]/text()')[0].strip())
                # line.extend(htree.xpath('//*[@class = "t_f"]/text()'))
                # get question
                res_question = htree.xpath('//*[@id="thread_subject"]/text()')
                questions = [item.strip('') for item in res_question if item.strip('') != '']
                if len(questions) < 1:
                    print 'no page found in %s' % request
                    continue
                question = questions[0]

                # get answers
                res_answers = htree.xpath('//*[@class = "t_f"]/text()')
                line = [item for item in res_answers if item.strip('') != '' \
                        and item.strip('') != '\r\n']
                if len(line) < 1:
                    continue
                # there is no subquestion in the list, then get it from line
                subquestion = line[0].strip()
                # get url
                url = request.strip()
                # get answer
                answers = ''
                for i in range(0,len(line)):
                    if line[i].strip() != '':
                        answers += line[i].strip()
                        answers += '_&_'

                tmp = []
                tmp.append(url)
                tmp.append(question)
                tmp.append(subquestion)
                tmp.append(answers)
                #print request
                time.sleep(random.randint(1,2))
                self._content.append(tmp)

                count = count + 1
                if dump:
                    for x in tmp:
                        fout.write(x.strip()+'\t\n')
                print '%d/%d dump content in url %s' % (count, len(self._requestlist), url)

    def Write(self, out_file):
        #print len(self._content)
        fout = file('./'+ out_file,'w')
        for line in self._content:
            for x in line:
                fout.write(x.strip()+'\t\n')
    
    def run(self):
        self.Spider()
        print '-------------------->'
        print 'Now start write'
        self.Write()



# if __name__ == '__main__':
#     # requestlist = ['http://jzb.com/bbs/thread-5732295-1-1.html', \
#     #                'http://jzb.com/bbs/thread-2824201-1-1.html']
#     requestlist = ['http://bbs.scsxks.com/forum.php?mod=viewthread&tid=244&extra=page%3D1']
#     spider = Ques_ans(requestlist, 'sad')
#     spider.Spider()
#     spider.Write()
#     print 'Done'





