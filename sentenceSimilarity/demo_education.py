# -*- coding:utf-8 -*-

from zhcnSegment import *
from fileObject import FileObj
from sentenceSimilarity import SentenceSimilarity
from sentence import Sentence
import sys
import os

reload(sys)
sys.setdefaultencoding('utf-8')

try:
    import cPickle as pickle
except:
    import pickle

'''
This script is a domo code that used sentence2sentence similarity for question retrieval
'''

if __name__ == '__main__':
    # load question database
    database_dir = '/media/xuxing/windisk/workspace-xing/qa-system'
    qa_pickle_file = 'qa_dataset.pickle'

    fid_qa = open(os.path.join(database_dir, qa_pickle_file), 'r')
    list_qa_dataset = pickle.load(fid_qa)
    fid_qa.close()
    print 'load %s finished' % qa_pickle_file

    # get questions in the list of tuple, (question, answer, url) in the list
    question_list = [x[0] for x in list_qa_dataset]
    answer_list = [x[1] for x in list_qa_dataset]

    numQuestions_train = len(question_list) - 100
    numQuestions_test = 100

    question_list_train = question_list[:numQuestions_train]
    question_list_test = question_list[numQuestions_train:]

    answer_list_train = answer_list[:numQuestions_train]
    answer_list_test = answer_list[numQuestions_train:]

    # 分词工具，基于jieba分词，我自己加了一次封装，主要是去除停用词
    seg = Seg()

    # 训练模型
    ss = SentenceSimilarity(seg)
    ss.set_sentences(question_list_train)
    # ss.TfidfModel()         # tfidf模型
    ss.LsiModel()         # lsi模型
    # ss.LdaModel()         # lda模型

    # 测试集1
    right_count = 0
    for i in range(0,len(question_list_test)):
        sentenceK = ss.similarityK(question_list_test[i])
        print ' '
        print 'question: %s' % question_list_test[i]
        for k in range(len(sentenceK)):
            sentence_k = sentenceK[k]
            org_sentence = sentence_k.origin_sentence
            sentence_id = sentence_k.id
            answer_k = answer_list_train[sentence_id]

            print 'top %d: question: %s, answer %s' % (k, org_sentence, answer_k)

    print 'finished'

    # 测试集2
    # right_count = 0
    # for i in range(0,len(train_sentences)):
    #     sentence = ss.similarity(test2_sentences[i])
    #
    #     if i != sentence.id:
    #         print str(i) + " wrong! score: " + str(sentence.score)
    #     else:
    #         right_count += 1
    #         print str(i) + " right! score: " + str(sentence.score)
    #
    # print "正确率为: " + str(float(right_count)/len(train_sentences))