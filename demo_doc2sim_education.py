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


def load_qa_education(data_dir, education_file):
    '''
        load the eudcation file, return a list, with each element is a string in each line
    '''
    education_content = []
    idx = 0
    with open(os.path.join(data_dir, education_file)) as fid:
        for item in fid:
            education_content.append(item.strip('\n'))
            idx = idx + 1
            # if idx % 1000 == 0:
            #     print 'loading %d-th questions done!' % idx

    return education_content

def load_qa_education_with_answer(data_dir, education_file):
    '''
        load the eudcation file, return a list, with each element is a string in each line
    '''
    education_content = []
    answer_content = []
    idx = 0
    with open(os.path.join(data_dir, education_file)) as fid:
        for item in fid:
            if idx % 2 == 0: # questions
                education_content.append(item.strip('\n'))
            elif idx % 2 == 1: # answer
                answer_content.append(item.strip('\n'))

            idx = idx + 1
            # if idx % 1000 == 0:
            #     print 'loading %d-th questions done!' % idx
    print 'loading %d questions done!' % int(idx/2)
    return education_content, answer_content

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

def calculate_education_data(data_dir, education_content, stopwords_list):
    '''
    this file is to calculate the dictionary, similarity matrix given a data.txt file
    :param data_dir: the root dir that save the returned data
    :param eudcation_content: a list that each element is a eudcation question
    :param stopwords_list: stopwords list for eudcation corpus
    :return: a dictionary, a simialrity matrix
    '''

    corpora_documents_name = 'qa_education_corpora.pickle'
    if not os.path.exists(os.path.join(data_dir, corpora_documents_name)):
        corpora_documents = []
        idx = 0
        for item_text in education_content:
            item_str = filtering_line(item_text, stopwords_list)
            corpora_documents.append(item_str)
            idx = idx + 1
            if idx % 1000 == 0:
                print 'jieba cutting for %d-th sentence' % idx
        # dump pickfile
        fid_corpora = open(os.path.join(data_dir, corpora_documents_name), 'wb')
        pickle.dump(corpora_documents, fid_corpora)
        fid_corpora.close()
        print 'save %s finished' % corpora_documents_name
    else:
        # load pickfile
        fid_corpora = open(os.path.join(data_dir, corpora_documents_name), 'rb')
        corpora_documents = pickle.load(fid_corpora)
        fid_corpora.close()
        print 'load %s finished' % corpora_documents_name

    dict_name = 'dict_education'
    # 生成字典和向量语料
    if not os.path.exists(os.path.join(data_dir, dict_name)):
        print 'calculating dictionary education !'
        dictionary = gensim.corpora.Dictionary(corpora_documents)
        dictionary.save(os.path.join(data_dir, dict_name))
    else:
        print 'dictionary for education already exists, load it!'
        dictionary = gensim.corpora.Dictionary.load(os.path.join(data_dir, dict_name))

    corpus = [dictionary.doc2bow(text) for text in corpora_documents]
    numSen = len(corpus)

    # calculate the similarity for pairwise training samples
    num_features = len(dictionary.keys())
    print '%d words in dictionary' % num_features
    # # save object
    sim_name = 'sim_education'
    if not os.path.exists(os.path.join(data_dir, sim_name)):
        print 'calculating sim_education !'
        similarity = gensim.similarities.Similarity(os.path.join(data_dir, sim_name), corpus, num_features)
        similarity.save(os.path.join(data_dir, sim_name))
    else:
        print 'sim_eudcation already exists, load it!'
        similarity = gensim.similarities.Similarity.load(os.path.join(data_dir, sim_name))

    return dictionary, similarity


def calculate_education_data_w2v(data_dir, education_content, w2v_model, stopwords_list):
    '''
    this file is to calculate the dictionary, similarity matrix given a data.txt file
    :param data_dir: the root dir that save the returned data
    :param eudcation_content: a list that each element is a eudcation question
    :param stopwords_list: stopwords list for eudcation corpus
    :return: a dictionary, a simialrity matrix
    '''
    corpora_documents = []
    idx = 0
    for item_text in education_content:
        item_str = filtering_line(item_text, stopwords_list)
        corpora_documents.append(item_str)
        idx = idx + 1
        if idx % 1000 == 10:
            print 'jieba cutting for %d-th sentence' % idx

    # corpus = [text for text in corpora_documents]
    corpus = corpora_documents
    numSen = len(corpus)


    # calculate the similarity for pairwise training samples
    # # save object
    sim_name = 'sim_education_w2v'
    if not os.path.exists(os.path.join(data_dir, sim_name)):
        print 'calculating sim_education !'
        similarity = gensim.similarities.WmdSimilarity(corpus, w2v_model, num_best=3)
        similarity.save(os.path.join(data_dir, sim_name))
    else:
        print 'sim_eudcation already exists, load it!'
        similarity = gensim.similarities.WmdSimilarity.load(os.path.join(data_dir, sim_name))

    return similarity


'''
测试的问题：

北京小升初的政策？
成都比较好的小学推荐
小孩子谈恋爱怎么办？
怎么提高小孩子英语学习？
北京好的幼儿园推荐
中考前饮食应该注意什么？
我家小孩上课注意力不集中，贪玩，怎么办？
小孩子在学校打架，怎么办？
成都龙江路小学划片么？
小孩子厌学怎么办？
孩子上课注意力不集中，贪玩怎么办？
武汉比较好的中学有哪些？
幼儿园学前教育有必要吗？
'''


if __name__ == '__main__':
    # load the eudcation data
    data_dir = './qa_dataset'
    qa_education_file = 'qa_education.txt'

    # education_content = load_qa_education(data_dir, qa_education_file)
    education_content, answer_content = load_qa_education_with_answer(data_dir, qa_education_file)

    # use jieba to cut the sentence in each line with stopwords
    stopwords_file = 'stopwords_gaokao.txt'
    stopwords_dir = './stopwords_cn'
    stopwords_list = load_stopwords_file(stopwords_dir, stopwords_file)


    # caluclate the dictionary and the similarity of the given corpus
    dictionary, similarity = calculate_education_data(data_dir, education_content, stopwords_list)
    print 'obtained the dictionary and similarity of the %s corpus!' % qa_education_file

    similarity.num_best = 3
    while(True):
        print '欢迎来到小题博士-教育问答 @_@'
        print '你可以咨询与中小学教育相关的问题，比如:'
        print '  北京好的幼儿园推荐? \n 中考前饮食应该注意什么？\n 我家小孩上课注意力不集中，贪玩，怎么办？ \n 小孩子在学校打架，怎么办？'
        print '################################'
        print ''
        input_query = raw_input(u'请输入你要问的问题：')
        input_query_cut = filtering_line(input_query, stopwords_list)
        # parse the input query, get its doc vector
        doc_input_query = dictionary.doc2bow(input_query_cut)
        res = similarity[doc_input_query]
        print '这是你要问的问题吗？'
        for idx, content in res:
            print '%d, %s' % (idx, education_content[idx])
            print '%s' % answer_content[idx]

        print '################################'
        print '请问下一个问题 @_@'


    '''
    # caluclate the dictionary and the similarity using walking-earth similarity measure of the given corpus
    # load wiki model
    wiki_model_file = './tempfile/out_w2v_qa_incremental.model'
    wiki_model = gensim.models.Word2Vec.load(wiki_model_file)

    similarity = calculate_education_data_w2v(data_dir, education_content, wiki_model, stopwords_list)
    print 'obtained the dictionary and similarity of the %s corpus!' % qa_education_file

    num_best = 3
    while (True):
        print '欢迎来到小题博士-教育问答 @_@'
        input_query = raw_input(u'请输入你要问的问题：')
        input_query_cut = filtering_line(input_query, stopwords_list)
        res = similarity[input_query_cut]
        print '这是你要问的问题吗？'
        for idx, content in res:
            print '%d, %s' % (idx, education_content[idx])

        print '################################'
        print '请问下一个问题 @_@'
    '''

