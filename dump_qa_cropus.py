# -*- coding:utf-8 -*-

"""
This script is used to dump the information crawled from web,
to generate the corpus used for education.
"""

import sys
import re
import os
import jieba

reload(sys)
sys.setdefaultencoding('utf-8')

# DIR_XIAOSHENGCHU = 'E:\\Project\\QA-system\\qa_dataset\\xiaoshengchu'
DIR_XIAOSHENGCHU = './qa_dataset/xiaoshengchu'
DIR_JIAZHANGJIAOYU = './qa_dataset/jiazhangjiaoyu'

def remove_noise_symbol_in_line(input_filename, fid_outfile):
    '''
    remove noise symbol in a line
    :param input_line: a string
    :return: a string
    '''
    multi_version = re.compile(ur'-\{.*?(zh-hans|zh-cn):([^;]*?)(;.*?)?\}-')
    punctuation = re.compile(u"[-~!@#$%^&*()_+`=\[\]\\\{\}\"|;':,./<>?·！@#￥%……&*（）——+【】、；‘：“”，。、《》？「『」』]")

    line_idx = 0
    print 'dumping file %s ' % input_filename
    with open(input_filename, 'r') as ins:
        for line in ins:
            line_idx = line_idx + 1
            if line.strip() == '':
                continue
            # remove noise
            if line_idx % 4 != 1:
                line = multi_version.sub(ur'\2', line)
                line = punctuation.sub('', line.decode('utf8'))
                line = line.replace('_&_', '')
                if line.strip() == '':
                    continue
                fid_outfile.write(line)
            if line_idx % 500 == 0:
                print 'parsing %d lines in file ' % line_idx


def filtering_line(line_content, stopwords_list):
    '''
    this function spams the noisy symbols, then cut the line to words and remove the stopwords in each line
    :param line_content:
    :return:
    '''
    multi_version = re.compile(ur'-\{.*?(zh-hans|zh-cn):([^;]*?)(;.*?)?\}-')
    # punctuation = re.compile(u"[-~!@#$%^&*()_+`=\[\]\\\{\}\\t\\r\"|;':,./<>?·！@#￥%……&*（）——+【】、；‘：“”，。、《》？「『」』]")
    punctuation = re.compile(u"[\[\]\\\{\}\\t\\r\"|;',<>?·！@#￥%……&*（）——+【】、；‘：“”，。、《》？「『」』]")

    line_content = line_content.replace('_&_', '')
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

def remove_noise_symbol_in_line2(input_filename, fid_outfile, stopwords_list):
    '''
    remove noise symbol in a line, another approach
    read each url line as an anchor
    :param input_filename: a string
    :return: a string
    '''
    line_idx = 0
    print 'dumping file %s ' % input_filename

    question = ''
    subquestion = ''
    url = ''
    # content_list = []
    question_idx = 0
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
                # question = filtering_line(question, stopwords_list)

                answer = qa_content[-2].strip('\n').strip('\t')
                # answer = filtering_line(answer, stopwords_list)

                # add (question, answer, url) to the list
                # now add a tuble to the list
                # qa_tuble = (question, answer, url)
                # content_list.append(qa_tuble)

                question_idx = question_idx + 1
                if question_idx % 500 == 0:
                    print 'get %d-th question %s' % (question_idx, question)

                # write the question-answer pair to file
                fid_outfile.write('%s\n' % question)
                fid_outfile.write('%s\n' % answer)

                # reset qa_content as the new url
                qa_content = [qa_content[0]]

        # last qa_pair
        url = qa_content[0].strip('\n').strip('\t')

        question = qa_content[1].strip('\n').strip('\t')
        # question = filtering_line(question, stopwords_list)

        answer = qa_content[-1].strip('\n').strip('\t')
        # answer = filtering_line(answer, stopwords_list)

        # add (url, question, answer) to the list
        # now add a tuble to the list
        qa_tuble = (question, answer, url)
        # content_list.append(qa_tuble)

        question_idx = question_idx + 1
        print 'get last %d-th question %s' % (question_idx, question)

        # write the last question-answer pair to file
        fid_outfile.write('%s\n' % question)
        fid_outfile.write('%s\n' % answer)

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


if __name__ == '__main__':
    qa_corpus_dir = '/media/xuxing/windisk/workspace-xing/qa-system/qa_corpus'
    out_file = 'qa_jiazhangjiaoyu_corpus.txt'

    fid_outfile = open(os.path.join(qa_corpus_dir, out_file), 'w')


    '''
    # get files in a list
    corpus_files = os.listdir(DIR_XIAOSHENGCHU)
    for cfile in corpus_files:
        inputfile = os.path.join(DIR_XIAOSHENGCHU, cfile)
        remove_noise_symbol_in_line(inputfile, fid_outfile)
    '''

    # use stopword list
    # use jieba to cut the sentence in each line with stopwords
    stopwords_file = 'stopwords_gaokao.txt'
    stopwords_dir = '/media/xuxing/windisk/workspace-xing/qa-system/stopwords_cn'
    stopwords_list = load_stopwords_file(stopwords_dir, stopwords_file)

    # get files in a list
    corpus_files = os.listdir(DIR_JIAZHANGJIAOYU)
    for cfile in corpus_files:
        inputfile = os.path.join(DIR_JIAZHANGJIAOYU, cfile)
        remove_noise_symbol_in_line2(inputfile, fid_outfile, stopwords_list)


    fid_outfile.close()

    print 'Done'

