## 问答的例子参考
demo_doc2sim_education.py
demo_doc2sim_gaokao.py

## 爬虫文件的使用
各个文件的作用：
1. city.py


2. pre2mid.py
获取jzb.com 各个城市的主入口,返回各个城市的小升初的入口地址

3. page_url.py
获取小升初的问题列表页面（，每个城市多个列表）

4. ques_list.py
获取每个问题的具体入口地址

5. ques_ans.py
抓取问题和答案

总章程：
在 city.py 页面设置多进程，一个城市是一个进程，传入进程的参数是 url 和 城市的名字。

最终呈现：每个城市一个txt，
格式：
question_url
question
subquestion
answers
其中，由于有多个answer per question ，所以问题之间用特殊符号 ‘ ’
