#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys
import multiprocessing
import gensim
import io
import jieba
import re

reload(sys)
sys.setdefaultencoding('utf-8')


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

def word2vec_train(input_file, output_file):
    print 'training word2vect for file %s' % input_file
    sentences = gensim.models.word2vec.LineSentence(input_file)
    model = gensim.models.Word2Vec(sentences, size=300, min_count=10, sg=0, \
                                   workers=multiprocessing.cpu_count())
    model.save(output_file)
    # model.save_word2vec_format(output_file + '.vector', binary=True)
    print 'finish training w2v model for %s, save as %s' % (input_file, output_file)

def word2vec_train_increamental(input_file, output_file, trained_model):

    # new_sentences = gensim.models.word2vec.LineSentence(input_file)
    new_sentences = []
    idx = 0
    with open(input_file, 'r') as fid:
        for item in fid:
            new_sentences.append(item.decode('utf-8'))
            idx = idx + 1
            if idx % 1000 == 0:
                print '%d' % idx

    print 'now train word2vec based on wiki model ...'
    trained_model.build_vocab(new_sentences, update=True)
    # trained_model.train(new_sentences, total_examples=idx, epochs=trained_model.iter)
    trained_model.train(new_sentences, total_examples=trained_model.corpus_count, epochs=trained_model.iter)

    print 'training incremental word2vect for file %s' % input_file

    trained_model.save(output_file)
    # model.save_word2vec_format(output_file + '.vector', binary=True)
    print 'finish training incremental w2v model for %s, save as %s' % (input_file, output_file)


def combine_multiple_corpus_file(root_dir, dir_corpus, out_file):
    '''
    combine multiple corpus file in the directory to a corpus file
    :param root_dir
    :param dir_corpus:
    :param out_file
    :return:
    '''
    corpus_files = os.listdir(os.path.join(root_dir, dir_corpus))
    with open(out_file, 'w') as ins:
        for cfile in corpus_files:
            print 'combining file %s in dir %s' % (cfile, dir_corpus)
            with open(os.path.join(root_dir, dir_corpus, cfile)) as cins:
                for line_content in cins:
                    ins.write(line_content)
    print 'finished cominbing all corpus file to %s' % out_file

def fenci_words(input_file, output_file, stopwords_list=None):
    count = 0
    with io.open(output_file, mode='w', encoding='utf-8') as outfile:
        with io.open(input_file, mode='r', encoding='utf-8') as infile:
            for line in infile:
                line = line.strip()
                if len(line) < 1:  # empty line
                    continue

                words_list = []
                # if stopwords_list is None:
                #     for word in jieba.cut(line):
                #         words_list.append(word)
                #         # outfile.write(word + ' ')
                # else:
                #     for word in jieba.cut(line):
                #         if word not in stopwords_list:
                #             words_list.append(word)
                #             # outfile.write(word + ' ')

                words_list = filtering_line_re(line, stopwords_list)

                outfile.write(u' '.join(words_list) + '\n')

                count = count + 1
                if count % 500 == 0:
                    print 'cut %d-th line in file %s' % (count, input_file)

def filtering_line_re(line_content, stopwords_list=None):
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


if __name__ == '__main__':
    # if len(sys.argv) < 3:
    #     print "Usage: python script.py infile outfile"
    #     sys.exit()
    # input_file, output_file = sys.argv[1], sys.argv[2]
    cwdir = os.getcwd()
    dir_corpus = 'qa_corpus'
    dir_tmp = 'tempfile'

    if not os.path.exists(os.path.join(cwdir, dir_tmp)):
        os.mkdir(os.path.join(cwdir, dir_tmp))

    # combine to get an entire corpus file
    print 'combine to get an entire corpus file'
    comb_corpus_file = os.path.join(cwdir, dir_tmp, 'comb_corpus_qa')
    if not os.path.exists(os.path.join(cwdir, dir_tmp, comb_corpus_file)):
        combine_multiple_corpus_file(cwdir, dir_corpus, comb_corpus_file)

    # use jieba to cut the sentence in each line with stopwords
    stopwords_file = 'stopwords_education.txt'
    stopwords_dir = '/media/xuxing/windisk/workspace-xing/qa-system/stopwords_cn'
    stopwords_list = load_stopwords_file(stopwords_dir, stopwords_file)

    # fenci
    print 'fenci'
    fenci_corpus_file = os.path.join(cwdir, dir_tmp,  'fenci_corpus_qa')
    if not os.path.exists(os.path.join(cwdir, dir_tmp, fenci_corpus_file)):
        fenci_words(comb_corpus_file, fenci_corpus_file, stopwords_list)


    # out_w2v_qa = os.path.join(cwdir, dir_tmp, 'out_w2v_qa')
    # word2vec_train(fenci_corpus_file, out_w2v_qa)

    # train incremental model based on wiki
    # load wiki model
    wiki_model_file = '/media/xuxing/windisk/workspace-xing/qa-system/zhiwiki_extracted/wiki_w2v.model'
    wiki_model = gensim.models.Word2Vec.load(wiki_model_file)

    out_w2v_qa = os.path.join(cwdir, dir_tmp, 'out_w2v_qa_incremental.model')
    word2vec_train_increamental(fenci_corpus_file, out_w2v_qa, wiki_model)

