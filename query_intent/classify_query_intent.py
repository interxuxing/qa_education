# -*- coding:utf-8 -*-

"""
This script is used to classify the query intent given the inital query

The categories of the query intent include:
1. 学校专业信息
[学校名，专业][排名][怎么样，怎样]
[学校名][哪些好]
[就业]
2. 志愿填报
[年份][xx省，城市][男女生][xxx分数，排名xxx][介词，副词][志愿填报][学校，专业]

3. 备考经验
[怎样，如何][提高，增加，学习，注意，xxx][专有名词]

4. 高考名词概念
[xxx][啥意思，是啥，是什么意思]

5. 其他杂项
[xxx]

"""


import csv
import os
import codecs

import re
import os
import jieba
import jieba.posseg
import gensim

try:
    import cPickle as pickle
except:
    import pickle

import sys

reload(sys)
sys.setdefaultencoding("utf-8")

'''
Pre-defined keywords in each class
'''

KEYWORDS_SCHOOL = ['分数线','录取线','收分线','批次','大学','学院','独立学院','软实力','硬实力','985','211','高等院校','排名','学校','招生章程','招生计划','学费', '专业']
CONDITION_SCHOOL = ['如何', '怎么样', '哪个', '比较', '更', '好', '更加', '适合']

KEYWORDS_ZHIYUAN = ['分数','志愿','征集','填报','平行志愿','提前批','艺术生','体育生','特长生','国防生','退档','名次','专业','排名','军校','服从调剂','调剂','第一志愿','第二志愿','报考']
CONDITION_ZHIYUAN = ['多少', '大概', '低','高','怎么']

KEYWORDS_BEIKAO = ['提高','阅读','作文','技巧','复习','英语','语文','理综','文综','焦虑','紧张','失眠','饮食','笔','准考证','身份证','药','家长','调节','主观题','注意','期间']
CONDITION_BEIKAO = ['如何', '怎么样', '哪个好', '比较']

KEYWORDS_CONCEPTS = ['大专','高职','单招','预科','加分','分数级差','农村专项','助学贷款','自主招考','一本','二本','三本','省控线','拟录取','提前批次','预录取','专业代码','平行志愿']
CONDITION_CONCETPS = ['什么', '意思', '啥']

KEYWORDS_OTHERS = []
CONDITION_OTHERS = []


dict_school = {'id':'100', 'keywords':KEYWORDS_SCHOOL, 'condition':CONDITION_SCHOOL}
dict_zhiyuan = {'id':'200', 'keywords':KEYWORDS_ZHIYUAN, 'condition':CONDITION_ZHIYUAN}
dict_beikao = {'id':'300', 'keywords':KEYWORDS_BEIKAO, 'condition':CONDITION_BEIKAO}
dict_concepts = {'id':'400', 'keywords':KEYWORDS_CONCEPTS, 'condition':CONDITION_CONCETPS}
dict_others = {'id':'500', 'keywords':KEYWORDS_OTHERS, 'condition':CONDITION_OTHERS}

dict_list = [dict_school, dict_zhiyuan, dict_beikao, dict_concepts, dict_others]

def load_stopwords_file(data_dir, stopwords_file):
    '''
        load the stopwords file, return a list, with each element is a string in each line
    '''
    stopwords_list = []
    idx = 0
    with open(os.path.join(data_dir, stopwords_file)) as fid:
        for item in fid:
            stopwords_list.append(item.strip('\n'))
            idx = idx + 1
    print 'loading %d stopwords done!' % idx

    return stopwords_list

def dump_corpus_csv(corpus_file, csv_file):
    '''
    dump the corpus file to a csv file, each line in csv file is a question
    :param corpus_file: input corpus file
    :param csv_file:  input csv file
    :return:
    '''
    # with open('test.csv', 'wb') as csvfile:
    #     csvfile.write(codecs.BOM_UTF8)
    #     spamwriter = csv.writer(csvfile, dialect='excel')
    #     spamwriter.writerow(['测试'] * 5 + ['Baked Beans'])
    #     spamwriter.writerow(['Spam', 'Lovely Spam', 'Wonderful Spam'])


    # 读取csv至字典
    csvFile = open(csv_file, "w")
    csvFile.write(codecs.BOM_UTF8)

    writer = csv.writer(csvFile)
    # 文件头，一般就是数据名
    fileHeader = ['keywords']


    writer.writerow(fileHeader)
    with open(corpus_file, 'r') as fid:
        for item in fid:
            writer.writerow(item.strip('\n'))

    csvFile.close()
    print 'dump %s file to csv file %s' % (corpus_file, csv_file)


def filtering_line(line_content, stopwords_list):
    '''
    this function spams the noisy symbols, then cut the line to words and remove the stopwords in each line
    :param line_content:
    :return:
    '''
    multi_version = re.compile(ur'-\{.*?(zh-hans|zh-cn):([^;]*?)(;.*?)?\}-')
    # punctuation = re.compile(u"[-~!@#$%^&*()_+`=\[\]\\\{\}\\t\\r\"|;':,./<>?·！@#￥%……&*（）——+【】、；‘：“”，。、《》？「『」』]")
    punctuation = re.compile(u"[\[\]\\\{\}\\t\\r\"|;',<>?·！@#￥%……&*（）——+【】、；‘：“”，。、《》？「『」』]")

    line_content = multi_version.sub(ur'\2', line_content)
    line_content = punctuation.sub('', line_content.decode('utf8'))

    # cut the line content to words
    line_content_cut = [w for w in jieba.cut(line_content)]

    if stopwords_list is not None:
        new_line = []
        for word in line_content_cut:
            if word not in stopwords_list:
                new_line.append(word)
        return new_line
    else:
        return line_content_cut

if __name__ == '__main__':
    # first dump the corpus to a csv file, with each line is a query
    qa_corpus_dir = '/media/xuxing/windisk/workspace-xing/qa-system/qa_dataset'
    working_dir = os.getcwd()

    ### 根据规则生成 问题的分类
    '''
    qa_gaokao_file = 'qa_gaokao.txt'

    qa_gaokao_csv_file = qa_gaokao_file.replace('.txt', '.csv')

    # dump_corpus_csv(os.path.join(qa_corpus_dir, qa_gaokao_file), os.path.join(working_dir, qa_gaokao_csv_file))

    qa_gaokao_csv_file = 'qa_gaokao_csv.txt'

    numDict = len(dict_list)
    idx = 0
    # loop for each
    with open(os.path.join(working_dir, qa_gaokao_csv_file), 'w') as fid_out:
        with open(os.path.join(qa_corpus_dir, qa_gaokao_file), 'r') as fid_in:
            for item in fid_in:
                line_content = item.strip('\n')
                line_labels = set([])
                # # now cut the line_content without stop word list
                # line_content_cut = filtering_line(line_content, None)


                for index in range(numDict - 1):
                    cate = dict_list[index]
                    cate_label = cate['id']
                    cate_keywords = cate['keywords']
                    cate_condition = cate['condition']

                    for word in cate_condition:
                        if word in line_content:
                            line_labels.add(cate_label)
                            break

                    for word in cate_keywords:
                        if word in line_content:
                            line_labels.add(cate_label)
                            break

                # if loop over, no label assigned, then assigned the 'other' label
                if len(line_labels) == 0:
                    line_labels.add(dict_list[numDict-1]['id'])

                labels_string = ' '.join(list(line_labels))

                new_content = '%s %s\n' % (line_content, labels_string)

                fid_out.write(new_content)

                idx = idx + 1

                if idx % 1000 == 0:
                    print 'classifying %d th query done!' % idx

    '''


    ### 对分类好的100 - 500 类的问题，抽取问题中的关键元素，比如名词，问句词等
    category_file = '100.txt'
    category_poseg_file = category_file.replace('.txt', '_poseg.txt')
    vaild_poseg = ['n', 'ns', 'nt', 'nz', 'a', 'd', 'r', 'm', 'v']


    # use jieba to cut the sentence in each line with stopwords
    stopwords_file = 'stopwords_gaokao.txt'
    stopwords_dir = '/media/xuxing/windisk/workspace-xing/qa-system/stopwords_cn'
    stopwords_list = load_stopwords_file(stopwords_dir, stopwords_file)

    idx = 0
    with open(os.path.join(qa_corpus_dir, category_file), 'r') as fid:
        with open(os.path.join(qa_corpus_dir, category_poseg_file), 'w') as fid_out:
            for item in fid:
                question = item.strip('\n')

                # cut the question without stopwords
                res = filtering_line(question, stopwords_list)
                question_cut = ''.join(res)

                # poseg for question
                seg = jieba.posseg.cut(question_cut)

                l = []
                for i in seg:
                    if i.flag in vaild_poseg:
                        l.append('%s/%s' % (i.word, i.flag))

                new_line_content = ' '.join(l)
                fid_out.write('%s\n' % new_line_content)

                idx = idx + 1
                if idx % 1000 == 0:
                    print '%d question done!' % idx

    print 'finished!'









