# -*- coding:utf-8 -*-
import urllib2
import re
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
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393',
    'Referer':'https//www.baidu.com'
}

class Page_url(object):
    """
    获取小升初的问题列表页面（，每个城市多个列表）
    """

    def __init__(self, request = None, city = None, city_id = None):
        self._request = request
        self._city = city
        self._city_id = city_id
    
    def Spider(self,request):
        
        url_list = []
        suburl = request[0:len(request)-6]
        #print suburl

        fails = 0
        while(True):
            if fails >= 3:
                break
            try:
                a_request =urllib2.Request(request.strip(),headers=loginHeaders)
                response = urllib2.urlopen(a_request,timeout=20)
                htree = Html.parse(response)
                response.close()
                page = htree.xpath('//*[@id="fd_page_top"]/span/label/span/text()')[0].strip()
                page = int(re.search('[0-9]+',page).group())
                for i in range(1,page):
                    url_list.append(suburl+str(i)+'.html')
                #response = urllib2.urlopen(line[0].strip(), timeout = 20).read()
            except:
                fails+=1
            else:
                break
        

        #htree = Html.parse(response)
        #response.close()
        #page = htree.xpath('//*[@id="fd_page_top"]/span/label/span/text()')[0].strip()
        #page = int(re.search('[0-9]+',page).group())
        #for i in range(1,page):
            #url_list.append(suburl+str(i)+'.html')
        return url_list
            
    def Write(self, url_list, _city_):
        lines = []
        for url in url_list:
            lines.append(url+'\t\n')
        fout = file("D:\\Aaron\\"+_city_+".txt",'w')
        fout.writelines(lines)
        fout.close()

    def run(self):
        #for i in range(len(self._requestlilst)):
        return self.Spider(self._request)
        
        #self.Write(url_list, self._city)

                
    
'''
if __name__ == '__main__':
    requestlilst = ['http://jzb.com/bbs/forum-2033-1.html', 'http://jzb.com/bbs/forum-3243-1.html', 'http://jzb.com/bbs/forum-3354-1.html']
    city = ['sad_1','sad_2','sad_3']
    city_id = [1,2,3]
    city_id = 1
    page_url = Page_url(requestlilst, city, city_id)
    page_url.run()
    print 'Done'
'''
