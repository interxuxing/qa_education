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
            fout = file('./qa_g12e.txt','w')

        count = 0
        for request in self._requestlist:
            try:
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
                res_question = htree.xpath('//*[@class = "title"]/h1/text()')
                questions = [item.strip('') for item in res_question if item.strip('') != '']
                question = questions[0]
                if len(question) < 1:
                    continue
                # get answers
                res_answers = htree.xpath('//*[@class = "postcontent"]/text()')
                line = [item for item in res_answers if item.strip('') != '']

                # get subquestion, subquestion has the special cases of font color
                subq_answers = htree.xpath('//*[@class = "postcontent"]//*/font/text()')
                subquestion = ''
                has_sub_font = False
                if len(subq_answers) > 1:
                    # there are subquestions in list
                    has_sub_font = True
                    for i in range(len(subq_answers)):
                        if subq_answers[i].strip() != '':
                            subquestion += subq_answers[i].strip()
                            subquestion += ' '
                else:
                    # there is no subquestion in the list, then get it from line
                    subquestion = line[0].strip()
                # get url
                url = request.strip()
                # get answer
                answers = ''
                if has_sub_font == True:
                    start_range = 0
                else:
                    start_range = 0
                for i in range(start_range,len(line)):
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



if __name__ == '__main__':
    # requestlist = ['http://jzb.com/bbs/thread-5732295-1-1.html', \
    #                'http://jzb.com/bbs/thread-2824201-1-1.html']
    requestlist = ['http://bbs.g12e.com/forum-262-232/topic-1699158.html']
    spider = Ques_ans(requestlist, 'sad')
    spider.Spider()
    spider.Write()
    print 'Done'





