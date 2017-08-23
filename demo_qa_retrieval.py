# -*- coding:utf-8 -*-

"""
This script is a demo that retrieve candidate question given an input query
"""
import os, sys
import multiprocessing
import gensim
import io
import jieba
import numpy as np
import pyemd
import re
import scipy.spatial.distance

reload(sys)
sys.setdefaultencoding('utf-8')

try:
    import cPickle as pickle
except:
    import pickle


def filtering_content(line_content):
    multi_version = re.compile(u'-\{.*?(zh-hans|zh-cn):([^;]*?)(;.*?)?\}-')
    punctuation = re.compile(u"[-~!@#$%^&*()_+`=\[\]\\\{\}\\t\\r\"|;':,./<>?·！@#￥%……&*（）——+【】、；‘：“”，。、《》？「『」』]")
    # punctuation = re.compile(ur"[0-9]\[\]\\\{\}\\t\\r\"|;',<>?·！@#￥%……&*（）——+【】、，；‘：“”，。、《》？「『」』]")

    line_content = multi_version.sub(ur'\2', line_content)
    line_content = punctuation.sub('', line_content.decode('utf8'))
    line_content = line_content.replace('_&_', '')

    return line_content

def caluclate_avg_word_vector_database(question_list, model, dim_features=300):
    dimW2V = 300
    mat_w2v_question = np.zeros([1, dimW2V])
    count_ques = 0
    for question in question_list:
        question_filtered = filtering_content(question)
        question_words = [w for w in jieba.cut(question_filtered.strip('\n'))]
        w2v_question = doc_avg_word_vector(question_words, model, dim_features)

        count_ques = count_ques + 1
        if count_ques == 1:
            mat_w2v_question = w2v_question[np.newaxis, :]
        else:
            mat_w2v_question = np.vstack((mat_w2v_question, w2v_question[np.newaxis, :]))

        if count_ques % 1000 == 0:
            print 'calculating %d / %d questions finished!' % (count_ques, numQuestions)

    return mat_w2v_question

def doc_avg_word_vector(doc_words, model, dim_features=300):
    # function to average all words vectors in a given paragraph
    featureVec = np.zeros((dim_features, ), dtype="float32")
    nwords = 0
    # list containing names of words in the vocabulary
    # index2word_set = set(model.index2word) this is moved as input param for performance reasons
    for word in doc_words:
        try:
            nwords = nwords + 1
            featureVec = np.add(featureVec, model[word])
        except:
            continue

    if (nwords > 0):
        featureVec = np.divide(featureVec, nwords)
    return featureVec


if __name__ == '__main__':
    # load the question answer dataset, pickle
    qa_pickle_file = 'qa_dataset.pickle'
    fid_qa = open(qa_pickle_file, 'r')
    list_qa_dataset = pickle.load(fid_qa)
    fid_qa.close()
    print 'load %s finished' % qa_pickle_file

    # load the pretrained word2vec model
    tempdir = 'tempfile'
    model = gensim.models.Word2Vec.load(os.path.join(os.getcwd(), tempdir, 'out_w2v_qa'))

    # get questions in the list of tuple, (question, answer, url) in the list
    question_list = [x[0] for x in list_qa_dataset]
    # numQuestions = len(question_list)
    # question_list = question_list[:10000]
    # calculate the average word vector for each question
    numQuestions = len(question_list)
    answer_list = [x[1] for x in list_qa_dataset]
    # given a input query, get the candidate query and its answer
    input_query = u'北京的小升初政策'
    input_query_cut = [w for w in jieba.cut(filtering_content(input_query.strip('\n')))]

    # calculate the word2vec for the query
    mat_w2v_query = doc_avg_word_vector(input_query_cut, model, 300)
    mat_w2v_query = mat_w2v_query[np.newaxis, :]

    # calculate the word2vec for the question database
    questions_w2v_database = 'questions_w2v_db.npz'
    if not os.path.exists(questions_w2v_database):
        mat_w2v_question = caluclate_avg_word_vector_database(question_list, model)
        np.savez(questions_w2v_database, mat_questions_db = mat_w2v_question)
    else:
        npzfile = np.load(questions_w2v_database)
        mat_w2v_question = npzfile['mat_questions_db']

    # calulate cosine similarity between the vector and the question in database
    scores = np.ones((numQuestions, )) * 1e5
    for i in range(mat_w2v_question.shape[0]):
        # calulate the cosine similary
        w2v_question_i = mat_w2v_question[i, :]
        scores[i] = 1 - scipy.spatial.distance.cosine(mat_w2v_query, w2v_question_i)

        if i % 1000 == 0:
            print 'calulating cosine similarity for %d - %d ' % (i, numQuestions)

    ''' 
    # calculate the similarity of input query with the database
    scores = np.zeros([numQuestions, 1])
    
    for idx in range(numQuestions):
        item = question_list[idx]
        item_filtered = filtering_content(item.strip('\n'))
        item_cut = [w for w in jieba.cut(item_filtered)]
        # calulate the distance
        dist_score = model.wmdistance(input_query_cut, item_cut)
        if dist_score == float('inf'):
            dist_score = 1e5
        scores[idx] = dist_score

        if idx % 100 == 0:
            print 'parsing %d-th questions in database over' % idx

    '''

    # sort to get the top-5 answers
    # idx_sort = np.argsort(np.squeeze(scores, axis=1))
    idx_sort = np.argsort(scores)
    print 'query: %s' % input_query
    for k in range(5):
        idx_k = idx_sort[k]
        print 'question-%d: %s' % (idx_k, question_list[idx_k])
        print 'answer-%d: %s' % (idx_k, answer_list[idx_k])





