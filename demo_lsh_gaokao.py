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
import sklearn.feature_extraction
import sklearn.neighbors

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

    # 使用lsh来处理
    tfidf_vectorizer = sklearn.feature_extraction.text.TfidfVectorizer(min_df=3, max_features=None, \
                                                                       ngram_range=(1, 2), use_idf=1, smooth_idf=1, sublinear_tf=1)
    corpora_documents_tmp = []
    idx = 0
    for item_text in gaokao_content:
        item_str = filtering_line(item_text, stopwords_list)
        corpora_documents_tmp.append(item_str)
        idx = idx + 1
        if idx % 1000 == 0:
            print 'jieba cutting for %d-th sentence' % idx
    print 'total %d questions loaded!' % idx
    # extract each list in corpora_documents_tmp to one list
    corpora_documents = [inner_item for out_iterm in corpora_documents_tmp for inner_item in out_iterm]
    # save corpus_vectors, lshf to pickle
    pickle_gaokao = 'lsh_gaokao.pickle'
    if not os.path.exists(os.path.join(data_dir, pickle_gaokao)):
        print 'calculating pickle lsh gaokao !'
        corpus_vectors = tfidf_vectorizer.fit_transform(corpora_documents)

        lshf = sklearn.neighbors.LSHForest(random_state=42)
        lshf.fit(corpus_vectors.toarray())

        with open(os.path.join(data_dir, pickle_gaokao), 'w') as fid:
            pickle.dump((tfidf_vectorizer, corpus_vectors, lshf), fid)
        print 'dump to file %s ' % pickle_gaokao
    else:
        print 'pickle file for lsh gaokao already exists, load it!'
        with open(os.path.join(data_dir, pickle_gaokao), 'r') as fid:
            tfidf_vectorizer, corpus_vectors, lshf = pickle.load(fid)


    return tfidf_vectorizer, corpus_vectors, lshf



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
    tfidf_vectorizer, corpus_vectors, lshf = calculate_gaokao_data(data_dir, gaokao_content, stopwords_list)
    print 'obtained the dictionary and similarity of the %s corpus!' % qa_gaokao_file

    # while(True):
    #     print '欢迎来到小题博士-高考问答 @_@'
    #     input_query = raw_input(u'请输入你要问的问题：')
    #     input_query_cut = filtering_line(input_query, stopwords_list)
    #     # parse the input query, get its doc vector
    #     x_test = tfidf_vectorizer.transform(input_query_cut)
    #     distances, indices = lshf.kneighbors(x_test.toarray(), n_neighbors=3)
    #     print '这是你要问的问题吗？'
    #     for idx in indices[0]:
    #         print idx
    #         print '%d, %s' % (idx, gaokao_content[idx])
    #
    #     print '################################'
    #     print '请问下一个问题 @_@'


    print '欢迎来到小题博士-高考问答 @_@'
    input_query = u'高考前应该吃什么比较好？'
    input_query_cut = filtering_line(input_query, stopwords_list)
    # parse the input query, get its doc vector
    x_test = tfidf_vectorizer.transform(input_query_cut)
    distances, indices = lshf.kneighbors(x_test.toarray(), n_neighbors=3)
    print '这是你要问的问题吗？'
    for idx in indices[0]:
        print idx
        print '%d, %s' % (idx, gaokao_content[idx])

    print '################################'
    print '请问下一个问题 @_@'
