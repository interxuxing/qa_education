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

def filtering_line(line_content):
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
    #
    # new_line = []
    # for word in line_content_cut:
    #     if word not in stopwords_list:
    #         new_line.append(word)
    #
    # clean_line = ' '.join(new_line)

    return line_content_cut

# 训练样本
raw_documents = [
    u'0无偿居间介绍买卖毒品的行为应如何定性',
    u'1吸毒男动态持有大量毒品的行为该如何认定',
    u'2如何区分是非法种植毒品原植物罪还是非法制造毒品罪',
    u'3为毒贩贩卖毒品提供帮助构成贩卖毒品罪',
    u'4将自己吸食的毒品原价转让给朋友吸食的行为该如何认定',
    u'5为获报酬帮人购买毒品的行为该如何认定',
    u'6毒贩出狱后再次够买毒品途中被抓的行为认定',
    u'7虚夸毒品功效劝人吸食毒品的行为该如何认定',
    u'8妻子下落不明丈夫又与他人登记结婚是否为无效婚姻',
    u'9一方未签字办理的结婚登记是否有效',
    u'10夫妻双方1990年按农村习俗举办婚礼没有结婚证 一方可否起诉离婚',
    u'11结婚前对方父母出资购买的住房写我们二人的名字有效吗',
    u'12身份证被别人冒用无法登记结婚怎么办？',
    u'13同居后又与他人登记结婚是否构成重婚罪',
    u'14未办登记只举办结婚仪式可起诉离婚吗',
    u'15同居多年未办理结婚登记，是否可以向法院起诉要求离婚'
]
corpora_documents = []
for item_text in raw_documents:
    item_str = filtering_line(item_text)
    corpora_documents.append(item_str)

# 生成字典和向量语料
dictionary = gensim.corpora.Dictionary(corpora_documents)
corpus = [dictionary.doc2bow(text) for text in corpora_documents]

similarity = gensim.similarities.Similarity('./temp_doc', corpus, num_features=400)

test_data_1 = u'你好，我想问一下我想离婚他不想离，孩子他说不要，是六个月就自动生效离婚'
test_cut_raw_1 = filtering_line(test_data_1)
test_corpus_1 = dictionary.doc2bow(test_cut_raw_1)
similarity.num_best = 5
res = similarity[test_corpus_1]

print test_data_1
for idx, content in res:
    print '%d, %s' % (idx, raw_documents[idx])

# print()  # 返回最相似的样本材料,(index_of_document, similarity) tuples

print('################################')

test_data_2 = u'家人因涉嫌运输毒品被抓，她只是去朋友家探望朋友的，结果就被抓了，还在朋友家收出毒品，可家人的身上和行李中都没有。现在已经拘留10多天了，请问会被判刑吗'
test_cut_raw_2 = filtering_line(test_data_2)
test_corpus_2 = dictionary.doc2bow(test_cut_raw_2)
similarity.num_best = 5

res = similarity[test_corpus_2]

print test_data_2
for idx, content in res:
    print '%d, %s' % (idx, raw_documents[idx])
# print(similarity[test_corpus_2])  # 返回最相似的样本材料,(index_of_document, similarity) tuples