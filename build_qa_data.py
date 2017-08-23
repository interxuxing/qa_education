# -*- coding:utf-8 -*-

"""
This script is used to build a qa data for usage.
Typically, each enty contains three elements: a question, an answer, a url
"""

import sys
import re
import os
import jieba

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
    :param stopwords_list:
    :return:
    '''
    multi_version = re.compile(ur'-\{.*?(zh-hans|zh-cn):([^;]*?)(;.*?)?\}-')
    # punctuation = re.compile(u"[-~!@#$%^&*()_+`=\[\]\\\{\}\\t\\r\"|;':,./<>?·！@#￥%……&*（）——+【】、；‘：“”，。、《》？「『」』]")
    punctuation = re.compile(u"[\[\]\\\{\}\\t\\r\"|;',<>?·！@#￥%……&*（）——+【】、；‘：“”，。、《》？「『」』]")

    line_content = multi_version.sub(ur'\2', line_content)
    line_content = punctuation.sub('', line_content.decode('utf8'))
    line_content = line_content.replace('_&_', '')

    # cut the line content to words
    # line_content_cut = jieba.cut(line_content)
    #
    # new_line = []
    # for word in line_content_cut:
    #     if word not in stopwords_list:
    #         new_line.append(word)
    #
    # clean_line = ' '.join(new_line)

    return line_content

def build_dataset(dir_source, stopwords_list):
    '''
    build dataset from the source directory
    :param dir_source:
    :return: a pickle file of dataset, a list with each one is a tuple (question, answer, url)
    '''
    subdirs = os.listdir(dir_source)
    list_qa_dataset = []
    question_idx = 0

    for subdir_file in subdirs:
        # parse content in file
        subfiles = os.listdir(os.path.join(dir_source, subdir_file))
        for subsubfile in subfiles:
            res_list, question_idx = remove_noise_symbol_in_line2(os.path.join(dir_source, subdir_file, subsubfile), question_idx, stopwords_list)
            list_qa_dataset += res_list
    return list_qa_dataset

def load_stopwords_cn(stopwords_file):

    list_stopwords = []
    with open(stopwords_file, 'r') as ins:
        for item in ins:
            list_stopwords.append(item.strip('\n'))

    return list_stopwords

def remove_noise_symbol_in_line(input_filename, content_list, line_count):
    '''
    remove noise symbol in a line
    this function is deprecated, since the input_file is not stardard four lines per question-answer
    :param input_filename: a string
    :return: a string
    '''
    line_idx = 0
    question_idx = line_count
    print 'dumping file %s ' % input_filename

    question = ''
    subquestion = ''
    url = ''
    with open(input_filename, 'r') as ins:
        for line in ins:
            line_idx = line_idx + 1
            # if line.strip() == '':
            #     print 'no content found in line'
            #     continue

            if line_idx % 4 == 1:
                line = filtering_line(line)
                url = line.strip('\n')
                if 'http' not in url:
                    print '%d-line error!'
            elif line_idx % 4 == 2:
                line = filtering_line(line)
                question = line.strip('\n')
            elif line_idx % 4 == 3:
                line = filtering_line(line)
                subquestion = line.strip('\n')
            elif line_idx % 4 == 0:
                line = filtering_line(line)
                answer = line.strip('\n')

                # now add a tuble to the list
                qa_tuble = (question, answer, url)
                content_list.append(qa_tuble)
                question_idx = question_idx + 1
                print 'get %d-th question %s' % (question_idx, question)
                # if subquestion != '':
                #     subqa_tuble = (subquestion, answer, url)
                #     content_list.append(subqa_tuble)
                #     question_idx = question_idx + 1
                #     print 'get %d-th question-subquestion %s' % (question_idx, url)

    return content_list, question_idx


def remove_noise_symbol_in_line2(input_filename, line_count, stopwords_list):
    '''
    remove noise symbol in a line, another approach
    read each url line as an anchor
    :param input_filename: a string
    :return: a string
    '''
    line_idx = 0
    question_idx = line_count
    print 'dumping file %s ' % input_filename

    question = ''
    subquestion = ''
    url = ''
    content_list = []
    with open(input_filename, 'r') as ins:
        qa_content = []
        for line in ins:
            line_idx = line_idx + 1

            # add each line
            qa_content.append(line.strip('\n').strip('\t'))
            # check line starts with http (a url)
            if 'http' == line[0:4] and line_idx != 1:
                # start a new qa pair, first get the content then clean the list
                url = qa_content[0].strip('\n').strip('\t')

                question = qa_content[1].strip('\n').strip('\t')
                question = filtering_line(question, stopwords_list)

                answer = qa_content[-2].strip('\n').strip('\t')
                answer = filtering_line(answer, stopwords_list)

                # add (question, answer, url) to the list
                # now add a tuble to the list
                qa_tuble = (question, answer, url)
                content_list.append(qa_tuble)
                question_idx = question_idx + 1
                print 'get %d-th question %s' % (question_idx, question)

                # reset qa_content as the new url
                qa_content = [qa_content[0]]

        # last qa_pair
        url = qa_content[0].strip('\n').strip('\t')

        question = qa_content[1].strip('\n').strip('\t')
        question = filtering_line(question, stopwords_list)

        answer = qa_content[-1].strip('\n').strip('\t')
        answer = filtering_line(answer, stopwords_list)

        # add (url, question, answer) to the list
        # now add a tuble to the list
        qa_tuble = (question, answer, url)
        content_list.append(qa_tuble)
        question_idx = question_idx + 1
        print 'get last %d-th question %s' % (question_idx, question)

    return content_list, question_idx


if __name__ == '__main__':

    # generate the qa_dataset.pickle
    # load the stopwords list
    # load stopwords list
    stopwords_list = []
    with open('./stopwords_cn/jieba_stopwords_cn.txt') as sw:
        for line in sw:
            stopwords_list.append(line.strip('\n'))

    # initial qa dataset directory
    dir_qa_dataset = '/media/xuxing/windisk/workspace-xing/qa-system/qa_dataset'

    list_qa_dataset = build_dataset(dir_qa_dataset, stopwords_list)
    qa_pickle_file = 'qa_dataset.pickle'

    # save in pickle
    if not os.path.exists(os.path.join(dir_qa_dataset, qa_pickle_file)):
        print '%s not exist, creating it!' % qa_pickle_file
        fid_qa = open(os.path.join(dir_qa_dataset, qa_pickle_file), 'w')
        pickle.dump(list_qa_dataset, fid_qa)
        fid_qa.close()
        print 'save %s finished' % qa_pickle_file
    else:
        fid_qa = open(os.path.join(dir_qa_dataset, qa_pickle_file), 'w')
        list_qa_dataset = pickle.load(fid_qa)
        fid_qa.close()
        print 'load existing %s' % qa_pickle_file

    # convert the qa_dataset.pickle to qa_education.txt that was used by s2s model
    # load the question answer dataset, pickle
    qa_conv_file = 'qa_education.txt'
    numQestions = len(list_qa_dataset)
    with open(qa_conv_file, 'w') as ins:
        for idx in range(numQestions):
            item = list_qa_dataset[idx]
            # item format (url, question, answer)
            question = item[0]
            answer = item[1]
            try:
                ins.write('%s\n' % question)
                # ins.write('%s\n' % answer)
                # ins.write('\n')
            except:
                print 'error'

            if idx % 1000 == 0:
                print 'write %d-%d question-answer pair finished!' % (idx, numQestions)
    print 'save %s finished!' % qa_conv_file



