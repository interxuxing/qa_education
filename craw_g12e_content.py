# -*- coding:utf-8 -*-
import ques_list
import ques_ans


if __name__ == '__main__':
    req_path_list = ['http://bbs.g12e.com/forum-262-232/']
    req_path_base = 'http://bbs.g12e.com/forum-262-232/offset-'
    num_pages = 109
    for i in range(1, num_pages):
        # new page
        new_page = ('%s%d' % (req_path_base, i*30))
        req_path_list.append(new_page)

    # now download the images in each page
    city = 'wwww'
    city_id = 2
    qlist = ques_list.Ques_List(req_path_list, city, city_id)

    # get all the pages
    page_list = qlist.run()

    # now craw the content in all the page_list
    ans = ques_ans.Ques_ans(page_list, 'sad')
    ans.Spider(dump=True)
    # ans.Write('qa_g12e.txt')
    print 'Done'


