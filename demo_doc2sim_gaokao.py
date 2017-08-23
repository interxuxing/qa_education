# -*- coding:utf-8 -*-

"""
This script is used to build a qa data for usage.
Typically, each enty contains three elements: a question, an answer, a url
"""

import sys
import re
import os
import jieba
import gensim

try:
    import cPickle as pickle
except:
    import pickle

reload(sys)
sys.setdefaultencoding('utf-8')

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


def load_qa_gaokao(data_dir, gaokao_file):
    '''
        load the gaokao file, return a list, with each element is a string in each line
    '''
    gaokao_content = []
    idx = 0
    with open(os.path.join(data_dir, gaokao_file)) as fid:
        for item in fid:
            gaokao_content.append(item.strip('\n'))
            idx = idx + 1
            # if idx % 1000 == 0:
            #     print 'loading %d-th questions done!' % idx

    return gaokao_content

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

def calculate_gaokao_data(data_dir, gaokao_content, stopwords_list):
    '''
    this file is to calculate the dictionary, similarity matrix given a data.txt file
    :param data_dir: the root dir that save the returned data
    :param gaokao_content: a list that each element is a gaokao question
    :param stopwords_list: stopwords list for gaokao corpus
    :return: a dictionary, a simialrity matrix
    '''
    corpora_documents = []
    idx = 0
    for item_text in gaokao_content:
        item_str = filtering_line(item_text, stopwords_list)
        corpora_documents.append(item_str)
        idx = idx + 1
        if idx % 1000 == 0:
            print 'jieba cutting for %d-th sentence' % idx

    # 生成字典和向量语料
    if not os.path.exists(os.path.join(data_dir, 'dict_gaokao')):
        print 'calculating dictionary gaokao !'
        dictionary = gensim.corpora.Dictionary(corpora_documents)
        dictionary.save(os.path.join(data_dir, 'dict_gaokao'))
    else:
        print 'dictionary for gaokao already exists, load it!'
        dictionary = gensim.corpora.Dictionary.load(os.path.join(data_dir, 'dict_gaokao'))

    corpus = [dictionary.doc2bow(text) for text in corpora_documents]
    numSen = len(corpus)

    # calculate the similarity for pairwise training samples
    num_features = len(dictionary.keys())
    print '%d words in dictionary' % num_features
    # # save object
    if not os.path.exists(os.path.join(data_dir, 'sim_gaokao')):
        print 'calculating sim_gaokao !'
        similarity = gensim.similarities.Similarity(os.path.join(data_dir, 'sim_gaokao'), corpus, num_features)
        similarity.save(os.path.join(data_dir, 'sim_gaokao'))
    else:
        print 'sim_gaokao already exists, load it!'
        similarity = gensim.similarities.Similarity.load(os.path.join(data_dir, 'sim_gaokao'))

    return dictionary, similarity



if __name__ == '__main__':
    # load the gaokao data
    data_dir = '/media/xuxing/windisk/workspace-xing/qa-system/qa_dataset'
    qa_gaokao_file = 'qa_gaokao.txt'

    gaokao_content = load_qa_gaokao(data_dir, qa_gaokao_file)

    # use jieba to cut the sentence in each line with stopwords
    stopwords_file = 'stopwords_gaokao.txt'
    stopwords_dir = '/media/xuxing/windisk/workspace-xing/qa-system/stopwords_cn'
    stopwords_list = load_stopwords_file(stopwords_dir, stopwords_file)

    # caluclate the dictionary and the similarity of the given corpus
    dictionary, similarity = calculate_gaokao_data(data_dir, gaokao_content, stopwords_list)
    print 'obtained the dictionary and similarity of the %s corpus!' % qa_gaokao_file

    similarity.num_best = 3
    while(True):
        print '欢迎来到小题博士-高考问答 @_@'
        input_query = raw_input(u'请输入你要问的问题：')
        input_query_cut = filtering_line(input_query, stopwords_list)
        # parse the input query, get its doc vector
        doc_input_query = dictionary.doc2bow(input_query_cut)
        res = similarity[doc_input_query]
        print '这是你要问的问题吗？'
        for idx, content in res:
            print '%d, %s' % (idx, gaokao_content[idx])

        print '################################'
        print '请问下一个问题 @_@'
